from datetime import datetime
import pytest
from channels.testing import WebsocketCommunicator
from wiperino.asgi import application
from ..factories import UserFactory, RunFactory, GameFactory
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_timer_connection():
    """
    Test to ensure that connection to WebSocket can be established.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='SPEEDRUN')
    token = str(AccessToken.for_user(user))

    communicator = WebsocketCommunicator(
        application,
        f'/ws/runs/{run.id}/timer/?token={token}',
    )
    connected, _ = await communicator.connect()
    assert connected, 'WebSocket connection failed.'
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_timer_start_timer():
    """
    Test to ensure that 'start_timer' message is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='SPEEDRUN')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/timer/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected1, _ = await communicator_1.connect()
    connected2, _ = await communicator_2.connect()

    await communicator_1.send_json_to({
        'type': 'start_timer',
        'segment_id': 1,
        'started_at': datetime.now().isoformat(),
        'elapsed_time': 0.0,
    })

    response = await communicator_2.receive_json_from()

    assert response['type'] == 'start_timer', 'Wrong response type'
    assert response['segment_id'] == 1, 'Wrong response data'
    assert response['elapsed_time'] == 0.0, 'Wrong response data'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_timer_pause_timer():
    """
    Test to ensure that 'start_timer' message is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='SPEEDRUN')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/timer/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected1, _ = await communicator_1.connect()
    connected2, _ = await communicator_2.connect()

    await communicator_1.send_json_to({
        'type': 'pause_timer',
        'segment_id': 1,
        'elapsed_time': 12.0,
    })

    response = await communicator_2.receive_json_from()

    assert response['type'] == 'pause_timer', 'Wrong response type'
    assert response['segment_id'] == 1, 'Wrong response data'
    assert response['elapsed_time'] == 12.0, 'Wrong response data'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_timer_finish_timer():
    """
    Test to ensure that 'start_timer' message is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='SPEEDRUN')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/timer/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected1, _ = await communicator_1.connect()
    connected2, _ = await communicator_2.connect()

    await communicator_1.send_json_to({
        'type': 'finish_timer',
        'segment_id': 1,
        'elapsed_time': 12.0,
    })

    response = await communicator_2.receive_json_from()

    assert response['type'] == 'finish_timer', 'Wrong response type'
    assert response['segment_id'] == 1, 'Wrong response data'
    assert response['elapsed_time'] == 12.0, 'Wrong response data'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_timer_run_finished():
    """
    Test to ensure that 'start_timer' message is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='SPEEDRUN')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/timer/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected1, _ = await communicator_1.connect()
    connected2, _ = await communicator_2.connect()

    await communicator_1.send_json_to({
        'type': 'run_finished',
    })

    response = await communicator_2.receive_json_from()

    assert response['type'] == 'run_finished', 'Wrong response type'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_timer_new_segment():
    """
    Test to ensure that 'start_timer' message is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='SPEEDRUN')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/timer/?token={token}'

    communicator_1 = WebsocketCommunicator(application, ws_url)
    communicator_2 = WebsocketCommunicator(application, ws_url)

    connected1, _ = await communicator_1.connect()
    connected2, _ = await communicator_2.connect()

    await communicator_1.send_json_to({
        'type': 'new_segment',
        'segment_id': 1,
        'segment_name': 'New Segment',
        'elapsed_time': 0.0,
        'is_finished': False,
    })

    response = await communicator_2.receive_json_from()

    assert response['type'] == 'new_segment', 'Wrong response type'
    assert response['segment_id'] == 1, 'Wrong response data'
    assert response['elapsed_time'] == 0.0, 'Wrong response data'
    assert response['is_finished'] is False, 'Wrong response data'
    assert response['segment_name'] == 'New Segment', 'Wrong response data'

    await communicator_1.disconnect()
    await communicator_2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_timer_wrong_data():
    """
    Test to ensure that wrong data format is handled correctly.
    """
    user = await sync_to_async(UserFactory)()
    game = await sync_to_async(GameFactory)()
    run = await sync_to_async(RunFactory)(user=user, game=game, mode='SPEEDRUN')
    token = str(AccessToken.for_user(user))

    ws_url = f'ws/runs/{run.id}/timer/?token={token}'

    communicator = WebsocketCommunicator(application, ws_url)
    connected, _ = await communicator.connect()

    await communicator.send_to('{not:valid json}')
    response = await communicator.receive_json_from()
    assert response['type'] == 'error', 'Wrong response type.'