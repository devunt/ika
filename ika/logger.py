import logging


logging.basicConfig(format='[%(asctime)s] {%(levelname)s} %(message)s')
logger = logging.getLogger('ika')
logger.setLevel(logging.DEBUG)
