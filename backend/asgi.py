"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.apps import apps
# from chatapp import routing


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# import django
# django.setup()

# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             # Define your routing here (websocket URLs)
#             routing.websocket_urlpatterns
#         )
#     ),
# })







import os
from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack   
from chatapp.middleware import JWTAuthMiddleware
import chatapp.routing



application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': JWTAuthMiddleware(
        URLRouter(
            chatapp.routing.websocket_urlpatterns
        )
    )
})