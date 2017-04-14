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
    target_account = models.ForeignKey(Account, related_name='channel_flags', null=True, blank=True)
    target_mask = models.CharField(max_length=255, null=True, blank=True)
    type = models.PositiveSmallIntegerField()
    updated_on = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f'<Flag {self.channel} - {self.target} - {Flags(self.type)}>'

    @property
    def target(self):
        if self.target_account:
            return self.target_account.name
        else:
            return self.target_mask

    @target.setter
    def target(self, value):
        if isinstance(value, Account):
            self.target_account = value
        else:
            self.target_mask = value

    def match(self, irc_user):
        if self.target_account:
            return self.target_account == irc_user.account
        else:
            pattern = re.escape(self.target_mask)
            pattern = pattern.replace('\*', '.+?')
            pattern = '^{}$'.format(pattern)
            return re.match(pattern, irc_user.mask, re.IGNORECASE) is not None

    def save(self, *args, **kwargs):
        if (self.target_account and self.target_mask) or (not self.target_account and not self.target_mask):
            raise ValueError('Exactly one of [Flag.target_acount, Flag.target_mask] must be set')
        super().save(*args, **kwargs)

    @classmethod
    def get(cls, channel, target) -> 'Flag':
        if isinstance(target, Account):
            return cls.objects.filter(channel=channel, target_account=target).first()
        else:
            return cls.objects.filter(channel=channel, target_mask__iexact=target).first()

    @classmethod
    def create(cls, channel, target) -> 'Flag':
        flag = cls(channel=channel)
        if isinstance(target, Account):
            flag.target_account = target
        else:
            flag.target_mask = target
        return flag

    class Meta:
        unique_together = ('channel', 'target_account', 'target_mask')
