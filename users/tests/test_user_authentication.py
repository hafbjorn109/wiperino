import pytest
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator


@pytest.mark.django_db
def test_register_user(client):
    """
    Test to ensure that a new user can be registered successfully.

    Expects a 201 Created response and the user to exist in the database.
    """
    data = {
        'username': 'test_user',
        'email': 'test@mail.com',
        'password': 'testpass1234',
        'password2': 'testpass1234'
    }
    response = client.post('/api/register/', data, format='json')
    assert response.status_code == 201, 'User was not created'
    assert User.objects.filter(username='test_user').exists(), 'User was not created'


@pytest.mark.django_db
def test_login_user(client):
    """
    Test to ensure that an existing user can log in and receive JWT tokens.

    Expects a 200 OK response containing access and refresh tokens.
    """
    User.objects.create_user(username='testuser', password='testpass1234')
    data = {
        'username': 'testuser',
        'password': 'testpass1234'
    }
    response = client.post('/api/login/', data, format='json')
    assert response.status_code == 200, 'User was not logged in'
    assert 'access' in response.data, 'User was not logged in'
    assert 'refresh' in response.data, 'User was not logged in'


@pytest.mark.django_db
def test_login_invalid_data(client):
    """
    Test to ensure that login fails with invalid credentials.

    Expects a 401 Unauthorized response with no tokens in the response data.
    """
    data = {
        'username': 'testuser',
        'password': 'testpass1234'
    }
    response = client.post('/api/login/', data, format='json')
    assert response.status_code == 401, 'User was not logged in'
    assert 'access' not in response.data, 'User was not logged in'


@pytest.mark.django_db
def test_refresh_token(client):
    """
    Test to ensure that a valid refresh token returns a new access token.

    Expects a 200 OK response and a new access token in the response.
    """
    user = User.objects.create_user(username='testuser', password='testpass1234')
    refresh = RefreshToken.for_user(user)
    data = {
        'refresh': str(refresh)
    }
    response = client.post('/api/token/refresh/', data, format='json')
    assert response.status_code == 200, 'Token was not refreshed'
    assert 'access' in response.data, 'Token was not refreshed'


@pytest.mark.django_db
def test_password_reset_request(client, mailoutbox):
    """
    Test that password reset email is sent if the user exists.
    Expects a 200 OK regardless of whether the user exists or not.
    """
    User.objects.create_user(username='testuser', email='test@mail.com', password='secretpass1234')
    data = {'email': 'test@mail.com'}
    response = client.post('/api/password-reset-request/', data, format='json')

    assert response.status_code == 200, 'Password reset email was not sent'
    assert len(mailoutbox) == 1, 'Password reset email was not sent'
    assert 'Reset your password' in mailoutbox[0].subject, 'Wrong email subject'


@pytest.mark.django_db
def test_password_reset_request_unknown_email(client, mailoutbox):
    """
    Test that no error is thrown if the email does not exist.
    """
    data = {'email': 'unknown@mail.com'}
    response = client.post('/api/password-reset-request/', data, format='json')

    assert response.status_code == 200, 'Password reset email was not sent'
    assert len(mailoutbox) == 0, 'Password reset email was sent for unknown email'


@pytest.mark.django_db
def test_password_reset_confirm(client):
    """
    Test that a user can reset their password with a valid token and uid.
    """
    user = User.objects.create_user(
        username='resetuser', email='reset@mail.com', password='secretpass1234')
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)

    data = {
        'uid': uid,
        'token': token,
        'password': 'newpass1234',
        'password2': 'newpass1234'
    }
    response = client.post('/api/password-reset-confirm/', data, format='json')

    assert response.status_code == 200, 'Password was not reset'
    user.refresh_from_db()
    assert user.check_password('newpass1234') is True, 'Password was not reset'


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(client):
    user = User.objects.create_user(username='invalidreset',
                                    email='badtoken@mail.com',
                                    password='secretpass1234')
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = 'bad-token'

    data = {
        'uid': uid,
        'token': token,
        'password': 'newpass1234',
        'password2': 'newpass1234'
    }

    response = client.post('/api/password-reset-confirm/', data, format='json')

    assert response.status_code == 400, \
        'Password was reset with invalid token'
    assert 'Invalid or expired token' in str(response.data), \
        'Password was reset with invalid token'
