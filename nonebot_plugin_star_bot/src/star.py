from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent

from .. import config, rules

# descriptions = {
#     '帮助': ['-h', '--help'],
#     '桃花岛数据分析': ['-a', '--analyse'],
#     '今日老婆': ['-w', '--wife'],
# }

# commends = {cmd: des for des, cmdList in descriptions.items() for cmd in cmdList}

# help = on_command('star help', rule=rules.standerd_rule, block=True, priority=config.priority)

# @help.handle()
# async def _() -> None:
#     msg = '这里是星夜酱的使用方式：\n'
#     for key, value in config.descriptions.items():
#         msg += '/star '
#         for cmd in value:
#             msg += cmd + ','
#         msg = msg[:-1]
#         msg += ' ' + key + '\n'
#     msg = msg[:-1]

#     await help.finish(msg)

star = on_command('star', rule=rules.standerd_rule, block=True, priority=config.priority + 1)

@star.handle()
async def _(event: GroupMessageEvent) -> None:
    msg = Message()
    msg.append(MessageSegment.at(event.user_id))
    msg.append('这里是星夜酱哦，请愉悦地使用咱吧~')

    await star.finish(msg)