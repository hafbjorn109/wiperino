import uuid
import pytest
from django.conf import settings
import redis
import json

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@pytest.mark.django_db
def test_create_poll_session(client):
    response = client.post('/api/polls/create_session/', {}, format='json')
    assert response.status_code == 201, 'Session was not created'
    data = response.json()

    assert 'moderator_url' in data, 'Moderator URL was not returned'
    assert 'session_id' in data, 'Session ID was not returned'
    assert 'viewer_url' in data, 'Viewer URL was not returned'
    assert 'overlay_url' in data, 'Overlay URL was not returned'

    moderator_token = data['moderator_url'].split('/m/')[1]
    viewer_token = data['viewer_url'].split('/v/')[1]
    overlay_token = data['overlay_url'].split('/o/')[1]

    session_id = data['session_id']
    assert r.get(f'poll:token_map:{moderator_token}') == session_id, 'Moderator token was not mapped to session ID'
    assert r.get(f'poll:token_map:{viewer_token}') == session_id, 'Viewer token was not mapped to session ID'
    assert r.get(f'poll:token_map:{overlay_token}') == session_id, 'Overlay token was not mapped to session ID'

    session_exists = r.get(f'poll:session:{session_id}')
    assert session_exists is not None, 'Session was not stored in Redis'


def test_add_poll(client):
    session_id = str(uuid.uuid4())
    moderator_token = f'{session_id}-mod-test'
    r.set(f'poll:token_map:{moderator_token}', session_id, ex=60)

    data = {
        'question': 'Test Question',
        'answers': ['Yes', 'No']
    }

    response = client.post(f'/api/polls/m/{moderator_token}/add_poll/', data, format='json')

    assert response.status_code == 201, 'Poll was not created'
    response_json = response.json()
    assert 'question_id' in response_json, 'Question ID was not returned'
    assert response_json['question'] == data['question']
    assert response_json['answers'] == data['answers']

    redis_key = f'poll:question:{response_json["question_id"]}'
    stored = r.get(redis_key)
    assert stored is not None, 'Poll was not stored in Redis'


def test_list_poll_questions(client):
    session_id = str(uuid.uuid4())
    moderator_token = f'{session_id}-mod-test'
    question_id_1 = 'q-123'
    question_id_2 = 'q-456'

    r.set(f'poll:token_map:{moderator_token}', session_id, ex=60)
    r.rpush(f'poll:session:{session_id}:questions', question_id_1, question_id_2)

    r.set(f'poll:question:{question_id_1}', json.dumps({
        'id': question_id_1,
        'question': 'Question 1',
        'answers': ['Yes', 'No'],
        'votes': {'Yes': 0, 'No': 0}
    }), ex=60)

    r.set(f'poll:question:{question_id_2}', json.dumps({
        'id': question_id_2,
        'question': 'Question 2',
        'answers': ['Yes', 'No'],
        'votes': {'Yes': 0, 'No': 0}
    }), ex=60)

    response = client.get(f'/api/polls/m/{moderator_token}/')
    assert response.status_code == 200, 'Questions were not retrieved'
    data = response.json()
    assert len(data) == 2, 'Wrong number of questions returned'
    assert any(q["question"] == "Question 1" for q in data)
    assert any(q["question"] == "Question 2" for q in data)


def test_delete_poll_question(client):
    session_id = str(uuid.uuid4())
    moderator_token = f'{session_id}-mod-test'
    question_id = 'q-123'

    r.set(f'poll:token_map:{moderator_token}', session_id, ex=60)
    r.rpush(f'poll:session:{session_id}:questions', question_id)
    r.set(f'poll:question:{question_id}', json.dumps({
        'id': question_id,
        'question': 'Question 1',
        'answers': ['Yes', 'No'],
        'votes': {'Yes': 0, 'No': 0}
    }), ex=60)

    response = client.delete(f'/api/polls/m/{moderator_token}/{question_id}/')
    assert response.status_code == 204, 'Question was not deleted'

    assert r.get(f'poll:question:{question_id}') is None, 'Question was not deleted from Redis'
    assert question_id not in r.lrange(f'poll:session:{session_id}:questions', 0, -1), 'Question was not removed from session'


