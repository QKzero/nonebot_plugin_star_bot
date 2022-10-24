from nonebot import get_driver
from nonebot.log import logger

_config = get_driver().config.dict()

if 'group_white_list' not in _config:
    logger.warning('[star_bot] 未发现配置项 `group_white_list` , 采用默认值: []')

group_white_list = set(_config.get('group_white_list', []))

priority = 5