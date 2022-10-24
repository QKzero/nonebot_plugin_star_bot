import datetime
import json
from operator import le
import os
from pathlib import Path
import random
import traceback
from typing import Dict, List

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment

from star_bot import config, rules

resource_path = os.path.split(os.path.realpath(__file__))[0] + '/../res/touhou_wife/'
picture_path = resource_path + 'picture/'
def _get_data_path():
    data_mkdir_path = resource_path + 'wife_log/'
    data_file_path = data_mkdir_path + str(datetime.date.today()) + '.json'
    if not os.path.exists(data_mkdir_path):
        os.mkdir(data_mkdir_path)
    return data_file_path

if not os.path.exists(resource_path):
    os.mkdir(resource_path)

if os.path.isfile(_get_data_path()):
    with open(file=_get_data_path(), mode='r') as file:
        touhou_wife_data = json.load(file)
else:
    touhou_wife_data = {}

touhou_wife = on_command('star touhou', rule=rules.standerd_rule, aliases={'车万老婆', '东方老婆'}, block=True, priority=config.priority)

@touhou_wife.handle()
async def _(bot: Bot, event: GroupMessageEvent) -> None:
    global touhou_wife_data
    
    try:
        user_id = event.user_id
        group_id = event.group_id
        member_list = await bot.get_group_member_list(group_id=group_id)
        member_list = [member['user_id'] for member in member_list]

        if 'date' not in touhou_wife_data or touhou_wife_data['date'] != str(datetime.date.today()):
            touhou_wife_data = {}
            touhou_wife_data['date'] = str(datetime.date.today())

        if str(group_id) not in touhou_wife_data:
            spouses = shuffle_wife(bot=bot, member_list=member_list)
            touhou_wife_data[str(group_id)] = spouses
            save_wife_data()
        else:
            spouses = touhou_wife_data[str(group_id)]

        if str(user_id) in spouses:
            if spouses[str(user_id)] != 'singleton':
                await send_wife(matcher=touhou_wife, bot=bot, user_id=user_id, wife_name=spouses[str(user_id)])
            else:
                await touhou_wife.send(singleton_message(user_id=user_id))
        else:
            await touhou_wife.send(no_wife_message(user_id=user_id))

    except:
        await touhou_wife.send('发生异常，请联系管理员')
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())


def save_wife_data() -> None:
    with open(_get_data_path(), mode='w') as file:
        json.dump(touhou_wife_data, file, skipkeys=True, indent=4)


def shuffle_wife(bot: Bot, member_list: List[int]) -> Dict[str, str]:
    # bot_id = bot.self_id

    pool = os.listdir(picture_path)
    pool = [i.split('.')[0] for i in pool]
    
    random.shuffle(member_list)
    random.shuffle(pool)

    spouses = {}

    if len(member_list) <= len(pool):
        for i in range(len(member_list)):
            spouses[str(member_list[i])] = str(pool[i])
    else:
        for i in range(len(pool)):
            spouses[str(member_list[i])] = str(pool[i])
        for i in range(len(pool), len(member_list)):
            spouses[str(member_list[i])] = 'singleton'


    return spouses

async def send_wife(matcher: Matcher, bot: Bot, user_id: int, wife_name: str):
    try:
        file_path = Path(picture_path + wife_name + '.png')

        msg = Message()
        msg.append(MessageSegment.at(user_id=user_id))
        msg.append('你今日的车万老婆是\n')
        msg.append(MessageSegment.image(file_path))
        msg.append('「' + wife_name + '」')
        await matcher.send(msg)
    except:
        await matcher.send('发生异常，请联系管理员')
        logger.error('发生异常，此时发送的文件为：' + file_path + '\n回溯如下：\n' + traceback.format_exc())

def no_wife_message(user_id: int) -> Message:
    msg = Message()
    msg.append(MessageSegment.at(user_id=user_id))
    msg.append('老婆已经抽完啦，明天再来吧~')
    return msg

def singleton_message(user_id: int) -> Message:
    msg = Message()
    msg.append(MessageSegment.at(user_id=user_id))
    msg.append('今天没抽到老婆呢，明天再试试吧（')
    return msg