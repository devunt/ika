from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, validates
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import PasswordType

from ika.conf import settings


Base = declarative_base()


class Nick(Base):
    __tablename__ = 'nick'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship('Account', foreign_keys='Nick.account_id', backref=backref('name', uselist=False))
    account_alias_id = Column(Integer, ForeignKey('account.id'))
    account_alias = relationship('Account', foreign_keys='Nick.account_alias_id', backref='aliases')
    last_use = Column(DateTime)


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(PasswordType(max_length=128,
        schemes=['bcrypt_sha256', 'md5_crypt'], deprecated=['md5_crypt']))
    last_login = Column(DateTime)

    @validates('email')
    def validate_email(self, key, value):
        assert '@' in value
        return value


engine = create_engine(settings.database)
Session = sessionmaker(bind=engine)
