from rest_framework import serializers
from django.contrib.auth.models import User

class CreateUserSerializer(serializers.ModelSerializer):
    """
      Serializer for registering a new user.

      Accepts username, email, and password.
      Ensures password is write-only and creates the user using Django's built-in create_user method.
      """
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
