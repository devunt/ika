import asyncio
import aiohttp
import json
from aiohttp import web
from ika.service import Listener
from ika.conf import settings
from ika.models import Application, Channel


class Webhook(Listener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wss = list()

        self.app = web.Application()
        self.app.add_routes([
            web.get('/ws', self.__handle_ws_request),
            web.post('/message', self.__handle_message_request),
        ])

        if not hasattr(self.service, 'webhook_lock'):
            self.service.webhook_lock = asyncio.Lock()

        asyncio.ensure_future(self.__run_webapp())

    def __uninit__(self):
        asyncio.ensure_future(self.__shutdown_webapp())

    async def __run_webapp(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, settings.webhook.host, settings.webhook.port)
        await site.start()

    async def __shutdown_webapp(self):
        for _, ws in self.wss:
            await ws.close()
        if hasattr(self, 'runner'):
            await self.runner.cleanup()
        await asyncio.sleep(1)
        if self.service.webhook_lock.locked():
            self.service.webhook_lock.release()

    async def __handle_ws_request(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        token = None

        async for message in ws:
            if message.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(message.data)
                except json.JSONDecodeError:
                    await ws.send_json({'type': 'invalid_payload'})
                else:
                    action = data.get('type')
                    if action == 'auth':
                        token = data.get('token')
                        if token:
                            app = Application.get_by_token(str(token))
                            if app:
                                await ws.send_json({'type': 'authed', 'name': app.name, 'slug': app.slug})
                                self.wss.append((app.id, ws))
                            else:
                                return {'type': 'invalid_token'}
                        else:
                            await ws.send_json({'type': 'invalid_payload'})
                    elif action == 'message':
                        await ws.send_json(await self.__handle_payload(token, data))
                    else:
                        await ws.send_json({'type': 'invalid_payload'})

        for entry in self.wss:
            if ws == entry[1]:
                self.wss.remove(entry)

        return ws

    async def __handle_message_request(self, request):
        token = request.headers.get('X-OZ-TOKEN')
        data = await request.json()

        return web.json_response(await self.__handle_payload(token, data))

    async def __handle_payload(self, token, payload):
        app = Application.get_by_token(str(token))

        if not app:
            return {'type': 'invalid_token'}

        nick = payload.get('nick')
        target = payload.get('target')
        text = payload.get('text')

        if not nick or not target or not text or ' ' in nick or ' ' in target:
            return {'type': 'invalid_payload'}

        if target.startswith('#'):
            channel = Channel.get(target)
            if not channel or not app.channels.filter(pk=channel.pk).exists():
                return {'type': 'unauthorized_channel'}
        else:
            return {'type': 'invalid_target'}

        await self.__send_fakemsg(nick, app.slug, target, payload['text'])
        return {'type': 'sent'}

    async def __send_fakemsg(self, nick, slug, target, text):
        mask = f'{nick}+{slug}!{slug}@{slug}.api.ozinger.org'
        self.writesvsuserline(f'FAKEMSG {mask} {target} {text}')

    async def privmsg(self, uid, target_uid_or_cname, message):
        if not target_uid_or_cname.startswith('#'):
            return

        channel = Channel.get(target_uid_or_cname)
        if not channel:
            return

        for app in channel.apps.all():
            for _id, ws in self.wss:
                if _id == app.id:
                    await ws.send_json({
                        'type': 'message',
                        'nick': uid,
                        'target': target_uid_or_cname,
                        'text': message,
                    })
