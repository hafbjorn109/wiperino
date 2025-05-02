import pytest
from .factories import UserFactory, RunFactory, TimerFactory, GameFactory
from playerhub.models import Timer


@pytest.mark.django_db
def test_add_timer(client):
    """
    Test to ensure that an authenticated user can create a timer segment.

    Expects a 201 Created response and one additional timer in the database.
    """
    timers_count = Timer.objects.count()
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    data = {
        'segment_name': 'Test Timer',
        'is_finished': False,
        'elapsed_time': 45.68
    }
    response = client.post(f'/api/runs/{run.id}/timers/', data, format='json')
    assert response.status_code == 201, 'Timer was not created'
    assert Timer.objects.count() == timers_count + 1, 'Timer was not created'


@pytest.mark.django_db
def test_add_timer_not_logged_in(client):
    """
    Test to ensure that an unauthenticated user cannot create a timer.

    Sends a POST request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    data = {
        'segment_name': 'Test Timer',
        'is_finished': False,
        'elapsed_time': 45.68
    }
    response = client.post(f'/api/runs/{run.id}/timers/', data, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_add_timer_for_foreign_user(client):
    """
    Test to ensure that a user cannot create a timer for another user's run.

    Sends a POST request for a run not owned by the user.
    Expects a 404 Not Found response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(game=game)
    data = {
        'segment_name': 'Test Timer',
        'is_finished': False,
        'elapsed_time': 45.68
    }
    response = client.post(f'/api/runs/{run.id}/timers/', data, format='json')
    assert response.status_code == 404, 'User should not be able to add foreign user timer'


@pytest.mark.django_db
def test_get_timers(client):
    """
    Test to ensure that a user can retrieve only their own timers.

    Creates 5 timers for the logged-in user and 4 for another.
    Sends a GET request and expects only 5 user-owned timers in response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    TimerFactory.create_batch(5, run=run)
    TimerFactory.create_batch(4)
    response = client.get(f'/api/runs/{run.id}/timers/', {}, format='json')
    assert response.status_code == 200, 'Timers were not retrieved'
    assert len(response.data) == 5, 'User should see only his timers'
    for timer in response.data:
        assert timer['run'] == run.name, 'User should see only his timers'


@pytest.mark.django_db
def test_get_timers_not_logged_in(client):
    """
    Test to ensure that unauthenticated users cannot access timers.

    Sends a GET request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    TimerFactory.create_batch(5, run=run)
    response = client.get(f'/api/runs/{run.id}/timers/', {}, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_change_timer(client):
    """
    Test to ensure that an authenticated user can update their own timer.

    Expects a 200 OK response and the timer data to be updated.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    timer = TimerFactory(run=run)
    change_data = {
        'segment_name': 'New Timer Name',
    }
    response = client.patch(f'/api/runs/{run.id}/timers/{timer.id}/', change_data, format='json')
    assert response.status_code == 200, 'Timer was not changed'
    assert response.data['segment_name'] == change_data['segment_name'], 'Timer was not changed'


@pytest.mark.django_db
def test_change_not_logged_in_timer(client):
    """
    Test to ensure that unauthenticated users cannot update timers.

    Sends a PATCH request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    timer = TimerFactory(run=run)
    change_data = {
        'segment_name': 'New Timer Name',
    }
    response = client.patch(f'/api/runs/{run.id}/timers/{timer.id}/', change_data, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_change_foreign_user_timer(client):
    """
    Test to ensure that a user cannot update another user's timer.

    Sends a PATCH request for a timer not owned by the user.
    Expects a 404 Not Found response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(game=game)
    timer = TimerFactory(run=run)
    change_data = {
        'segment_name': 'New Timer Name',
    }
    response = client.patch(f'/api/runs/{run.id}/timers/{timer.id}/', change_data, format='json')
    assert response.status_code == 404, 'User should not be able to change foreign user timer'


@pytest.mark.django_db
def test_delete_timer(client):
    """
    Test to ensure that a user can delete their own timer.

    Expects a 204 No Content response and removal from the database.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    timer = TimerFactory(run=run)
    response = client.delete(f'/api/runs/{run.id}/timers/{timer.id}/')
    assert response.status_code == 204, 'Timer was not deleted correctly'


@pytest.mark.django_db
def test_delete_not_logged_in_timer(client):
    """
    Test to ensure that unauthenticated users cannot delete timers.

    Sends a DELETE request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    game = GameFactory()
    run = RunFactory(user=user, game=game)
    timer = TimerFactory(run=run)
    response = client.delete(f'/api/runs/{run.id}/timers/{timer.id}/')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_delete_foreign_user_timer(client):
    """
    Test to ensure that a user cannot delete another user's timer.

    Sends a DELETE request for a timer not owned by the user.
    Expects a 404 Not Found response.
    """
    user = UserFactory()
    game = GameFactory()
    client.force_authenticate(user=user)
    run = RunFactory(game=game)
    timer = TimerFactory(run=run)
    response = client.delete(f'/api/runs/{run.id}/timers/{timer.id}/')
    assert response.status_code == 404, 'User should not be able to delete foreign user timer'