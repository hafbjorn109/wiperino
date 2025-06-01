import pytest
from playerhub.models import Run
from .factories import UserFactory, RunFactory, GameFactory, WipeCounterFactory, TimerFactory


@pytest.mark.django_db
def test_add_run(client):
    """
    Test to ensure that an authenticated user can create a run.

    Expects a 201 Created response and one new run in the database.
    """
    runs_count = Run.objects.count()
    user = UserFactory()
    game = GameFactory()
    client.force_authenticate(user=user)
    data = {
        'name': 'Test Run',
        'game': game.id,
        'mode': 'SPEEDRUN',
        'is_finished': False,
    }
    response = client.post('/api/runs/', data, format='json')
    assert response.status_code == 201, 'Run was not created'
    assert Run.objects.count() == runs_count + 1, 'Run was not created'


@pytest.mark.django_db
def test_not_logged_in_user_add_run(client):
    """
    Test to ensure that unauthenticated users cannot create runs.

    Sends a POST request without authentication.
    Expects a 403 Forbidden response.
    """
    game = GameFactory()
    data = {
        'name': 'Test Run',
        'game': game.id,
        'mode': 'SPEEDRUN',
        'is_finished': False,
    }
    response = client.post('/api/runs/', data, format='json')
    assert response.status_code == 401, 'User should be not authenticated'


@pytest.mark.django_db
def test_get_runs(client):
    """
    Test to ensure that an authenticated user only receives their own runs.

    Creates runs for the authenticated user and another user.
    Sends a GET request and verifies only the user's own runs are returned.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    RunFactory.create_batch(5, user=user, game=game)
    RunFactory.create_batch(4, game=game)
    response = client.get('/api/runs/', {}, format='json')
    assert response.status_code == 200, 'Runs were not retrieved'
    assert len(response.data) == 5, 'User should see only his runs'
    for run in response.data:
        assert run['user'] == user.username, 'User should see only his runs'


@pytest.mark.django_db
def test_not_logged_in_get_runs(client):
    """
    Test to ensure that unauthenticated users cannot access the run list.

    Sends a GET request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    game = GameFactory()
    RunFactory.create_batch(5, user=user, game=game)
    RunFactory.create_batch(4, game=game)
    response = client.get('/api/runs/', {}, format='json')
    assert response.status_code == 401, 'User should be not authenticated'


@pytest.mark.django_db
def test_change_run(client):
    """
    Test to ensure that an authenticated user can update their own run.

    Expects a 200 OK response and the run to be updated.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    change_data = {
        'name': 'New Run Name',
    }
    response = client.patch(f'/api/runs/{run.id}/', change_data, format='json')
    assert response.status_code == 200, 'Run was not changed'
    assert response.data['name'] == change_data['name'], 'Run was not changed'


@pytest.mark.django_db
def test_change_foreign_user_run(client):
    """
    Test to ensure that users cannot update runs they do not own.

    Sends a PATCH request on a run belonging to another user.
    Expects a 404 Not Found response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(game=game)
    change_data = {
        'name': 'New Run Name',
    }
    response = client.patch(f'/api/runs/{run.id}/', change_data, format='json')
    assert response.status_code == 404, 'User should not be able to change foreign user run'


@pytest.mark.django_db
def test_not_logged_in_change_run(client):
    """
    Test to ensure that unauthenticated users cannot update runs.

    Sends a PATCH request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    change_data = {
        'name': 'New Run Name',
    }
    response = client.patch(f'/api/runs/{run.id}/', change_data, format='json')
    assert response.status_code == 401, 'User should be not authenticated'


@pytest.mark.django_db
def test_delete_run(client):
    """
    Test to ensure that an authenticated user can delete their own run.

    Expects a 204 No Content response and the run is removed from the database.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    response = client.delete(f'/api/runs/{run.id}/')
    assert response.status_code == 204, 'Run was not deleted correctly'


@pytest.mark.django_db
def test_not_logged_in_delete_run(client):
    """
    Test to ensure that unauthenticated users cannot delete runs.

    Sends a DELETE request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    response = client.delete(f'/api/runs/{run.id}/')
    assert response.status_code == 401, 'User should be not authenticated'


@pytest.mark.django_db
def test_delete_foreign_user_run(client):
    """
    Test to ensure that users cannot delete runs they do not own.

    Sends a DELETE request on a run belonging to another user.
    Expects a 404 Not Found response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(game=game)
    response = client.delete(f'/api/runs/{run.id}/')
    assert response.status_code == 404, 'User should not be able to delete foreign user run'


@pytest.mark.django_db
def test_export_wipecounter_excel(client):
    """
    Test exporting a WIPECOUNTER run to Excel by its owner.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game, mode='WIPECOUNTER')
    WipeCounterFactory.create_batch(5, run=run)
    WipeCounterFactory.create_batch(5, run=run)

    response = client.get(f'/api/runs/{run.id}/export/', {}, format='json')

    assert response.status_code == 200, 'Run was not exported'
    assert (response['Content-Type']
            == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    assert f'wipes_run_{run.id}.xlsx' in response['Content-Disposition']


@pytest.mark.django_db
def test_export_speedrun_excel(client):
    """
    Test exporting a SPEEDRUN to Excel by its owner.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game, mode='SPEEDRUN')
    TimerFactory.create_batch(5, run=run)

    response = client.get(f'/api/runs/{run.id}/export/', {}, format='json')

    assert response.status_code == 200, 'Run was not exported'
    assert (response['Content-Type']
            == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    assert f'speedrun_run_{run.id}.xlsx' in response['Content-Disposition']


@pytest.mark.django_db
def test_export_foreign_run(client):
    """
    Test exporting a foreign run by another user.
    Expected: 403 Forbidden
    """
    run = RunFactory()
    user = UserFactory()
    client.force_authenticate(user=user)
    response = client.get(f'/api/runs/{run.id}/export/', {}, format='json')
    assert response.status_code == 403, 'User should not be able to export foreign run'


@pytest.mark.django_db
def test_export_invalid_mode(client):
    """
    Test exporting a run with an invalid mode.
    Expected: 400 Bad Request
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game, mode='INVALID')
    response = client.get(f'/api/runs/{run.id}/export/', {}, format='json')
    assert response.status_code == 400, 'Invalid mode should return 400'
    assert 'Invalid run mode' in response.json()['detail']
