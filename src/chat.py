import os
from pathlib import Path
import random
import traceback

from nonebot import on_notice, on_message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, PokeNotifyEvent

from star_bot import config, rules

def _load_emoji_path(path: str) -> str:
    load_path = os.path.split(os.path.realpath(__file__))[0] + path
    if not os.path.exists(load_path):
        os.mkdir(load_path)
    return load_path

emoji_path = {
    '/../res/emoji/cat/',
    '/../res/emoji/pusheen/',
}
emoji_path = [_load_emoji_path(path=p) for p in emoji_path]

pokeMe = on_notice(rule=rules.standerd_rule, priority=config.priority)

@pokeMe.handle()
async def _(event: PokeNotifyEvent) -> None:
    if event.is_tome():
        await send_emoji(pokeMe)

atMe = on_message(rule=rules.standerd_rule & rules.font_atme_rule, priority=config.priority)

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

async def send_emoji(matcher: Matcher) -> None:
    try:
        pool = []
        for p in emoji_path:
            if os.path.exists(p) and len(os.listdir(p)) >= 0:
                pool.extend([p + f for f in os.listdir(p)])

        if len(pool) > 0:
            file_path = pool[random.randint(0, len(pool) - 1)]
            msg = MessageSegment.image(Path(file_path))
            await matcher.send(msg)
    
    except:
        await matcher.send('图片发送失败')
        logger.error('互动发生异常，此时发送的文件为：' + file_path + '\n回溯如下：\n' + traceback.format_exc())