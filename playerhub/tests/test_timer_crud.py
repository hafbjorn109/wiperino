import pytest
from .factories import UserFactory, RunFactory, TimerFactory
from playerhub.models import Timer

@pytest.mark.django_db
def test_add_timer(client):
    timers_count = Timer.objects.count()
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    data = {
        'segment_name': 'Test Timer',
        'is_finished': False,
        'elapsed_time': 45.68
    }
    response = client.post(f'/runs/{run.id}/timers/', data, format='json')
    assert response.status_code == 201, 'Timer was not created'
    assert Timer.objects.count() == timers_count + 1, 'Timer was not created'

@pytest.mark.django_db
def test_add_timer_not_logged_in(client):
    user = UserFactory()
    run = RunFactory(user=user)
    data = {
        'segment_name': 'Test Timer',
        'is_finished': False,
        'elapsed_time': 45.68
    }
    response = client.post(f'/runs/{run.id}/timers/', data, format='json')
    assert response.status_code == 403, 'User should be not authenticated'

@pytest.mark.django_db
def test_add_timer_for_foreign_user(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory()
    data = {
        'segment_name': 'Test Timer',
        'is_finished': False,
        'elapsed_time': 45.68
    }
    response = client.post(f'/runs/{run.id}/timers/', data, format='json')
    assert response.status_code == 404, 'User should not be able to add foreign user timer'

@pytest.mark.django_db
def test_get_timers(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    TimerFactory.create_batch(5, run=run)
    TimerFactory.create_batch(4)
    response = client.get(f'/runs/{run.id}/timers/', {}, format='json')
    assert response.status_code == 200, 'Timers were not retrieved'
    assert len(response.data) == 5, 'User should see only his timers'
    for timer in response.data:
        assert timer['run'] == run.name, 'User should see only his timers'

@pytest.mark.django_db
def test_get_timers_not_logged_in(client):
    user = UserFactory()
    run = RunFactory(user=user)
    TimerFactory.create_batch(5, run=run)
    response = client.get(f'/runs/{run.id}/timers/', {}, format='json')
    assert response.status_code == 403, 'User should be not authenticated'

@pytest.mark.django_db
def test_change_timer(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    timer = TimerFactory(run=run)
    change_data = {
        'segment_name': 'New Timer Name',
    }
    response = client.patch(f'/runs/{run.id}/timers/{timer.id}/', change_data, format='json')
    assert response.status_code == 200, 'Timer was not changed'
    assert response.data['segment_name'] == change_data['segment_name'], 'Timer was not changed'

@pytest.mark.django_db
def test_change_not_logged_in_timer(client):
    user = UserFactory()
    run = RunFactory(user=user)
    timer = TimerFactory(run=run)
    change_data = {
        'segment_name': 'New Timer Name',
    }
    response = client.patch(f'/runs/{run.id}/timers/{timer.id}/', change_data, format='json')
    assert response.status_code == 403, 'User should be not authenticated'

@pytest.mark.django_db
def test_change_foreign_user_timer(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory()
    timer = TimerFactory(run=run)
    change_data = {
        'segment_name': 'New Timer Name',
    }
    response = client.patch(f'/runs/{run.id}/timers/{timer.id}/', change_data, format='json')
    assert response.status_code == 404, 'User should not be able to change foreign user timer'

@pytest.mark.django_db
def test_delete_timer(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    timer = TimerFactory(run=run)
    response = client.delete(f'/runs/{run.id}/timers/{timer.id}/')
    assert response.status_code == 204, 'Timer was not deleted correctly'

@pytest.mark.django_db
def test_delete_not_logged_in_timer(client):
    user = UserFactory()
    run = RunFactory(user=user)
    timer = TimerFactory(run=run)
    response = client.delete(f'/runs/{run.id}/timers/{timer.id}/')
    assert response.status_code == 403, 'User should be not authenticated'

@pytest.mark.django_db
def test_delete_foreign_user_timer(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory()
    timer = TimerFactory(run=run)
    response = client.delete(f'/runs/{run.id}/timers/{timer.id}/')
    assert response.status_code == 404, 'User should not be able to delete foreign user timer'