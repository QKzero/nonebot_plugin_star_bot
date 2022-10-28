import datetime
import json
import os
from pathlib import Path
import random
import traceback
from typing import Dict, List

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment

from .. import config, rules

picture_path = config.resource_mkdir + '/touhou_wife/' + 'picture/'
def _get_data_path():
    data_mkdir_path = config.resource_mkdir + '/logs/touhou_wife/'
    data_file_path = data_mkdir_path + str(datetime.date.today()) + '.json'
    if not os.path.exists(data_mkdir_path):
        os.mkdir(data_mkdir_path)
    return data_file_path

if not os.path.exists(picture_path):
    os.mkdir(picture_path)

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

        if 'date' not in touhou_wife_data or touhou_wife_data['date'] != str(datetime.date.today()):
            touhou_wife_data = {}
            touhou_wife_data['date'] = str(datetime.date.today())

        if str(group_id) not in touhou_wife_data:
            touhou_wife_data[str(group_id)] = {}
        group_spouses = touhou_wife_data[str(group_id)]

        if str(user_id) not in group_spouses:
            wife_name = draw_wife(group_spouses=group_spouses)
            
            if wife_name == '':
                await touhou_wife.send(no_wife_message(user_id=user_id))
            else:
                group_spouses[str(user_id)] = wife_name
                group_spouses[wife_name] = str(user_id)
                save_wife_data()
                await send_wife(matcher=touhou_wife, user_id=user_id, wife_name=wife_name)
        else:
            wife_name = group_spouses[str(user_id)]
            await send_wife(matcher=touhou_wife, user_id=user_id, wife_name=wife_name)

    except:
        await touhou_wife.send('发生异常，请联系管理员')
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())


def save_wife_data() -> None:
    with open(_get_data_path(), mode='w') as file:
        json.dump(touhou_wife_data, file, skipkeys=True, indent=4)

def draw_wife(group_spouses: dict[str: str]) -> str:
    pictures = os.listdir(picture_path)
    pictures = [i.split('.')[0] for i in pictures]
    pool = []
    for picture in pictures:
        if picture not in group_spouses:
            pool.append(picture)

    if len(pool) > 0:
        wife_name = pool[random.randint(0, len(pool) - 1)]
        return wife_name
    else:
        return ''

async def send_wife(matcher: Matcher, user_id: int, wife_name: str) -> None:
    try:
        pictures = os.listdir(picture_path)
        for p in pictures:
            if wife_name in p:
                file_path = Path(picture_path + p)
                break

        msg = Message()
        msg.append(MessageSegment.at(user_id=user_id))
        msg.append('你今日的车万老婆是\n')
        if file_path:
            msg.append(MessageSegment.image(file_path))
        msg.append('「' + wife_name + '」')
        await matcher.send(msg)
    except:
        await matcher.send('星夜坏掉啦，请帮忙叫主人吧')
        logger.error('发生异常，此时发送的文件为：' + file_path + '\n回溯如下：\n' + traceback.format_exc())

def no_wife_message(user_id: int) -> Message:
    msg = Message()
    msg.append(MessageSegment.at(user_id=user_id))
    msg.append('今天老婆已经抽完啦，明天再来吧~')
    return msg