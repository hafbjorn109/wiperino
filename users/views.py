from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import CreateUserSerializer


# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
