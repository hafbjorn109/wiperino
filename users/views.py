from rest_framework import generics
from .serializers import CreateUserSerializer
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView


# Create your views here.

class RegisterView(generics.CreateAPIView):
    """
    API view for registering a new user.

    Accepts POST requests with username, email, and password.
    Uses CreateUserSerializer to validate and create the user instance.
    """
    serializer_class = CreateUserSerializer

class RegisterPageView(FormView):
    """
    View to render and handle user registration form.
    """
    template_name = 'users/register_form.html'
    form_class = RegisterForm
    success_url = reverse_lazy('runs')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class LoginPageView(LoginView):
    """
    View to render and handle user login form.
    On successful authentication, redirects to the user's run list.
    """
    template_name = 'users/login_form.html'
    fields = '__all__'
    redirect_authenticated_user = True
    success_url = reverse_lazy('runs')

class LogoutPageView(LogoutView):
    next_page = reverse_lazy('login')