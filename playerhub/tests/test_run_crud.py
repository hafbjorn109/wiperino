import pytest
from playerhub.models import Run
from .factories import UserFactory, RunFactory


@pytest.mark.django_db
def test_add_run(client):
    runs_count = Run.objects.count()
    user = UserFactory()
    client.force_authenticate(user=user)
    data = {
        'name': 'Test Run',
        'game': 'Test Game',
        'mode': 'SPEEDRUN',
        'is_finished': False,
        'session_code': '223'
    }
    response = client.post('/runs/', data, format='json')
    assert response.status_code == 201, 'Run was not created'
    assert Run.objects.count() == runs_count + 1, 'Run was not created'


@pytest.mark.django_db
def test_not_logged_in_user_add_run(client):
    data = {
        'name': 'Test Run',
        'game': 'Test Game',
        'mode': 'SPEEDRUN',
        'is_finished': False,
        'session_code': '223'
    }
    response = client.post('/runs/', data, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_get_runs(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    RunFactory.create_batch(5, user=user)
    RunFactory.create_batch(4)
    response = client.get('/runs/', {}, format='json')
    assert response.status_code == 200, 'Runs were not retrieved'
    assert len(response.data) == 5, 'User should see only his runs'
    for run in response.data:
        assert run['user'] == user.username, 'User should see only his runs'


@pytest.mark.django_db
def test_not_logged_in_get_runs(client):
    user = UserFactory()
    RunFactory.create_batch(5, user=user)
    RunFactory.create_batch(4)
    response = client.get('/runs/', {}, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_change_run(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    change_data = {
        'name': 'New Run Name',
    }
    response = client.patch(f'/runs/{run.id}/', change_data, format='json')
    assert response.status_code == 200, 'Run was not changed'
    assert response.data['name'] == change_data['name'], 'Run was not changed'


@pytest.mark.django_db
def test_change_foreign_user_run(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory()
    change_data = {
        'name': 'New Run Name',
    }
    response = client.patch(f'/runs/{run.id}/', change_data, format='json')
    assert response.status_code == 404, 'User should not be able to change foreign user run'


@pytest.mark.django_db
def test_not_logged_in_change_run(client):
    user = UserFactory()
    run = RunFactory(user=user)
    change_data = {
        'name': 'New Run Name',
    }
    response = client.patch(f'/runs/{run.id}/', change_data, format='json')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_delete_run(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    response = client.delete(f'/runs/{run.id}/')
    assert response.status_code == 204, 'Run was not deleted correctly'


@pytest.mark.django_db
def test_not_logged_in_delete_run(client):
    user = UserFactory()
    run = RunFactory(user=user)
    response = client.delete(f'/runs/{run.id}/')
    assert response.status_code == 403, 'User should be not authenticated'


@pytest.mark.django_db
def test_delete_foreign_user_run(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory()
    response = client.delete(f'/runs/{run.id}/')
    assert response.status_code == 404, 'User should not be able to delete foreign user run'


