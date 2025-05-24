import json

import pytest
import redis
import uuid
from django.conf import settings
from channels.testing import WebsocketCommunicator
from wiperino.asgi import application
from asgiref.sync import sync_to_async

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@pytest.mark.asyncio
async def test_ws_poll_connection():
    """
    Test to ensure that connection to WebSocket can be established.
    """
    client_token = 'abc-mod-123'
    session_id = uuid.uuid4().hex[:6]

    await sync_to_async(r.set)(f'poll:token_map:{client_token}', session_id)

    communicator = WebsocketCommunicator(
        application,
        f'/ws/polls/{client_token}/'
    )
    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'
    await sync_to_async(r.delete)(f'poll:token_map:{client_token}')
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_ws_poll_publish_question_broadcast():
    """
    Test to ensure that 'publish_question' message is handled correctly.
    """
    client_token = 'abc-mod-123'
    session_id = uuid.uuid4().hex[:6]
    question_id = uuid.uuid4().hex[:6]
    question_data = {
        'id': question_id,
        'question': 'Question?',
        'answers': ['Yes', 'No']
    }

    await sync_to_async(r.set)(f'poll:token_map:{client_token}', session_id)
    await sync_to_async(r.set)(f'poll:question:{question_id}', json.dumps(question_data))
    await sync_to_async(r.set)(f'poll:session:{session_id}', json.dumps({}))

    communicator = WebsocketCommunicator(
        application,
        f'ws/polls/{client_token}/'
    )
    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'

    await communicator.send_json_to({
        'type': 'publish_question',
        'question_id': question_id,
    })

    response = await communicator.receive_json_from()
    assert response['type'] == 'publish_question', 'Wrong response type.'
    assert response['question_id'] == question_id
    assert 'question_data' in response
    assert response['question_data']['question'] == 'Question?'

    await communicator.disconnect()
    await sync_to_async(r.delete)(f'poll:token_map:{client_token}')
    await sync_to_async(r.delete)(f'poll:question:{question_id}')
    await sync_to_async(r.delete)(f'poll:session:{session_id}')


@pytest.mark.asyncio
async def test_ws_poll_unpublish_question_broadcast():
    """
    Test to ensure that 'unpublish_question' message is handled correctly.
    """
    client_token = 'abc-mod-123'
    session_id = uuid.uuid4().hex[:6]
    question_id = uuid.uuid4().hex[:6]
    question_data = {
        'id': question_id,
        'question': 'Question?',
        'answers': ['Yes', 'No']
    }

    await sync_to_async(r.set)(f'poll:token_map:{client_token}', session_id)
    await sync_to_async(r.set)(f'poll:question:{question_id}', json.dumps(question_data))
    await sync_to_async(r.set)(f'poll:session:{session_id}', json.dumps({}))

    communicator = WebsocketCommunicator(
        application,
        f'ws/polls/{client_token}/'
    )
    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'

    await communicator.send_json_to({
        'type': 'unpublish_question',
    })

    response = await communicator.receive_json_from()
    assert response['type'] == 'unpublish_question', 'Wrong response type.'
    assert set(response.keys()) == {'type'}, 'Unexpected keys in response'

    await communicator.disconnect()
    await sync_to_async(r.delete)(f'poll:token_map:{client_token}')
    await sync_to_async(r.delete)(f'poll:question:{question_id}')
    await sync_to_async(r.delete)(f'poll:session:{session_id}')


@pytest.mark.asyncio
async def test_ws_poll_vote_update_broadcast():
    """
    Test to ensure that 'vote_update' message is handled correctly.
    """
    client_token = 'abc-mod-123'
    session_id = uuid.uuid4().hex[:6]
    question_id = uuid.uuid4().hex[:6]
    question_data = {
        'id': question_id,
        'question': 'Question?',
        'answers': ['Yes', 'No'],
        'votes': {'Yes': 0, 'No': 0}
    }

    await sync_to_async(r.set)(f'poll:token_map:{client_token}', session_id)
    await sync_to_async(r.set)(f'poll:question:{question_id}', json.dumps(question_data))
    await sync_to_async(r.set)(f'poll:session:{session_id}', json.dumps({}))

    communicator = WebsocketCommunicator(
        application,
        f'ws/polls/{client_token}/'
    )
    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'

    await communicator.send_json_to({
        'type': 'vote',
        'question_id': question_id,
        'answer': 'Yes'
    })

    response = await communicator.receive_json_from()
    assert response['type'] == 'vote', 'Wrong response type.'
    assert response['question_id'] == question_id, 'Wrong question ID.'
    assert 'votes' in response, 'Missing votes in response.'
    assert response['votes']['Yes'] == 1, 'Vote not counted correctly.'
    assert response['votes']['No'] == 0, 'Other options should remain 0.'

    await communicator.disconnect()
    await sync_to_async(r.delete)(f'poll:token_map:{client_token}')
    await sync_to_async(r.delete)(f'poll:question:{question_id}')
    await sync_to_async(r.delete)(f'poll:session:{session_id}')


