import pytest
from .factories import WipeCounterFactory, UserFactory, RunFactory
from playerhub.models import WipeCounter


@pytest.mark.django_db
def test_add_wipecounter(client):
    """
    Test to ensure that an authenticated user can create a wipe counter segment.

    Expects a 201 Created response and one additional wipe counter in the database.
    """
    wipecounters_count = WipeCounter.objects.count()
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    data = {
        'segment_name': 'Test Segment',
        'count': 30,
        'is_finished': False,
    }
    response = client.post(f'/api/runs/{run.id}/wipecounters/', data, format='json')
    assert response.status_code == 201, 'WipeCounter was not created'
    assert WipeCounter.objects.count() == wipecounters_count + 1, 'WipeCounter was not created'


@pytest.mark.django_db
def test_not_logged_in_user_add_wipecounter(client):
    """
    Test to ensure that unauthenticated users cannot create wipe counters.

    Sends a POST request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    run = RunFactory(user=user)
    data = {
        'segment_name': 'Test Segment',
        'count': 30,
        'is_finished': False,
    }
    response = client.post(f'/api/runs/{run.id}/wipecounters/', data, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_add_wipecounter_for_foreign_user(client):
    """
    Test to ensure that a user cannot create a wipe counter for another user's run.

    Sends a POST request for a run not owned by the user.
    Expects a 404 Not Found response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory()
    data = {
        'segment_name': 'Test Segment',
        'count': 30,
        'is_finished': False,
    }
    response = client.post(f'/api/runs/{run.id}/wipecounters/', data, format='json')
    assert response.status_code == 404, 'User should not be able to add foreign user wipecounter'


@pytest.mark.django_db
def test_get_wipecounters(client):
    """
    Test to ensure that a user can retrieve only their own wipe counters.

    Creates 5 wipe counters for the authenticated user's run, 4 for others.
    Sends a GET request and expects only 5 wipe counters in response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    WipeCounterFactory.create_batch(5, run=run)
    WipeCounterFactory.create_batch(4)
    response = client.get(f'/api/runs/{run.id}/wipecounters/', {}, format='json')
    assert response.status_code == 200, 'WipeCounters were not retrieved'
    assert len(response.data) == 5, 'User should see only his wipecounters'
    for wipecounter in response.data:
        assert wipecounter['run'] == run.name, 'User should see only his wipecounters'


@pytest.mark.django_db
def test_get_wipecounters_for_not_logged_in_user(client):
    """
    Test to ensure that unauthenticated users cannot access wipe counters.

    Sends a GET request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    run = RunFactory(user=user)
    WipeCounterFactory.create_batch(5, run=run)
    response = client.get(f'/api/runs/{run.id}/wipecounters/', {}, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_change_wipecounter(client):
    """
    Test to ensure that an authenticated user can update their own wipe counter.

    Expects a 200 OK response and the wipe counter to be updated.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    wipecounter = WipeCounterFactory(run=run)
    change_data = {
        'segment_name': 'New Segment Name',
    }
    response = client.patch(f'/api/runs/{run.id}/wipecounters/{wipecounter.id}/', change_data, format='json')
    assert response.status_code == 200, 'WipeCounter was not changed'
    assert response.data['segment_name'] == change_data['segment_name'], 'WipeCounter was not changed'


@pytest.mark.django_db
def test_change_not_logged_in_wipecounter(client):
    """
    Test to ensure that unauthenticated users cannot update wipe counters.

    Sends a PATCH request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    run = RunFactory(user=user)
    wipecounter = WipeCounterFactory(run=run)
    change_data = {
        'segment_name': 'New Segment Name',
    }
    response = client.patch(f'/api/runs/{run.id}/wipecounters/{wipecounter.id}/', change_data, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_change_foreign_user_wipecounter(client):
    """
    Test to ensure that a user cannot update another user's wipe counter.

    Sends a PATCH request for a wipe counter not owned by the user.
    Expects a 404 Not Found response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory()
    wipecounter = WipeCounterFactory(run=run)
    change_data = {
        'segment_name': 'New Segment Name',
    }
    response = client.patch(f'/api/runs/{run.id}/wipecounters/{wipecounter.id}/', change_data, format='json')
    assert response.status_code == 404, 'User should not be able to change foreign user wipecounter'


@pytest.mark.django_db
def test_delete_wipecounter(client):
    """
    Test to ensure that a user can delete their own wipe counter.

    Expects a 204 No Content response and the wipe counter to be removed.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    wipecounter = WipeCounterFactory(run=run)
    response = client.delete(f'/api/runs/{run.id}/wipecounters/{wipecounter.id}/')
    assert response.status_code == 204, 'WipeCounter was not deleted correctly'


@pytest.mark.django_db
def test_delete_not_logged_in_wipecounter(client):
    """
    Test to ensure that unauthenticated users cannot delete wipe counters.

    Sends a DELETE request without authentication.
    Expects a 403 Forbidden response.
    """
    user = UserFactory()
    run = RunFactory(user=user)
    wipecounter = WipeCounterFactory(run=run)
    response = client.delete(f'/api/runs/{run.id}/wipecounters/{wipecounter.id}/')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_delete_foreign_user_wipecounter(client):
    """
    Test to ensure that a user cannot delete another user's wipe counter.

    Sends a DELETE request for a wipe counter not owned by the user.
    Expects a 404 Not Found response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory()
    wipecounter = WipeCounterFactory(run=run)
    response = client.delete(f'/api/runs/{run.id}/wipecounters/{wipecounter.id}/')
    assert response.status_code == 404, 'User should not be able to delete foreign user wipecounter'
