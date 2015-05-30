from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import sessionmaker

from ika.conf import settings


Base = declarative_base()


class Nick(Base):
    __tablename__ = 'nick'
    id = Column('nick_id', Integer, primary_key=True)
    name = Column('nick_name', String(32), unique=True)
    last_use = Column('nick_last_use', DateTime)
    user_id = Column(Integer, ForeignKey('user.user_id'))


class User(Base):
    __tablename__ = 'user'
    id = Column('user_id', Integer, primary_key=True)
    email = Column('user_email', String(255), unique=True)
    name = relationship('Nick', uselist=False, backref='user')
    aliases = relationship('Nick', backref='user_alias')
    password = Column('user_password', String(60))
    last_login = Column('user_last_login', DateTime)


engine = create_engine(settings.database)
Session = sessionmaker(bind=engine)
