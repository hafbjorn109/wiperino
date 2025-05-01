import pytest
from .factories import PollFactory, AnswerFactory
from playerhub.tests.factories import UserFactory, RunFactory
from livehub.models import Answer


@pytest.mark.django_db
def test_add_answer_moderator(client):
    """
    Test to ensure that a moderator can add an answer to a poll.

    Expects a 201 Created response and one additional answer in the database.
    """
    answers_count = Answer.objects.count()
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    poll = PollFactory(run=run)
    data = {
        'answer': 'Test Answer',
        'votes': 25
    }
    response = client.post(
        f'/api/polls/mod/{run.moderator_session_code}/{poll.id}/answers/', data,
        format='json')

    assert response.status_code == 201, 'Answer was not created'
    assert Answer.objects.count() == answers_count + 1, \
        'Answer was not created'


@pytest.mark.django_db
def test_get_answers_moderator(client):
    """
    Test to ensure that a moderator can retrieve only answers for a specific poll.

    Creates answers for the selected poll and others.
    Sends a GET request and expects only matching answers in the response.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    poll = PollFactory(run=run)
    AnswerFactory.create_batch(5, poll=poll)
    AnswerFactory.create_batch(4)
    response = client.get(
        f'/api/polls/mod/{run.moderator_session_code}/{poll.id}/answers/',
        {}, format='json')
    assert response.status_code == 200, 'Answers were not retrieved'
    assert len(response.data) == 5, \
        'User should see only answers from particular Poll'
    for answer in response.data:
        assert answer['poll'] == poll.id, \
            'Answer should belong to correct poll'


@pytest.mark.django_db
def test_get_answers_viewer(client):
    """
    Test to ensure that a viewer can retrieve answers via session code.

    Uses the public session_code instead of the moderator one.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    poll = PollFactory(run=run)
    AnswerFactory.create_batch(5, poll=poll)
    AnswerFactory.create_batch(4)
    response = client.get(
        f'/api/polls/{run.session_code}/{poll.id}/answers/',
        {}, format='json')
    assert response.status_code == 200, \
        'Answers were not retrieved'
    assert len(response.data) == 5, \
        'User should see only answers from particular Poll'
    for answer in response.data:
        assert answer['poll'] == poll.id, \
            'Answer should belong to correct poll'


@pytest.mark.django_db
def test_change_answer_moderator(client):
    """
    Test to ensure that a moderator can update an existing answer.

    Expects a 200 OK response and the answer to be changed.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    poll = PollFactory(run=run)
    answer = AnswerFactory(poll=poll)
    change_data = {
        'answer': 'New Answer',
        'votes': 25
    }
    response = client.patch(
        f'/api/polls/mod/{run.moderator_session_code}/{poll.id}/answers/{answer.id}/',
        change_data, format='json')
    assert response.status_code == 200, 'Answer was not changed'
    assert response.data['answer'] == change_data['answer'], \
        'Answer was not changed'


@pytest.mark.django_db
def test_delete_answer_moderator(client):
    """
    Test to ensure that a moderator can delete an existing answer.

    Expects a 204 No Content response and removal of the answer from the database.
    """
    user = UserFactory()
    client.force_authenticate(user=user)
    run = RunFactory(user=user)
    poll = PollFactory(run=run)
    answer = AnswerFactory(poll=poll)
    response = client.delete(
        f'/api/polls/mod/{run.moderator_session_code}/{poll.id}/answers/{answer.id}/',
        format='json')
    assert response.status_code == 204, \
        'Answer was not deleted correctly'
