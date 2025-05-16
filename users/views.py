from rest_framework import generics
from .serializers import CreateUserSerializer
from django.contrib.auth.views import  TemplateView
from rest_framework.permissions import AllowAny


class RegisterView(generics.CreateAPIView):
    """
    API view for registering a new user.

    Accepts POST requests with username, email, and password.
    Uses CreateUserSerializer to validate and create the user instance.
    """
    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer


class RegisterPageView(TemplateView):
    """
    View to render registration form.
    """
    template_name = 'users/register_form.html'


class LoginPageView(TemplateView):
    """
    View to render login form.
    """
    template_name = 'users/login_form.html'