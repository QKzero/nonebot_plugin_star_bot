import os
from nonebot.log import logger as _logger

from . import config

logger = _logger

logger.add(config.resource_mkdir / 'logs' / '{time:YYYY-MM-DD}.log', level='WARNING', rotation='0:00')


@logger.catch
def index_error(custom_list: list):
    for index in range(len(custom_list)):
        index_value = custom_list[index]
        if custom_list[index] < 2:
            custom_list.remove(index_value)

        print(index_value)
