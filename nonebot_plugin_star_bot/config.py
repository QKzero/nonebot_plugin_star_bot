from pathlib import Path

from nonebot import get_driver
from nonebot.log import logger

# 全局配置项
_config = get_driver().config.dict()

super_users = _config.get('superusers', [])
super_users = {int(i) for i in super_users}

if 'star_group' not in _config:
    logger.warning('[star_bot] 未发现配置项 `star_group` , 采用默认值: []')

group_white_list = set(_config.get('star_group', []))

# 资源路径
resource_mkdir = Path('star_bot')
database_path = resource_mkdir / 'star.sqlite'

# 事件优先级
normal_priority = 5
lowest_priority = 6
