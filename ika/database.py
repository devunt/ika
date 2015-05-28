from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ika.conf import settings


Base = declarative_base()


# XXX: Create tables


engine = create_engine(settings.database)
Session = sessionmaker(bind=engine)
