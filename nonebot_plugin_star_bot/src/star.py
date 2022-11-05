from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent

from .. import config, rules

star = on_command('star', rule=rules.group_rule, block=True, priority=config.priority + 1)


@star.handle()
async def _(event: GroupMessageEvent) -> None:
    msg = Message()
    msg.append(MessageSegment.at(event.user_id))
    msg.append('这里是星夜酱哦，请愉悦地使用咱吧~')

    await star.send(msg)


star = on_command('star github', rule=rules.group_rule, block=True, priority=config.priority)


@star.handle()
async def _(event: GroupMessageEvent) -> None:
    msg = Message()
    msg.append('星夜酱身体的秘密都在这里了哦~\n')
    msg.append('https://github.com/QKzero/nonebot_plugin_star_bot')

    await star.send(msg)
