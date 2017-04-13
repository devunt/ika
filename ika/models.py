import re
from django.db import models
from django.contrib.auth.hashers import check_password, make_password

from ika.enums import Flags


class Account(models.Model):
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=128)
    vhost = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    authenticated_on = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f'<Account {self.name} ({self.email})>'

    @property
    def name(self):
        return self.nicknames.get(is_account_name=True).name

    @property
    def aliases(self):
        return [nickname.name for nickname in self.nicknames.filter(is_account_name=False).all()]

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        def setter(_raw_password):
            self.set_password(_raw_password)
            self.save(update_fields=['password'])
        return check_password(raw_password, self.password, setter)

    @classmethod
    def get(cls, name) -> 'Account':
        nickname = Nickname.get(name)
        return nickname and nickname.account


class Nickname(models.Model):
    name = models.CharField(max_length=32, unique=True)
    account = models.ForeignKey(Account, related_name='nicknames')
    is_account_name = models.BooleanField(default=False)

    def __repr__(self):
        return f'<Nickname {self.name} ({self.account})>'

    @classmethod
    def get(cls, name) -> 'Nickname':
        return cls.objects.filter(name__iexact=name).first()


class Channel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f'<Channel {self.name}>'

    def get_flags_by_user(self, irc_user):
        types = 0
        for flag in self.flags.all():
            if flag.match(irc_user):
                types |= flag.type
        return Flags(types)

    @classmethod
    def get(cls, name) -> 'Channel':
        return cls.objects.filter(name__iexact=name).first()


class Flag(models.Model):
    channel = models.ForeignKey(Channel, related_name='flags')
    target = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField()
    updated_on = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f'<Flag {self.channel} - {self.target} - {Flags(self.type)}>'

    def match(self, irc_user):
        if ('!' not in self.target) or ('@' not in self.target):
            if irc_user.account:
                return irc_user.account.name == self.target
            else:
                return False
        pattern = re.escape(self.target)
        pattern = pattern.replace('\*', '.+?')
        pattern = '^{}$'.format(pattern)
        return re.match(pattern, irc_user.mask, re.IGNORECASE) is not None

    @classmethod
    def get(cls, channel, target) -> 'Flag':
        return cls.objects.filter(channel=channel, target__iexact=target).first()

    class Meta:
        unique_together = ('channel', 'target')
