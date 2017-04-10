import re
from django.db import models
from django.contrib.auth.hashers import check_password, make_password


class Account(models.Model):
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=128)
    vhost = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def name(self):
        return self.nicknames.get(is_account_name=True).name

    @property
    def aliases(self):
        return [nickname.name for nickname in self.nicknames.filter(is_account_name=False)]

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        def setter(_raw_password):
            self.set_password(_raw_password)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    @classmethod
    def get(cls, name) -> 'Account':
        nickname = Nickname.get(name)
        return nickname and nickname.account


class Nickname(models.Model):
    name = models.CharField(max_length=32, unique=True)
    account = models.ForeignKey(Account, related_name='nicknames')
    is_account_name = models.BooleanField(default=False)

    @classmethod
    def get(cls, name) -> 'Nickname':
        return cls.objects.filter(name__iexact=name).first()


class Channel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # data = models.Fie(JSONType, default=dict())
    created_on = models.DateTimeField(auto_now_add=True)

    def get_flags_by_user(self, user):
        types = 0
        for flag in self.flags:
            if flag.match_mask(user.mask) or (user.account and (flag.target.lower() == user.account.name.name.lower())):
                types |= flag.type
        return types

    @classmethod
    def get(cls, name) -> 'Channel':
        return cls.objects.filter(name__iexact=name).first()


class Flag(models.Model):
    channel = models.ForeignKey(Channel, related_name='flags')
    target = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField()
    created_on = models.DateTimeField(auto_now=True)

    def match_mask(self, mask):
        if ('!' not in self.target) or ('@' not in self.target):
            return False
        pattern = re.escape(self.target)
        pattern = pattern.replace('\*', '.+?')
        pattern = '^{}$'.format(pattern)
        return re.match(pattern, mask, re.IGNORECASE) is not None
