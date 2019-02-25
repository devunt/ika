from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from . import controllers

urlpatterns = [
    url(r'^chat$', controllers.MessageView.as_view()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        url(r'^chat$', controllers.MessageConsumer),
    ]),
})

