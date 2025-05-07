from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/runs/(?P<run_id>\d+)/$', consumers.WipecounterConsumer.as_asgi()),
    re_path(r'ws/overlay/runs/(?P<run_id>\d+)/$', consumers.OverlayConsumer.as_asgi()),
]
