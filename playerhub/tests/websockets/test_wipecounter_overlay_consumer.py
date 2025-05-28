import asyncio
import pytest
from channels.testing import WebsocketCommunicator
from wiperino.asgi import application
from ..factories import UserFactory, RunFactory, GameFactory
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_wipecounter_overlay_connection():
    """
    Test to ensure that connection to WebSocket can be established.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')

    communicator = WebsocketCommunicator(
        application,
        f'ws/overlay/runs/{run.id}/'
    )
    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed'
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_wipe_update_receiver():
    """
    Test to ensure that websocket receives 'wipe_update' message correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_broadcaster_url = f'ws/runs/{run.id}/?token={token}'
    ws_receiver_url = f'ws/overlay/runs/{run.id}/'

    communicator_broadcaster = WebsocketCommunicator(application, ws_broadcaster_url)
    communicator_receiver = WebsocketCommunicator(application, ws_receiver_url)
    connected_broadcaster, _ = await communicator_broadcaster.connect()
    connected_receiver, _ = await communicator_receiver.connect()
    assert connected_broadcaster, 'Broadcaster WebSocket connection failed'
    assert connected_receiver, 'Receiver WebSocket connection failed'

    await communicator_broadcaster.send_json_to({
        'type': 'wipe_update',
        'segment_id': 1,
        'count': 42
    })

    response = await communicator_receiver.receive_json_from()
    assert response['type'] == 'wipe_update', 'Wrong response type.'
    assert response['segment_id'] == 1, 'Wrong response.'
    assert response['count'] == 42, 'Wrong response.'

    await communicator_receiver.disconnect()
    await communicator_broadcaster.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_new_segment_receiver():
    """
    Test to ensure that websocket receives 'new_segment' message correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_broadcaster_url = f'ws/runs/{run.id}/?token={token}'
    ws_receiver_url = f'ws/overlay/runs/{run.id}/'

    communicator_broadcaster = WebsocketCommunicator(application, ws_broadcaster_url)
    communicator_receiver = WebsocketCommunicator(application, ws_receiver_url)
    connected_broadcaster, _ = await communicator_broadcaster.connect()
    connected_receiver, _ = await communicator_receiver.connect()
    assert connected_broadcaster, 'Broadcaster WebSocket connection failed'
    assert connected_receiver, 'Receiver WebSocket connection failed'

    await communicator_broadcaster.send_json_to({
        'type': 'new_segment',
        'segment_id': 1,
        'segment_name': 'New Segment',
        'count': 42,
        'is_finished': False,
    })

    response = await communicator_receiver.receive_json_from()
    assert response['type'] == 'new_segment', 'Wrong response type.'
    assert response['segment_name'] == 'New Segment', 'Wrong response.'
    assert response['count'] == 42, 'Wrong response.'
    assert response['is_finished'] == False, 'Wrong response.'

    await communicator_receiver.disconnect()
    await communicator_broadcaster.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_segment_finished_receiver():
    """
    Test to ensure that websocket receives 'segment_finished' message correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_broadcaster_url = f'ws/runs/{run.id}/?token={token}'
    ws_receiver_url = f'ws/overlay/runs/{run.id}/'

    communicator_broadcaster = WebsocketCommunicator(application, ws_broadcaster_url)
    communicator_receiver = WebsocketCommunicator(application, ws_receiver_url)
    connected_broadcaster, _ = await communicator_broadcaster.connect()
    connected_receiver, _ = await communicator_receiver.connect()
    assert connected_broadcaster, 'Broadcaster WebSocket connection failed'
    assert connected_receiver, 'Receiver WebSocket connection failed'

    await communicator_broadcaster.send_json_to({
        'type': 'segment_finished',
        'segment_id': 1,
    })

    response = await communicator_receiver.receive_json_from()
    assert response['type'] == 'segment_finished', 'Wrong response type.'
    assert response['segment_id'] == 1, 'Wrong response.'

    await communicator_receiver.disconnect()
    await communicator_broadcaster.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_run_finished_receiver():
    """
    Test to ensure that websocket receives 'run_finished' message correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_broadcaster_url = f'ws/runs/{run.id}/?token={token}'
    ws_receiver_url = f'ws/overlay/runs/{run.id}/'

    communicator_broadcaster = WebsocketCommunicator(application, ws_broadcaster_url)
    communicator_receiver = WebsocketCommunicator(application, ws_receiver_url)
    connected_broadcaster, _ = await communicator_broadcaster.connect()
    connected_receiver, _ = await communicator_receiver.connect()
    assert connected_broadcaster, 'Broadcaster WebSocket connection failed'
    assert connected_receiver, 'Receiver WebSocket connection failed'

    await communicator_broadcaster.send_json_to({
        'type': 'run_finished',
    })

    response = await communicator_receiver.receive_json_from()
    assert response['type'] == 'run_finished', 'Wrong response type.'

    await communicator_receiver.disconnect()
    await communicator_broadcaster.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_wipecounter_wrong_data_receiver():
    """
    Test to ensure that wrong data format is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='WIPECOUNTER')
    token = str(AccessToken.for_user(user))

    ws_broadcaster_url = f'ws/runs/{run.id}/?token={token}'
    ws_receiver_url = f'ws/overlay/runs/{run.id}/'

    communicator_broadcaster = WebsocketCommunicator(application, ws_broadcaster_url)
    communicator_receiver = WebsocketCommunicator(application, ws_receiver_url)
    connected_broadcaster, _ = await communicator_broadcaster.connect()
    connected_receiver, _ = await communicator_receiver.connect()
    assert connected_broadcaster, 'Broadcaster WebSocket connection failed'
    assert connected_receiver, 'Receiver WebSocket connection failed'

    await communicator_broadcaster.send_to('{not:valid json}')

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(communicator_receiver.receive_json_from(), timeout=0.5)

    await communicator_receiver.disconnect()
    await communicator_broadcaster.disconnect()
