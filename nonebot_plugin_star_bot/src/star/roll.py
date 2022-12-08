import random
import traceback

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from nonebot_plugin_star_bot.nonebot_plugin_star_bot import config, rules
from nonebot_plugin_star_bot.nonebot_plugin_star_bot.log import logger

star_roll = on_command('star roll', rule=rules.group_rule, block=True, priority=config.normal_priority)


@star_roll.handle()
async def _(event: GroupMessageEvent) -> None:
    try:
        msg = event.get_message()

        if not msg or not msg[0]:
            log_content = '掷色子空过，'
            if not msg:
                log_content += '消息为空'
            elif not msg[0]:
                log_content += '首消息为空'
            logger.warning(log_content)
            return

        text = str(msg[0]).split(' ')
        a = 0
        b = 1
        if len(text) == 3 and text[2].isdigit():
            b = int(text[2])
        elif len(text) >= 4 and text[2].isdigit() and text[3].isdigit():
            a = int(text[2])
            b = int(text[3])
            if a > b:
                a, b = b, a

        await star_roll.send(
            '({0}-{1}): {2}'.format(a, b, random.randint(a, b))
        )


    except:
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())
