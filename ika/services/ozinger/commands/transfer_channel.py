from ika.service import Command, Permission
from ika.models import Account, Channel, Flag
from ika.enums import Flags


class TransferChannel(Command):
    name = '채널소유권이전'
    aliases = (
        'TRANSFERCHANNEL',
    )
    syntax = '<#채널명> <계정명> <YES>'
    regex = r'(?P<cname>#\S+) (?P<target>\S+) (?P<confirmed>YES)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널의 소유권을 이전합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널의 \x02소유권을 이전\x02합니다.',
        '소유권 이전시 해당 채널에서 가지고 있던 권한 중 \x02F\x02 권한이 이전 받을 계정으로 이동하게 됩니다.',
        '채널 소유권 이전은 해당 채널에 \x02F\x02 (개설자) 권한이 있는 사용자만 할 수 있습니다.',
        '또한 이전 받을 계정으로 로그인 되어있는 유저가 \x02현재 해당 채널에 접속\x02해 있어야 합니다.',
        '실수로 명령을 실행하는 것을 방지하기 위해 명령 맨 뒤에 \x02YES\x02 를 붙여야 합니다.',
    )

    async def execute(self, user, cname, target, confirmed):
        if confirmed != 'YES':
            return

        channel = Channel.get(cname)
        if (not channel) or (Flags.FOUNDER not in channel.get_flags_by_user(user)):
            self.err(user, f'해당 채널 \x02{cname}\x02 의 \x02{user.nick}\x02 유저에 \x02F\x02 (개설자) 권한이 없습니다.')

        irc_channel = self.server.channels.get(cname)
        account = Account.get(target)
        if account and irc_channel:
            for irc_user in irc_channel.users.values():
                if irc_user.account == account:
                    target = irc_user.account
                    break
        if not isinstance(target, Account):
            self.err(user, f'\x02{channel}\x02 채널에 \x02{target}\x02 계정으로 로그인중인 유저가 존재하지 않습니다.')

        old_flag = Flag.get(channel, user.account)
        old_flag.flags &= ~Flags.FOUNDER
        old_flag.save()

        new_flag = Flag.get(channel, target)
        if new_flag is None:
            new_flag = Flag(channel=channel, type=0)
            new_flag.target = target

        new_flag.flags |= Flags.FOUNDER
        new_flag.save()

        self.msg(user, f'해당 채널 \x02{channel}\x02 의 소유권이 {target} 계정으로 이전되었습니다.')
        old_modestring = irc_channel.generate_synchronizing_modestring(account=user.account)
        new_modestring = irc_channel.generate_synchronizing_modestring(account=target)
        if old_modestring:
            self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, old_modestring)
        if new_modestring:
            self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, new_modestring)
