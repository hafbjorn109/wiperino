from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import CreateUserSerializer
from users.serializers import CreateUserSerializer


# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
        user.save()