import re
import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.views.generic import View
from django.http.response import JsonResponse

from ..models import Application, Channel


RE_NICK = re.compile(r'^[A-Za-z0-9가-힣_]{1,16}$')
channel_layer = get_channel_layer()


class MessageView(View):
    def post(self, request):
        body = json.load(request)
        token = request.META.get('HTTP_X_OZ_TOKEN') or body.get('token')

        app = Application.get_by_token(token)
        return JsonResponse({'code': handle_message_action(app, body)})


class MessageConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = None
        self.channels = []

    async def connect(self):
        await self.channel_layer.group_add('ika', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('ika', self.channel_name)

    async def receive_json(self, content):
        action = content.get('action')
        if action == 'authenticate':
            if self.app:
                await self.respond('invalid_payload', d='already authenticated')
                return

            token = content.get('token')
            if not token:
                await self.respond('invalid_payload', d='no token was provided')
                return

            self.app = await database_sync_to_async(Application.get_by_token)(token)
            if not self.app:
                await self.respond('invalid_token')
                return

            self.channels = [channel.name.lower() for channel in await database_sync_to_async(self.app.channels.all)()]
            await self.respond('authenticated', name=self.app.name, slug=self.app.slug, channels=self.channels)

        elif action == 'message':
            await self.respond(await database_sync_to_async(handle_message_action)(self.app, content))

        else:
            await self.respond('invalid_payload', d='invalid action')
            return

    async def ika_message(self, event):
        if not event['target'].startswith('#'):
            return

        if event['target'].lower() not in self.channels:
            return

        if event['origin'] == self.app.slug:
            return

        await self.respond(
            code='message',
            origin=event['origin'],
            sender=event['sender'],
            target=event['target'],
            message=event['message'],
        )

    async def respond(self, code, **extra):
        await self.send_json(dict(code=code, **extra))


def handle_message_action(app, payload):
    if not app:
        return 'invalid_token'

    sender = payload.get('sender')
    target = payload.get('target')
    message = payload.get('message')

    if not sender or not target or not message or ' ' in sender or ' ' in target:
        return 'invalid_payload'

    if not RE_NICK.match(sender):
        return 'invalid_payload'

    if target.startswith('#'):
        channel = Channel.get(target)
        if not channel or not app.channels.filter(pk=channel.pk).exists():
            return 'unauthorized_channel'

        async_to_sync(channel_layer.group_send)('ika', {
            'type': 'ika.message',
            'origin': app.slug,
            'sender': sender,
            'target': channel.name,
            'message': message,
        })
    else:
        return 'invalid_target'

    mask = f'{sender}+!{app.slug}@{app.slug}.apps.api.ozinger.org'

    async_to_sync(channel_layer.send)('ika_reverse', {
        'type': 'ika.reversed_message',
        'sender': mask,
        'target': target,
        'message': message,
    })

    return 'sent'
