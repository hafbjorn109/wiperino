from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/runs/(?P<run_id>\d+)/$', consumers.WipecounterConsumer.as_asgi()),
    re_path(r'ws/overlay/runs/(?P<run_id>\d+)/$', consumers.OverlayConsumer.as_asgi()),
    re_path(r'ws/polls/(?P<client_token>[\w\-]+)/$', consumers.PollConsumer.as_asgi()),
    re_path(r'ws/runs/(?P<run_id>\d+)/timer/$', consumers.TimerConsumer.as_asgi()),
    re_path(r'ws/overlay/runs/(?P<run_id>\d+)/timer/$', consumers.OverlayTimerConsumer.as_asgi()),
]
