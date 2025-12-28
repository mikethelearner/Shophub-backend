from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import login, authenticate
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer
from .models import User


class TokenAuthentication(BaseAuthentication):
    """Simple token authentication for MongoDB compatibility"""
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Token '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            user = User.objects.get(auth_token=token)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid token')


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Generate token for the new user
            token = user.generate_token()
            
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Registration error: {error_detail}")
            return Response({
                "error": str(e),
                "detail": error_detail
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate new token on login
        token = user.generate_token()
        
        return Response({
            "user": UserSerializer(user).data,
            "token": token
        })


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        # Clear the user's token
        User.objects.filter(email=request.user.email).update(auth_token=None)
        return Response({"message": "Successfully logged out"})


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "Error retrieving profile", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            
            # Manually update using queryset to avoid ObjectId/int mismatch in instance.save()
            User.objects.filter(email=instance.email).update(**serializer.validated_data)
            
            # Update instance in memory to return correct response
            for attr, value in serializer.validated_data.items():
                setattr(instance, attr, value)
                
            return Response(UserSerializer(instance).data)
        except Exception as e:
            return Response(
                {"error": "Error updating profile", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.data.get("new_password"))
            # Use update to avoid save() crash
            User.objects.filter(email=user.email).update(password=user.password)
            
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)