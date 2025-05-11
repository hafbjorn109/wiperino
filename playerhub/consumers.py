import json
import redis
from rest_framework import serializers
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from playerhub.serializers import  PollVoteSerializer
from asgiref.sync import sync_to_async

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


class WipecounterConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for authenticated users interacting with wipe counter sessions.
    Handles segment updates, creation, finishing, and run finalization.
    """

    async def connect(self):
        """Joins the user to a group based on the run ID."""
        print('WS CONNECTED')
        self.run_id = self.scope['url_route']['kwargs']['run_id']
        self.room_group_name = f'run_{self.run_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Removes the user from the group upon WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages from the client and dispatches them to the group.
        Supports wipe updates, segment creation, finishing segments, and finishing runs.
        """
        print("WS RECEIVE:", text_data)
        data = json.loads(text_data)

        if data.get('type') == 'wipe_update':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'wipe_update',
                    'segment_id': data['segment_id'],
                    'count': data['count'],
                    'user': self.scope['user'].username
                }
            )

        if data.get('type') == 'new_segment':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_segment',
                    'segment_id': data['segment_id'],
                    'segment_name': data['segment_name'],
                    'count': data['count'],
                    'is_finished': data['is_finished'],
                    'user': self.scope['user'].username
                }
            )

        if data.get('type') == 'segment_finished':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'segment_finished',
                    'segment_id': data['segment_id'],
                    'user': self.scope['user'].username
                }
            )

        if data.get('type') == 'run_finished':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'run_finished',
                    'user': self.scope['user'].username
                }
            )

    async def wipe_update(self, event):
        """Broadcasts a wipe counter update to all group members."""
        print("broadcasting to client:", event)
        await self.send(text_data=json.dumps({
            'type': 'wipe_update',
            'segment_id': event['segment_id'],
            'count': event['count'],
            'user': event['user']
        }))

    async def new_segment(self, event):
        """Broadcasts a new segment to all group members."""
        await self.send(text_data=json.dumps({
            'type': 'new_segment',
            'segment_id': event['segment_id'],
            'segment_name': event['segment_name'],
            'count': event['count'],
            'is_finished': event['is_finished'],
            'user': event['user']
        }))

    async def segment_finished(self, event):
        """Broadcasts that a segment has been marked as finished."""
        await self.send(text_data=json.dumps({
            'type': 'segment_finished',
            'segment_id': event['segment_id'],
            'user': event['user']
        }))

    async def run_finished(self, event):
        """Broadcasts that the entire run has been finished."""
        await self.send(text_data=json.dumps({
            'type': 'run_finished',
            'user': event['user']
        }))


class OverlayConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for public overlays (no authentication).
    Receives and broadcasts updates for OBS overlays in real time.
    """
    async def connect(self):
        """Joins a group based on run ID for receiving real-time updates."""
        self.run_id = self.scope['url_route']['kwargs']['run_id']
        self.room_group_name = f'run_{self.run_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Leaves the group when the WebSocket connection is closed."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def wipe_update(self, event):
        """Sends wipe count updates to the overlay client."""
        print("Overlay WS received wipe_update:", event)
        await self.send(text_data=json.dumps({
            'type': 'wipe_update',
            'segment_id': event['segment_id'],
            'count': event['count']
        }))

    async def new_segment(self, event):
        """Sends new segment data to the overlay client."""
        await self.send(text_data=json.dumps({
            'type': 'new_segment',
            'segment_id': event['segment_id'],
            'segment_name': event['segment_name'],
            'count': event['count'],
            'is_finished': event['is_finished']
        }))

    async def segment_finished(self, event):
        """Sends notification that a segment is finished."""
        await self.send(text_data=json.dumps({
            'type': 'segment_finished',
            'segment_id': event['segment_id']
        }))

    async def run_finished(self, event):
        """Sends notification that the run has ended."""
        await self.send(text_data=json.dumps({
            'type': 'run_finished'
        }))


class PollConsumer(AsyncWebsocketConsumer):
    """
    Websocket consumer for users interacting with poll sessions.
    Receives and broadcasts updates for poll questions in real time.
    """
    async def connect(self):
        """Joins a group based on poll session ID for receiving real-time updates."""
        self.client_token = self.scope['url_route']['kwargs']['client_token']
        self.session_id = r.get(f'poll:token_map:{self.client_token}')

        if not self.session_id:
            await self.close()
            return

        self.room_group_name = f'poll_{self.session_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Leaves the group when the WebSocket connection is closed."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages from the client and dispatches them to the group.
        Supports publishing a question and unpublishing a question to OBS overlay and votes view.
        """
        data = json.loads(text_data)
        print('[WS] Received data: ', data)

        if data.get('type') in ['publish_question', 'unpublish_question'] and '-mod' not in self.client_token:
            error_data = {
                'type': 'error',
                'error': 'Only moderators can perform this action'
            }
            await self.send(text_data=json.dumps(error_data))
            return

        if data.get('type') == 'publish_question':
            question_id = data['question_id']
            redis_key = f'poll:question:{question_id}'

            question_data = await sync_to_async(r.get)(redis_key)

            if not question_data:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': 'Question not found'
                }))
                return

            session_key = f'poll:session:{self.session_id}'
            session_data_raw = await sync_to_async(r.get)(session_key)
            if not session_data_raw:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': 'Session not found'
                }))
                return

            session_data = json.loads(session_data_raw)
            session_data['published_question_id'] = question_id
            await sync_to_async(r.set)(session_key, json.dumps(session_data), ex=86400)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'publish_question',
                    'question_id': question_id,
                    'question_data': question_data
                }
            )

        elif data.get('type') == 'unpublish_question':
            session_key = f'poll:session:{self.session_id}'
            session_data_raw = await sync_to_async(r.get)(session_key)
            if not session_data_raw:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': 'Session not found'
                }))
                return

            session_data = json.loads(session_data_raw)
            session_data['published_question_id'] = None
            await sync_to_async(r.set)(session_key, json.dumps(session_data), ex=86400)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'unpublish_question',
                }
            )

        elif data.get('type') == 'vote':
            print('[WS] Trying to validate vote:', data)
            serializer = PollVoteSerializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as e:
                error_data = {
                    'type': 'error',
                    'error': e.detail
                }
                await self.send(text_data=json.dumps(error_data))
                return

            validated_data = serializer.validated_data
            question_id = validated_data['question_id']
            answer = validated_data['answer']

            question_data_raw = await sync_to_async(r.get)(f'poll:question:{question_id}')

            if not question_data_raw:
                error_data = {
                    'type': 'error',
                    'error': 'Question not found'
                }
                await self.send(text_data=json.dumps(error_data))
                return

            question = json.loads(question_data_raw)

            if answer not in question.get('answers', []):
                error_data = {
                    'type': 'error',
                    'error': 'Answer not found'
                }
                await self.send(text_data=json.dumps(error_data))
                return

            question['votes'][answer] += 1

            await sync_to_async(r.set)(f'poll:question:{question_id}',
                                       json.dumps(question),
                                       ex=86400)

            print(f'[WS] Updated Redis votes for {question_id}:', question['votes'])

            vote_data = {
                'type': 'vote',
                'question_id': question_id,
                'votes': question['votes']
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'vote_update',
                    'message': vote_data
                }
            )

        elif data.get('type') == 'sync_questions' and '-mod' in self.client_token:
            questions_ids = r.lrange(f'poll:session:{self.session_id}:questions', 0, -1)
            for qid in questions_ids:
                q_raw = r.get(f'poll:question:{qid}')
                if q_raw:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'new_question',
                            'message': {
                                'type': 'new_question',
                                'question': json.loads(q_raw)
                            }
                        }
                    )

        elif data.get('type') == 'delete_question' and '-mod' in self.client_token:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_question',
                    'message': {
                        'type': 'delete_question',
                        'question_id': data['question_id']
                    }
                }
            )


    async def publish_question(self, event):
        """Broadcasts a publishing trigger for a question to all group members."""
        await self.send(text_data=json.dumps({
            'type': 'publish_question',
            'question_id': event['question_id'],
            'question_data': event['question_data']
        }))


    async def unpublish_question(self, event):
        """Broadcasts an unpublishing trigger for a question to all group members."""
        await self.send(text_data=json.dumps({
            'type': 'unpublish_question',
        }))


    async def vote_update(self, event):
        """Broadcasts a vote update for a question to all group members."""
        await self.send(text_data=json.dumps(event['message']))


    async def new_question(self, event):
        """Broadcasts a new question to all group members."""
        await self.send(text_data=json.dumps(event['message']))


    async def delete_question(self, event):
        """Broadcasts a delete question to all group members."""
        await self.send(text_data=json.dumps(event['message']))
