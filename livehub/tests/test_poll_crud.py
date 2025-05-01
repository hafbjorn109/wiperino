import pytest
from .factories import PollFactory
from playerhub.tests.factories import UserFactory, RunFactory
from livehub.models import Poll


@pytest.mark.django_db
def test_add_poll_moderator(client):
    polls_count = Poll.objects.count()
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    data = {
        'question': 'Test Question',
        'published': True
    }
    response = client.post(f'/api/polls/mod/{run.moderator_session_code}/',
                           data, format='json')
    assert response.status_code == 201, 'Poll was not created'
    assert Poll.objects.count() == polls_count + 1, 'Poll was not created'


@pytest.mark.django_db
def test_get_polls_moderator(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    PollFactory.create_batch(5, run=run)
    PollFactory.create_batch(4)
    response = client.get(
        f'/api/polls/mod/{run.moderator_session_code}/',
        {}, format='json')
    assert response.status_code == 200, 'Polls were not retrieved'
    assert len(response.data) == 5, \
        'User should see only polls from particular Run'
    for poll in response.data:
        assert poll['run'] == run.name, 'User should see only his polls'


@pytest.mark.django_db
def test_get_polls_viewers(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    PollFactory.create_batch(5, run=run)
    PollFactory.create_batch(4)
    response = client.get(f'/api/polls/{run.session_code}/', {}, format='json')
    assert response.status_code == 200, 'Polls were not retrieved'
    assert len(response.data) == 5, \
        'User should see only polls from particular Run'
    for poll in response.data:
        assert poll['run'] == run.name, 'User should see only his polls'


@pytest.mark.django_db
def test_change_poll_moderator(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    poll = PollFactory(run=run)
    change_data = {
        'question': 'New Poll Question',
    }
    response = client.patch(
        f'/api/polls/mod/{run.moderator_session_code}/{poll.id}/',
        change_data, format='json')
    assert response.status_code == 200, 'Poll was not changed'
    assert response.data['question'] == change_data['question'], \
        'Poll was not changed'


@pytest.mark.django_db
def test_delete_poll_moderator(client):
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    poll = PollFactory(run=run)
    response = client.delete(
        f'/api/polls/mod/{run.moderator_session_code}/{poll.id}/',
        format='json')
    assert response.status_code == 204, \
        'Poll was not deleted correctly'
