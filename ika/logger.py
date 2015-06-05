import logging
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from ika.conf import settings


logging.basicConfig(format='[%(asctime)s] {%(levelname)s} %(message)s')

if settings.raven_dsn is not None:
    client = Client(dsn=settings.raven_dsn, auto_log_stacks=True)
    handler = SentryHandler(client)
    handler.setLevel(logging.WARNING)
    setup_logging(handler)

logger = logging.getLogger('ika')
logger.setLevel(getattr(logging, settings.logging))
