from rest_framework import serializers
from django.contrib.auth.models import User

class CreateUserSerializer(serializers.ModelSerializer):
    """
      Serializer for registering a new user.

      Accepts username, email, and password.
      Ensures password is write-only and creates the user using Django's built-in create_user method.
      """
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)
