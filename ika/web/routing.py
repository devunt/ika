from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from . import consumers

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        url(r'^ws$', consumers.MessageConsumer),
    ]),
})
