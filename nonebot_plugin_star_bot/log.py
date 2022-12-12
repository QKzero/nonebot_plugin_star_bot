from nonebot.log import logger

from . import config

logger.add(config.resource_mkdir / 'logs' / 'INFO' / '{time:YYYY-MM-DD}.log', level='INFO', rotation='0:00')
logger.add(config.resource_mkdir / 'logs' / 'WARNING' / '{time:YYYY-MM-DD}.log', level='WARNING', rotation='0:00')
logger.add(config.resource_mkdir / 'logs' / 'ERROR' / '{time:YYYY-MM-DD}.log', level='ERROR', rotation='0:00')
