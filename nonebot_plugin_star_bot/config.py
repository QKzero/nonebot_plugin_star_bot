from nonebot import get_driver
from nonebot.log import logger

_config = get_driver().config.dict()

if 'star_group' not in _config:
    logger.warning('[star_bot] 未发现配置项 `star_group` , 采用默认值: []')

group_white_list = set(_config.get('star_group', []))

resource_mkdir = 'star_bot'

priority = 5
