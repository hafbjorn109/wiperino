import pytest
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_register_user(client):
    """
    Test to ensure that a new user can be registered successfully.

    Expects a 201 Created response and the user to exist in the database.
    """
    data = {
        'username': 'test_user',
        'email': 'test@mail.com',
        'password': 'testpass1234'
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
