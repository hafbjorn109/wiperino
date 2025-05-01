import pytest
from .factories import PollFactory
from playerhub.tests.factories import UserFactory, RunFactory
from livehub.models import Poll


@pytest.mark.django_db
def test_add_poll_moderator(client):
    """
    Test to ensure that a moderator can create a poll for a run.

    Sends a POST request with poll data using the moderator session code.
    Expects a 201 Created response and a new poll in the database.
    """
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
    """
    Test to ensure that a moderator can retrieve polls for their run.

    Creates polls for the user's run and other runs.
    Sends a GET request with moderator session code and expects only relevant polls.
    """
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
    """
    Test to ensure that viewers can retrieve public polls for a run.

    Uses the public session code to access published polls.
    Expects only polls related to the specific run.
    """
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
    """
    Test to ensure that a moderator can update their own poll.

    Sends a PATCH request with updated data using moderator session code.
    Expects a 200 OK response and updated poll data.
    """
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
    """
    Test to ensure that a moderator can delete a poll they created.

    Sends a DELETE request using moderator session code.
    Expects a 204 No Content response and poll removal.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    poll = PollFactory(run=run)
    response = client.delete(
        f'/api/polls/mod/{run.moderator_session_code}/{poll.id}/',
        format='json')
    assert response.status_code == 204, \
        'Poll was not deleted correctly'
