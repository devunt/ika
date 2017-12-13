from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from jsonfield import JSONField

from ika.enums import Flags


class Account(models.Model):
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=128)
    vhost = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    authenticated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

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
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='nicknames')
    is_account_name = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Nickname {self.name} ({self.account})>'

    @classmethod
    def get(cls, name) -> 'Nickname':
        return cls.objects.filter(name__iexact=name).first()


class Channel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    data = JSONField(default={})

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Channel {self.name}>'

    def get_flags_by_user(self, irc_user):
        flags = Flags(0)
        for flag in self.flags.all():
            if flag.match(irc_user):
                flags |= flag.flags
        return flags

    @classmethod
    def get(cls, name) -> 'Channel':
        return cls.objects.filter(name__iexact=name).first()


class Flag(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='flags')
    target_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='channel_flags', null=True)
    target_mask = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField()
    updated_on = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f'<Flag {self.channel} - {self.target} - {self.flags!r}>'

    __str__ = __repr__

    @property
    def flags(self):
        return Flags(self.type)

    @flags.setter
    def flags(self, value):
        self.type = value

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
            return irc_user.match_mask(self.target_mask)

    def save(self, *args, **kwargs):
        if (self.target_account and self.target_mask) or (not self.target_account and not self.target_mask):
            raise ValueError('Exactly one of [Flag.target_acount, Flag.target_mask] must be set')
        if self.flags:
            super().save(*args, **kwargs)
        else:
            self.delete()

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
