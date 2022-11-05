import datetime
import json
import os
import random
import traceback
from typing import Type

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment

from .. import config, rules


def _get_data_date() -> datetime.date:
    _datetime = datetime.datetime.today()
    date = _datetime.date()
    hour = _datetime.time().hour
    if hour <= 6:
        return date - datetime.timedelta(days=1)
    else:
        return date


def _get_data_path() -> str:
    data_mkdir_path = config.resource_mkdir + '/logs/today_wife/'
    data_file_path = data_mkdir_path + str(_get_data_date()) + '.json'
    if not os.path.exists(data_mkdir_path):
        os.mkdir(data_mkdir_path)
    return data_file_path


if os.path.isfile(_get_data_path()):
    with open(file=_get_data_path(), mode='r') as file:
        today_wife_data = json.load(file)
else:
    today_wife_data = {}

today_wife = on_command('star wife', rule=rules.group_rule, aliases={'今日老婆'}, block=True, priority=config.priority)


@today_wife.handle()
async def _(bot: Bot, event: GroupMessageEvent) -> None:
    global today_wife_data

    try:
        bot_id = int(bot.self_id)
        user_id = event.user_id
        group_id = event.group_id
        member_list = await bot.get_group_member_list(group_id=group_id)
        member_list = [member['user_id'] for member in member_list]

        if 'date' not in today_wife_data or today_wife_data['date'] != str(_get_data_date()):
            today_wife_data = {'date': str(_get_data_date())}

        if str(group_id) not in today_wife_data:
            today_wife_data[str(group_id)] = {}
        group_spouses = today_wife_data[str(group_id)]

        if str(user_id) not in group_spouses:
            wife_id = draw_wife(bot_id=bot_id, user_id=user_id, group_spouses=group_spouses, member_list=member_list)
            if wife_id == -1:
                await today_wife.send(no_wife_message(user_id=user_id))
            else:
                group_spouses[str(user_id)] = str(wife_id)
                group_spouses[str(wife_id)] = str(user_id)
                save_wife_data()
                await send_wife(matcher=today_wife, bot=bot, user_id=user_id, wife_id=wife_id, group_id=group_id,
                                member_list=member_list)
        else:
            wife_id = int(group_spouses[str(user_id)])
            await send_wife(matcher=today_wife, bot=bot, user_id=user_id, wife_id=wife_id, group_id=group_id,
                            member_list=member_list)

    except:
        await today_wife.send('发生异常，请联系管理员')
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())


def save_wife_data() -> None:
    with open(_get_data_path(), mode='w') as file:
        json.dump(today_wife_data, file, skipkeys=True, indent=4)


def draw_wife(bot_id: int, user_id: int, group_spouses: dict[str: str], member_list: list[int]) -> int:
    pool = []
    for member_id in member_list:
        if str(member_id) not in group_spouses and member_id != user_id and member_id != bot_id:
            pool.append(member_id)

    if len(pool) > 0:
        wife_id = pool[random.randint(0, len(pool) - 1)]
        return wife_id
    else:
        return -1


async def send_wife(matcher: Type[Matcher], bot: Bot, user_id: int, wife_id: int, group_id: int,
                    member_list: list[int]) -> None:
    if wife_id not in member_list:
        msg = Message()
        msg.append(MessageSegment.at(user_id=user_id))
        msg.append('你的老婆神隐了哦（')
        await matcher.send(msg)
    else:
        msg = Message()
        msg.append(MessageSegment.at(user_id=user_id))
        msg.append('你今日的老婆是\n')
        # msg.append(MessageSegment.image('https://q.qlogo.cn/headimg_dl?dst_uin={0}&spec=640&img_type=jpg'.format(wife_id)))
        msg.append(MessageSegment.image('http://q1.qlogo.cn/g?b=qq&nk={0}&s=640'.format(wife_id)))
        msg.append('{0}({1})'.format((await bot.get_group_member_info(group_id=group_id, user_id=wife_id))['nickname'],
                                     wife_id))
        await matcher.send(msg)


def no_wife_message(user_id: int) -> Message:
    msg = Message()
    msg.append(MessageSegment.at(user_id=user_id))
    msg.append('今天老婆已经抽完啦，明天再来吧~')
    return msg
