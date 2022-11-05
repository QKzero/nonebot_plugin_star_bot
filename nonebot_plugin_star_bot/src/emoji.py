import os
from pathlib import Path
import random
import traceback
from typing import Type

from nonebot import on_notice, on_message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, PokeNotifyEvent

from .. import config, rules

emoji_path = config.resource_mkdir + '/emoji'

pokeMe = on_notice(rule=rules.group_rule, priority=config.priority)


@pokeMe.handle()
async def _(event: PokeNotifyEvent) -> None:
    if event.is_tome():
        await send_emoji(pokeMe)


atMe = on_message(rule=rules.group_rule & rules.font_atme_rule, priority=config.priority)


@atMe.handle()
async def _(event: GroupMessageEvent) -> None:
    # # ensure message not empty
    # if not event.original_message or not event.original_message[0]:
    #     return

    # def _is_at_me_seg(segment: MessageSegment) -> None:
    #     return segment.type == "at" and str(segment.data.get("qq", "")) == str(event.self_id)

    # if _is_at_me_seg(event.original_message[0]):
    #     await send_emoji(atMe)
    await send_emoji(atMe)


async def send_emoji(matcher: Type[Matcher]) -> None:
    try:
        pool = [filepath + '/' + filename for filepath, _, filenames in os.walk(emoji_path) for filename in filenames]

        if len(pool) > 0:
            file_path = pool[random.randint(0, len(pool) - 1)]
            msg = MessageSegment.image(Path(file_path))
            await matcher.send(msg)

    except:
        await matcher.send('图片发送失败')
        logger.error('互动发生异常，此时发送的文件为：' + file_path + '\n回溯如下：\n' + traceback.format_exc())
