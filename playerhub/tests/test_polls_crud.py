import uuid
import pytest
from django.conf import settings
import redis

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


@pytest.mark.django_db
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