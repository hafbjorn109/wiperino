import pytest
from channels.testing import WebsocketCommunicator
from wiperino.asgi import application
from ..factories import UserFactory, RunFactory, GameFactory
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_wipecounter_connection():
    """
    Test to ensure that connection to WebSocket can be established.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    communicator = WebsocketCommunicator(
        application,
        f'/ws/runs/{run.id}/?token={token}',
    )

    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_wipecounter_broadcast_wipe_update():
    """
    Test to ensure that data between clients in WebSockets broadcasts correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected1, _ = await communicator_1.connect()
    connected2, _ = await communicator_2.connect()
    assert connected1, 'WebSocket connection failed.'
    assert connected2, 'WebSocket connection failed.'

    await communicator_1.send_json_to({
        'type': 'wipe_update',
        'segment_id': 1,
        'count': 42
    })

    response = await communicator_2.receive_json_from()
    assert response['type'] == 'wipe_update', 'Wrong response type.'
    assert response['segment_id'] == 1, 'Wrong response.'
    assert response['count'] == 42, 'Wrong response.'

    response_self = await communicator_1.receive_json_from()
    assert response_self['type'] == 'wipe_update', 'Wrong self response type.'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_wipecounter_broadcast_new_segment():
    """
    Test to ensure that 'new_segment' message type is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected, _ = await communicator_1.connect()
    connected, _ = await communicator_2.connect()

    await communicator_1.send_json_to({
        'type' : 'new_segment',
        'segment_id': 1,
        'segment_name': 'New Segment',
        'count': 42,
        'is_finished': False,
    })

    response = await communicator_2.receive_json_from()
    assert response['type'] == 'new_segment', 'Wrong response type.'
    assert response['segment_name'] == 'New Segment', 'Wrong response.'
    assert response['count'] == 42, 'Wrong response.'
    assert response['is_finished'] == False, 'Wrong response.'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_wipecounter_broadcast_segment_finished():
    """
    Test to ensure that 'segment_finished' message type is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected, _ = await communicator_1.connect()
    connected, _ = await communicator_2.connect()

    await communicator_1.send_json_to({
        'type': 'segment_finished',
        'segment_id': 1,
    })

    response = await communicator_2.receive_json_from()
    assert response['type'] == 'segment_finished', 'Wrong response type.'
    assert response['segment_id'] == 1, 'Wrong response.'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_wipecounter_broadcast_run_finished():
    """
    Test to ensure that 'run_finished' message type is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected1, _ = await communicator_1.connect()
    connected2, _ = await communicator_2.connect()

    await communicator_1.send_json_to({
        'type': 'run_finished',
    })

    response = await communicator_2.receive_json_from()
    assert response['type'] == 'run_finished', 'Wrong response type.'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_wipecounter_wrong_data():
    """
    Test to ensure that wrong data format is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/?token={token}'

    communicator = WebsocketCommunicator(application, ws_url)
    connected, _ = await communicator.connect()

    await communicator.send_to('{not:valid json}')
    response = await communicator.receive_json_from()
    assert response['type'] == 'error', 'Wrong response type.'
    await communicator.disconnect()
