from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
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
