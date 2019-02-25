from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from . import controllers

urlpatterns = [
    url(r'^message$', controllers.MessageView.as_view()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        url(r'^ws$', controllers.MessageConsumer),
    ]),
})

