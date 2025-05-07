"""
ASGI config for wiperino project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiperino.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from playerhub.middleware import JWTAuthMiddlewareStack
from django.core.asgi import get_asgi_application
import playerhub.routing



application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            playerhub.routing.websocket_urlpatterns
        )
    ),
})