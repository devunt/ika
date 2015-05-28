import logging

from ika.conf import settings


logging.basicConfig(format='[%(asctime)s] {%(levelname)s} %(message)s')
logger = logging.getLogger('ika')
logger.setLevel(getattr(logging, settings.logging))
