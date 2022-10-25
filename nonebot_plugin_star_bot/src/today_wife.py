import datetime
import json
import os
import random
import traceback
from typing import Dict, List

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment

from .. import config, rules

def _get_data_path():
    data_mkdir_path = os.path.split(os.path.realpath(__file__))[0] + '/../logs/today_wife/'
    data_file_path = data_mkdir_path + str(datetime.date.today()) + '.json'
    if not os.path.exists(data_mkdir_path):
        os.mkdir(data_mkdir_path)
    return data_file_path

if os.path.isfile(_get_data_path()):
    with open(file=_get_data_path(), mode='r') as file:
        today_wife_data = json.load(file)
else:
    today_wife_data = {}

class _WifeEventData:
    def __init__(self, user_id: int, group_id: int, member_list: list) -> None:
        self.user_id = user_id
        self.group_id = group_id
        self.member_list = member_list

today_wife = on_command('star wife', rule=rules.standerd_rule, aliases={'今日老婆'}, block=True, priority=config.priority)

@today_wife.handle()
async def _(bot: Bot, event: GroupMessageEvent) -> None:
    global today_wife_data

    try:
        user_id = event.user_id
        group_id = event.group_id
        member_list = await bot.get_group_member_list(group_id=group_id)
        member_list = [member['user_id'] for member in member_list]
        wife_event_data = _WifeEventData(user_id=user_id, group_id=group_id, member_list=member_list)

        if 'date' not in today_wife_data or today_wife_data['date'] != str(datetime.date.today()):
            today_wife_data = {}
            today_wife_data['date'] = str(datetime.date.today())

        if str(group_id) not in today_wife_data:
            spouses = shuffle_wife(bot=bot, member_list=member_list)
            today_wife_data[str(group_id)] = spouses
            save_wife_data()
        else:
            spouses = today_wife_data[str(group_id)]

        if str(user_id) in spouses:
            if spouses[str(user_id)] != 'singleton':
                await send_wife(matcher=today_wife, bot=bot, wife_id=int(spouses[str(user_id)]), wife_event_data=wife_event_data)
            else:
                await today_wife.send(singleton_message(user_id=user_id))
        else:
            await today_wife.send(no_wife_message(user_id=user_id))

    except:
        await today_wife.send('发生异常，请联系管理员')
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())


def save_wife_data() -> None:
    with open(_get_data_path(), mode='w') as file:
        json.dump(today_wife_data, file, skipkeys=True, indent=4)


def shuffle_wife(bot: Bot, member_list: List[int]) -> Dict:
    bot_id = int(bot.self_id)

    pool = [i for i in member_list]
    pool.remove(bot_id)
    random.shuffle(pool)

    spouses = {}

    if len(pool) >= 2:
        for i in range(1, len(pool), 2):
            spouses[str(pool[i])] = str(pool[i - 1])
            spouses[str(pool[i - 1])] = str(pool[i])
    spouses[str(pool[len(pool) - 1])] = 'singleton'

    return spouses

async def send_wife(matcher: Matcher, bot: Bot, wife_id: int , wife_event_data: _WifeEventData):
    if not wife_event_data.user_id or not wife_event_data.group_id or not wife_event_data.member_list:
        return

    user_id = wife_event_data.user_id
    group_id = wife_event_data.group_id
    member_list = wife_event_data.member_list

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
        msg.append('{0}({1})'.format((await bot.get_group_member_info(group_id=group_id, user_id=wife_id))['nickname'], wife_id))
        await matcher.send(msg)

def no_wife_message(user_id: int) -> Message:
    msg = Message()
    msg.append(MessageSegment.at(user_id=user_id))
    msg.append('今天老婆已经抽完啦，明天再来吧~')
    return msg

def singleton_message(user_id: int) -> Message:
    msg = Message()
    msg.append(MessageSegment.at(user_id=user_id))
    msg.append('今天的你没有老婆呢，那个，如果不嫌弃星夜酱的话？')
    return msg