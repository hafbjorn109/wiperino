import pytest
from playerhub.models import Game
from .factories import GameFactory, UserFactory


@pytest.mark.django_db
def test_add_game(client):
    games_count = Game.objects.count()
    user = UserFactory()
    client.force_authenticate(user=user)
    data = {
        'name': 'Test Game',
    }
    response = client.post('/api/games/', data, format='json')
    assert response.status_code == 201, 'Game was not created'
    assert Game.objects.count() == games_count + 1, 'Game was not created'


@pytest.mark.django_db
def test_add_game_not_logged_in(client):
    data = {
        'name': 'Test Game',
    }
    response = client.post('/api/games/', data, format='json')
    assert response.status_code == 401, 'User should be not authenticated'


@pytest.mark.django_db
def test_get_games(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    GameFactory.create_batch(5)
    response = client.get('/api/games/', {}, format='json')
    assert response.status_code == 200, 'Games were not retrieved'
    assert len(response.data) == 5, 'User should see all of the games'


@pytest.mark.django_db
def test_get_games_not_logged_in(client):
    GameFactory.create_batch(5)
    response = client.get('/api/games/', {}, format='json')
    assert response.status_code == 401, 'User should be not authenticated'


@pytest.mark.django_db
def test_get_game_by_id(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    response = client.get(f'/api/games/{game.id}/', {}, format='json')
    assert response.status_code == 200, 'Game was not retrieved'
    assert response.data['name'] == game.name, 'Game was not retrieved'


@pytest.mark.django_db
def test_get_game_by_id_not_logged_in(client):
    game = GameFactory()
    response = client.get(f'/api/games/{game.id}/', {}, format='json')
    assert response.status_code == 401, 'User should be not authenticated'


@pytest.mark.django_db
def test_change_game(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    change_data = {
        'name': 'New Game Name',
    }
    response = client.patch(f'/api/games/{game.id}/', change_data, format='json')
    assert response.status_code == 200, 'Game was not changed'
    assert response.data['name'] == change_data['name'], 'Game was not changed'


@pytest.mark.django_db
def test_change_game_not_logged_in(client):
    game = GameFactory()
    change_data = {
        'name': 'New Game Name',
    }
    response = client.patch(f'/api/games/{game.id}/', change_data, format='json')
    assert response.status_code == 401, 'User should be not authenticated'


@pytest.mark.django_db
def test_delete_game(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    response = client.delete(f'/api/games/{game.id}/', format='json')
    assert response.status_code == 204, 'Game was not deleted correctly'


@pytest.mark.django_db
def test_delete_game_not_logged_in(client):
    game = GameFactory()
    response = client.delete(f'/api/games/{game.id}/', format='json')
    assert response.status_code == 401, 'User should be not authenticated'