import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WipecounterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('WS CONNECTED')
        self.run_id = self.scope['url_route']['kwargs']['run_id']
        self.room_group_name = f'run_{self.run_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        print("WS RECEIVE:", text_data)
        data = json.loads(text_data)

        if 'segment_id' not in data or 'count' not in data:
            return

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

    async def wipe_update(self, event):
        print("broadcasting to client:", event)
        await self.send(text_data=json.dumps({
            'type': 'wipe_update',
            'segment_id': event['segment_id'],
            'count': event['count'],
            'user': event['user']
        }))

    async def new_segment(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_segment',
            'segment_id': event['segment_id'],
            'segment_name': event['segment_name'],
            'count': event['count'],
            'is_finished': event['is_finished'],
            'user': event['user']
        }))