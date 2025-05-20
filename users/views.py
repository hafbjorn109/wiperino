from rest_framework import generics
from .serializers import (CreateUserSerializer, PasswordResetRequestSerializer,
                          PasswordResetConfirmSerializer)
from django.contrib.auth.views import TemplateView
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail


class RegisterView(generics.CreateAPIView):
    """
    API view for registering a new user.

    Accepts POST requests with username, email, and password.
    Uses CreateUserSerializer to validate and create the user instance.
    """
    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer


class PasswordResetRequestView(GenericAPIView):
    """
    View to handle generation of password reset links.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"http://localhost:8000/reset-password/{uid}/{token}/"

            send_mail(
                subject='Reset your password',
                message=f'Click the link below to reset your password: {reset_link}',
                from_email='wiperino@mail.com',
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response({
            'message': 'If this email is registered, you will receive a reset link in your email.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(GenericAPIView):
    """
    View to handle password reset requests.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Password reset successful.'},
            status=status.HTTP_200_OK
        )


class RegisterPageView(TemplateView):
    """
    View to render a registration form.
    """
    template_name = 'users/register_form.html'


class LoginPageView(TemplateView):
    """
    View to render a login form.
    """
    template_name = 'users/login_form.html'


class ResetPasswordPageView(TemplateView):
    """
    View to render a reset password form.
    """
    template_name = 'users/reset_password.html'


class ForgotPasswordView(TemplateView):
    """
    View to render a forgot password form.
    """
    template_name = 'users/forgot_password.html'