@pytest.mark.asyncio
async def test_ws_poll_new_question_broadcast():
    """"
    Test to ensure that 'new_question' message is handled correctly.
    """
    client_token = 'abc-mod-123'
    session_id = uuid.uuid4().hex[:6]
    question_id = uuid.uuid4().hex[:6]
    question_data = {
        'id': question_id,
        'question': 'Question?',
        'answers': ['Yes', 'No'],
        'votes': {'Yes': 0, 'No': 0}
    }

    await sync_to_async(r.set)(f'poll:token_map:{client_token}', session_id)
    await sync_to_async(r.set)(f'poll:question:{question_id}', json.dumps(question_data))
    await sync_to_async(r.rpush)(f'poll:session:{session_id}:questions', question_id)

    communicator = WebsocketCommunicator(
        application,
        f'ws/polls/{client_token}/'
    )

    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'

    await communicator.send_json_to({
        'type': 'sync_questions'
    })

    response = await communicator.receive_json_from()
    assert response['type'] == 'new_question', 'Wrong response type.'
    assert response['question']['id'] == question_id, 'Wrong question ID.'
    assert 'question' in response, 'Missing question in response.'
    assert response['question']['question'] == 'Question?', 'Wrong question.'
    assert response['question']['answers'] == ['Yes', 'No'], 'Wrong answers.'

    await communicator.disconnect()
    await sync_to_async(r.delete)(f'poll:token_map:{client_token}')
    await sync_to_async(r.delete)(f'poll:question:{question_id}')
    await sync_to_async(r.delete)(f'poll:session:{session_id}:questions')


@pytest.mark.asyncio
async def test_ws_poll_delete_question_broadcast():
    """
    Test to ensure that 'delete_question' message is handled and broadcasted correctly.
    """
    client_token = 'abc-mod-123'
    session_id = uuid.uuid4().hex[:6]
    question_id = uuid.uuid4().hex[:6]

    question_data = {
        'id': question_id,
        'question': 'Should we test this?',
        'answers': ['Yes', 'Absolutely'],
        'votes': {'Yes': 0, 'Absolutely': 0}
    }
    await sync_to_async(r.set)(f'poll:token_map:{client_token}', session_id)
    await sync_to_async(r.set)(f'poll:question:{question_id}', json.dumps(question_data))
    await sync_to_async(r.rpush)(f'poll:session:{session_id}:questions', question_id)

    # Connect WebSocket
    communicator = WebsocketCommunicator(
        application,
        f'/ws/polls/{client_token}/'
    )

    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'

    await communicator.send_json_to({
        'type': 'delete_question',
        'question_id': question_id
    })

    response = await communicator.receive_json_from()
    assert response['type'] == 'delete_question', 'Wrong response type.'
    assert response['question_id'] == question_id, 'Wrong question ID.'

    await communicator.disconnect()
    await sync_to_async(r.delete)(f'poll:token_map:{client_token}')
    await sync_to_async(r.delete)(f'poll:question:{question_id}')
    await sync_to_async(r.delete)(f'poll:session:{session_id}:questions')


@pytest.mark.asyncio
async def test_poll_wrong_data():
    """
    Test to ensure that wrong data format is handled correctly.
    """
    client_token = 'abc-mod-123'
    session_id = uuid.uuid4().hex[:6]

    await sync_to_async(r.set)(f'poll:token_map:{client_token}', session_id)
    communicator = WebsocketCommunicator(
        application,
        f'/ws/polls/{client_token}/'
    )
    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'

    await communicator.send_to('{not:valid json}')
    response = await communicator.receive_json_from()

    assert response['type'] == 'error', 'Wrong response type.'
    assert 'Wrong JSON format' in response['error']

    await communicator.disconnect()
    await sync_to_async(r.delete)(f'poll:token_map:{client_token}')