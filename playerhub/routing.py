from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/runs/(?P<run_id>\d+)/$', consumers.RunConsumer.as_asgi()),
]