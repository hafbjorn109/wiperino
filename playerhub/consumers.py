import json
import redis
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
import playerhub.serializers as ph_serializers
from asgiref.sync import sync_to_async

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


class WipecounterConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for authenticated users interacting with wipe counter sessions.
    Handles segment updates, creation, finishing, and run finalization.
    """

    async def connect(self):
        """Joins the user to a group based on the run ID."""
        self.run_id = self.scope['url_route']['kwargs']['run_id']
        self.room_group_name = f'run_{self.run_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Leaves the group when the WebSocket connection is closed."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )


    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages from the client and dispatches them to the group.
        Supports wipe updates, segment creation, finishing segments, and finishing runs.
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            error_serializer = ph_serializers.WebSocketErrorSerializer({
                'type': 'error',
                'message': 'Wrong JSON format'
            })
            await self.send(text_data=error_serializer.data)
            return

        message_type = data.get('type')

        serializer_map = {
            'wipe_update': ph_serializers.WipeUpdateSerializer,
            'new_segment': ph_serializers.NewSegmentSerializer,
            'segment_finished': ph_serializers.SegmentFinishedSerializer,
            'run_finished': ph_serializers.RunFinishedSerializer
        }

        serializer_class = serializer_map.get(message_type)
        if not serializer_class:
            error_serializer = ph_serializers.WebSocketErrorSerializer({
                'type': 'error',
                'error': 'Invalid message type'
            })
            await self.send(text_data=json.dumps(error_serializer.data))
            return

        serializer = serializer_class(data=data)
        if not serializer.is_valid():
            error_serializer = ph_serializers.WebSocketErrorSerializer({
                'type': 'error',
                'error': serializer.errors
            })
            await self.send(text_data=json.dumps(error_serializer.data))
            return

        validated_data = serializer.validated_data
        payload = {'type': message_type, **validated_data, 'user': self.scope['user'].username}

        broadcast_serializer_map = {
            'wipe_update': ph_serializers.WipeUpdateBroadcastSerializer,
            'new_segment': ph_serializers.NewSegmentBroadcastSerializer,
            'segment_finished': ph_serializers.SegmentFinishedBroadcastSerializer,
            'run_finished': ph_serializers.RunFinishedBroadcastSerializer
        }

        out_serializer_class = broadcast_serializer_map.get(message_type)
        out_serializer = out_serializer_class(instance=payload)

        await self.channel_layer.group_send(self.room_group_name, out_serializer.data)

    async def wipe_update(self, event):
        """Broadcasts a wipe counter update to all group members."""
        serializer = ph_serializers.WipeUpdateBroadcastSerializer(instance=event)
        await self.send(text_data=json.dumps(serializer.data))

    async def new_segment(self, event):
        """Broadcasts a new segment to all group members."""
        serializer = ph_serializers.NewSegmentBroadcastSerializer(instance=event)
        await self.send(text_data=json.dumps(serializer.data))

    async def segment_finished(self, event):
        """Broadcasts that a segment has been marked as finished."""
        serializer = ph_serializers.SegmentFinishedBroadcastSerializer(instance=event)
        await self.send(text_data=json.dumps(serializer.data))

    async def run_finished(self, event):
        """Broadcasts that the entire run has been finished."""
        serializer = ph_serializers.RunFinishedBroadcastSerializer(instance=event)
        await self.send(text_data=json.dumps(serializer.data))


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
        serializer = ph_serializers.WipeUpdateBroadcastSerializer(instance=event)
        await self.send(text_data=json.dumps(serializer.data))

    async def new_segment(self, event):
        """Sends new segment data to the overlay client."""
        serializer = ph_serializers.NewSegmentBroadcastSerializer(instance=event)
        await self.send(text_data=json.dumps(serializer.data))

    async def segment_finished(self, event):
        """Sends notification that a segment is finished."""
        serializer = ph_serializers.SegmentFinishedBroadcastSerializer(instance=event)
        await self.send(text_data=json.dumps(serializer.data))

    async def run_finished(self, event):
        """Sends notification that the run has ended."""
        serializer = ph_serializers.RunFinishedBroadcastSerializer(instance=event)
        await self.send(text_data=json.dumps(serializer.data))


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
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages from the client and dispatches them to the group.
        Supports publishing a question and unpublishing a question to OBS overlay and votes view.
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            error_serializer = ph_serializers.WebSocketErrorSerializer({
                'type': 'error',
                'error': 'Wrong JSON format'
            })
            await self.send(text_data=json.dumps(error_serializer.data))
            return

        message_type = data.get('type')

        if (message_type in ['publish_question', 'unpublish_question']
                and '-mod' not in self.client_token):
            serializer = ph_serializers.WebSocketErrorSerializer({
                'type': 'error',
                'error': 'Only moderators can perform this action'
            })
            await self.send(text_data=json.dumps(serializer.data))
            return

        if data.get('type') == 'publish_question':
            question_id = data['question_id']
            redis_key = f'poll:question:{question_id}'

            question_data_raw = await sync_to_async(r.get)(redis_key)
            if not question_data_raw:
                serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': 'Question not found'
                })
                await self.send(text_data=json.dumps(serializer.data))
                return

            question_data = json.loads(question_data_raw)

            if 'votes' not in question_data:
                question_data['votes'] = {answer: 0 for answer in question_data['answers']}

            if not question_data:
                serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': 'Question not found'
                })
                await self.send(text_data=json.dumps(serializer.data))
                return

            session_key = f'poll:session:{self.session_id}'
            session_data_raw = await sync_to_async(r.get)(session_key)
            if not session_data_raw:
                serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': 'Session not found'
                })
                await self.send(text_data=json.dumps(serializer.data))
                return

            session_data = json.loads(session_data_raw)
            session_data['published_question_id'] = question_id
            await sync_to_async(r.set)(session_key, json.dumps(session_data), ex=86400)

            message_payload = {
                'type': 'publish_question',
                'question_id': question_id,
                'question_data': question_data
            }

            serializer = ph_serializers.PublishedQuestionSerializer(data=message_payload)

            if not serializer.is_valid():
                error_serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': serializer.errors
                })
                await self.send(text_data=json.dumps(error_serializer.data))
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'publish_question',
                    'message': serializer.data
                }
            )

        elif data.get('type') == 'unpublish_question':
            session_key = f'poll:session:{self.session_id}'
            session_data_raw = await sync_to_async(r.get)(session_key)
            if not session_data_raw:
                serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': 'Session not found'
                })
                await self.send(text_data=json.dumps(serializer.data))
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
            serializer = ph_serializers.PollVoteSerializer(data=data)
            if not serializer.is_valid():
                error_serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': serializer.errors
                })

                await self.send(text_data=json.dumps(error_serializer.data))
                return

            validated_data = serializer.validated_data
            question_id = validated_data['question_id']
            answer = validated_data['answer']

            question_data_raw = await sync_to_async(r.get)(f'poll:question:{question_id}')

            if not question_data_raw:
                serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': 'Question not found'
                })
                await self.send(text_data=json.dumps(serializer.data))
                return

            question = json.loads(question_data_raw)

            if answer not in question.get('answers', []):
                serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': 'Answer not found'
                })
                await self.send(text_data=json.dumps(serializer.data))
                return

            question['votes'][answer] += 1

            await sync_to_async(r.set)(f'poll:question:{question_id}',
                                       json.dumps(question),
                                       ex=86400)

            vote_data = {
                'type': 'vote',
                'question_id': question_id,
                'answers': question['answers'],
                'votes': question['votes']
            }

            out_serializer = ph_serializers.VoteUpdateSerializer(data=vote_data)
            if not out_serializer.is_valid():
                error_serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': out_serializer.errors
                })
                await self.send(text_data=json.dumps(error_serializer.data))
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'vote_update',
                    'message': out_serializer.data
                }
            )

        elif data.get('type') == 'sync_questions' and '-mod' in self.client_token:
            questions_ids = r.lrange(f'poll:session:{self.session_id}:questions', 0, -1)
            for qid in questions_ids:
                q_raw = r.get(f'poll:question:{qid}')
                if not q_raw:
                    error_serializer = ph_serializers.WebSocketErrorSerializer({
                        'type': 'error',
                        'error': 'Question not found'
                    })
                    await self.send(text_data=json.dumps(error_serializer.data))
                    return

                question = json.loads(q_raw)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'new_question',
                        'message': {
                            'type': 'new_question',
                            'question': question
                        }
                    }
                )

        elif data.get('type') == 'delete_question' and '-mod' in self.client_token:
            serializer = ph_serializers.DeleteQuestionSerializer(data={
                'type': 'delete_question',
                'question_id': data.get('question_id')
            })
            if not serializer.is_valid():
                error_serializer = ph_serializers.WebSocketErrorSerializer({
                    'type': 'error',
                    'error': serializer.errors
                })
                await self.send(text_data=json.dumps(error_serializer.data))
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_question',
                    'message': serializer.data
                }
            )

    async def publish_question(self, event):
        """Broadcasts a publishing trigger for a question to all group members."""
        serializer = ph_serializers.PublishedQuestionSerializer(event['message'])
        await self.send(text_data=json.dumps(serializer.data))

    async def unpublish_question(self, event):
        """Broadcasts an unpublishing trigger for a question to all group members."""
        serializer = ph_serializers.UnpublishQuestionSerializer({'type': 'unpublish_question'})
        await self.send(text_data=json.dumps(serializer.data))

    async def vote_update(self, event):
        """Broadcasts a vote update for a question to all group members."""
        serializer = ph_serializers.VoteUpdateSerializer(event['message'])
        await self.send(text_data=json.dumps(serializer.data))

    async def new_question(self, event):
        """Broadcasts a new question to all group members."""
        serializer = ph_serializers.NewQuestionSerializer(event['message'])
        await self.send(text_data=json.dumps(serializer.data))

    async def delete_question(self, event):
        """Broadcasts a delete question to all group members."""
        serializer = ph_serializers.DeleteQuestionSerializer(event['message'])
        await self.send(text_data=json.dumps(serializer.data))


class TimerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Joins a group based on timer ID for receiving real-time updates."""
        self.run_id = self.scope['url_route']['kwargs']['run_id']
        self.room_group_name = f'timer_{self.run_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """Leaves the group when the WebSocket connection is closed."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receives incoming WebSocket messages, validates them using the appropriate
        serializer (based on message 'type'), and broadcasts structured payload
        to all group members using a broadcast serializer.
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            error_serializer = ph_serializers.WebSocketErrorSerializer({
                'type': 'error',
                'error': 'Invalid JSON format'
            })
            await self.send(text_data=json.dumps(error_serializer.data))
            return

        message_type = data.get('type')

        input_serializer_map = {
            'start_timer': ph_serializers.TimerStartSerializer,
            'pause_timer': ph_serializers.TimerPauseSerializer,
            'finish_timer': ph_serializers.TimerFinishSerializer,
            'run_finished': ph_serializers.RunFinishedSerializer,
            'new_segment': ph_serializers.NewTimerSegmentSerializer,
        }

        serializer_class = input_serializer_map.get(message_type)
        if not serializer_class:
            error_serializer = ph_serializers.WebSocketErrorSerializer({
                'type': 'error',
                'error': 'Invalid message type'
            })
            await self.send(text_data=json.dumps(error_serializer.data))
            return

        serializer = serializer_class(data=data)
        if not serializer.is_valid():
            error_serializer = ph_serializers.WebSocketErrorSerializer({
                'type': 'error',
                'error': serializer.errors
            })
            await self.send(text_data=json.dumps(error_serializer.data))
            return

        validated_data = serializer.validated_data

        payload = {
            'type': message_type,
            **validated_data,
            'user': self.scope['user'].username
        }

        if message_type == 'new_segment':
            broadcast = ph_serializers.NewTimerSegmentSerializer(instance=payload)
        else:
            broadcast = ph_serializers.TimerBroadcastSerializer(instance=payload)

        await self.channel_layer.group_send(self.room_group_name, broadcast.data)

    async def start_timer(self, event):
        """
        Handles broadcasting of 'start_timer' events to the client.
        Used to synchronize timer start between dashboard and overlay.
        """
        serializer = ph_serializers.TimerBroadcastSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))

    async def pause_timer(self, event):
        """
        Handles broadcasting of 'pause_timer' events to the client.
        Used to stop the live update of the timer and sync elapsed time.
        """
        serializer = ph_serializers.TimerBroadcastSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))

    async def finish_timer(self, event):
        """
        Handles broadcasting of 'finish_timer' events to the client.
        Used to mark a timer segment as completed and stop updates.
        """
        serializer = ph_serializers.TimerBroadcastSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))

    async def run_finished(self, event):
        """
        Handles broadcasting of 'run_finished' events to overlay or other clients.
        Signals that the run session has been completed.
        """
        serializer = ph_serializers.TimerBroadcastSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))

    async def new_segment(self, event):
        """
        Broadcasts a newly added segment to all connected clients in the run group.
        Used to synchronize table updates between multiple views.
        """
        serializer = ph_serializers.NewTimerSegmentSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))


class OverlayTimerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Joins a group based on timer ID for receiving real-time updates."""
        self.run_id = self.scope['url_route']['kwargs']['run_id']
        self.room_group_name = f'timer_{self.run_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection and removes the client from the timer group.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def start_timer(self, event):
        serializer = ph_serializers.TimerBroadcastSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))

    async def pause_timer(self, event):
        serializer = ph_serializers.TimerBroadcastSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))

    async def finish_timer(self, event):
        serializer = ph_serializers.TimerBroadcastSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))

    async def new_segment(self, event):
        serializer = ph_serializers.NewTimerSegmentSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))

    async def run_finished(self, event):
        serializer = ph_serializers.TimerBroadcastSerializer(event)
        await self.send(text_data=json.dumps(serializer.data))
