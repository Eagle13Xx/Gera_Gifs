from django.urls import path
from .views import UserRegistrationView, LoginView, ProfileView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'), # DRF's built-in login
    path('profile/', ProfileView.as_view(), name='profile'),
]