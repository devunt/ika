import re
import json

from django.views.generic import View
from django.http.response import JsonResponse

from ..models import Application, Channel


class MessageView(View):
    def post(self, request):
        token = request.META.get('HTTP_X_OZ_TOKEN')
        body = json.load(request)
        resp = handle_payload(token, body)
        return JsonResponse(resp)


RE_NICK = re.compile(r'^[A-Za-z0-9가-힣_]{1,16}$')

def handle_payload(token, payload):
    app = Application.get_by_token(str(token))

    if not app:
        return {'type': 'invalid_token'}

    nick = payload.get('nick')
    target = payload.get('target')
    text = payload.get('text')

    if not nick or not target or not text or ' ' in nick or ' ' in target:
        return {'type': 'invalid_payload'}

    if not RE_NICK.match(nick):
        return {'type': 'invalid_payload'}

    if target.startswith('#'):
        channel = Channel.get(target)
        if not channel or not app.channels.filter(pk=channel.pk).exists():
            return {'type': 'unauthorized_channel'}
        # await self.__on_channel_msg(channel, app.slug, nick, text)
    else:
        return {'type': 'invalid_target'}

    mask = f'{nick}+{app.slug}!{nick}+{app.slug}@{app.slug}-app.api.ozinger.org'
    print(f'FAKEMSG {mask} {target} {text}')

    return {'type': 'sent'}
