from django.urls import path
from knox import views as knox_views
from .views import RegisterView, LoginView, UserDetailView, ChangePasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('profile/', UserDetailView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
] 