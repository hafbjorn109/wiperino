from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import CreateUserSerializer


# Create your views here.

class RegisterView(generics.CreateAPIView):
    """
    API view for registering a new user.

    Accepts POST requests with username, email, and password.
    Uses CreateUserSerializer to validate and create the user instance.
    """
    serializer_class = CreateUserSerializer
