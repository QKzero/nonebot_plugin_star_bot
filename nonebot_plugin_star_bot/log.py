import os
from nonebot.log import logger as _logger

logger = _logger

logger.add(os.path.split(os.path.realpath(__file__))[0] + '/logs/{time:YYYY-MM-DD}.log', level='ERROR', rotation='0:00')

@logger.catch
def index_error(custom_list: list):

    for index in range(len(custom_list)):
        index_value = custom_list[index]
        if custom_list[index] < 2 :
            custom_list.remove(index_value)

        print(index_value)