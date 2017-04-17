import dns.resolver
from ika.service import Command, Permission
from hashlib import sha224


class ChangeVirtualHost(Command):
    name = '가상호스트변경'
    aliases = (
        '가상호스트',
        'VHOST',
        'CHANGEVHOST',
    )
    syntax = '[가상 호스트]'
    regex = r'(?P<vhost>\S*)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 계정의 가상 호스트를 설정하거나 삭제합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 이미 등록되어 있는 계정의 가상 호스트를 설정하거나 삭제할 수 있습니다.',
        '명령에 인자가 있을 시 해당 인자로 가상 호스트를 설정하며, 인자가 없을 시 계정의 가상 호스트를 삭제합니다.',
        '가상 호스트란 원래 유저의 호스트 부분 (IP 부분)을 사용자가 직접 설정한 가상 호스트 (도메인)로 대체하는 것으로,',
        '자신의 실제 IP를 숨김과 동시에 자신이 소유중인 도메인을 홍보할 수 있습니다.',
        '가상 호스트 설정은 해당 도메인에 TXT 레코드를 설정함으로써 가능하며, 설정해야 할 TXT 레코드는 본 명령을 실행해 확인할 수 있습니다.',
    )

    @staticmethod
    def gen_verification_code(domain):
        hashcode = sha224(domain.encode()).hexdigest()[:6]
        return f'ozinger-verification-code={hashcode}'

    async def execute(self, user, vhost):
        if user.account.vhost == vhost:
            self.err(user, '\x02{}\x02 계정의 가상 호스트가 이미 \x02{}\x02 입니다.', user.account, vhost or '(없음)')

        if vhost:
            code = self.gen_verification_code(vhost)
            found = False
            try:
                resolver = dns.resolver.Resolver()
                answers = resolver.query(vhost, dns.rdatatype.TXT, raise_on_no_answer=False)
            except dns.resolver.NXDOMAIN:
                pass
            else:
                for answer in answers:
                    for txt in answer.strings:
                        if txt.decode() == code:
                            found = True
                            break
            if not found:
                self.err(user, f'TXT 레코드를 찾을 수 없습니다. \x02{vhost}\x02 도메인의 TXT 레코드에 \x02{code}\x02 레코드를 추가하거나, 이미 추가하셨다면 잠시 후 다시 시도해주세요.')

        account = user.account
        account.vhost = vhost
        account.save()

        self.writesvsuserline('CHGHOST', user.uid, account.vhost or user.host)
        self.msg(user, '\x02{}\x02 계정의 가상 호스트가 \x02{}\x02 로 변경되었습니다. 이제 TXT 레코드를 지우셔도 괜찮습니다.', user.account, vhost or '(없음)')
