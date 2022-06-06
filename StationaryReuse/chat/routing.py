from django.urls import path
from . import consumer

# Here, we are saying that whatever websocket is working on the given URL we need to connect it to the chat consumer.
websocket_urlpatterns = [
    path('chat/', consumer.ChatConsumer.as_asgi()),
    path('chat/<int:received_id>/', consumer.ChatConsumer.as_asgi()),
]