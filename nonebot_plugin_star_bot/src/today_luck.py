import json
import math
import os
import pathlib
import random
import sqlite3
import traceback
from typing import Type

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent

from . import util
from .. import config, rules

today_luck = on_command('star luck', rule=rules.group_rule, aliases={'今日运势'}, block=True,
                        priority=config.lowest_priority)


@today_luck.handle()
async def _(event: GroupMessageEvent) -> None:
    try:
        conn = sqlite3.connect(config.database_path)

        try:
            user_id = event.user_id
            group_id = event.group_id

            _check_database_table(conn)

            cursor = conn.execute('select luck_param from today_luck '
                                  'where user_id={0} and group_id={1} and date_time="{2}"'
                                  .format(user_id, group_id, util.get_wife_date()))
            record = [i[0] for i in cursor.fetchall()]

            if len(record) == 0:
                luck_param = random.randint(0, 100)

                conn.execute(
                    'insert into today_luck(user_id, group_id, luck_param, date_time) '
                    'VALUES ({0}, {1}, {2}, "{3}")'.format(user_id, group_id, luck_param, util.get_wife_date()))
                conn.commit()
            else:
                luck_param = record[0]

                await util.wife_date_remind(matcher=today_luck)

            await _send_luck(today_luck, user_id, luck_param)

        except:
            raise

    except:
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())


def _draw_luck(luck_param: int) -> str:
    file_path = pathlib.Path(os.path.dirname(__file__)) / '..' / 'res' / 'luck_sentence.json'
    with open(file_path, mode='r', encoding='utf-8') as file:
        luck_sentence = json.load(file)

        luck_option = tuple(luck_sentence.keys())
        luck_result = luck_option[math.floor(len(luck_option) * luck_param * 0.01)]  # 百分比向下取整

        luck_text = '你今日的运势是「' + luck_result + '」'
        luck_text += luck_sentence[luck_result][random.randint(0, len(luck_sentence[luck_result]) - 1)]

        return luck_text


async def _send_luck(matcher: Type[Matcher], user_id: int, luck_param: int) -> None:
    msg = Message()
    msg.append(MessageSegment.at(user_id))
    msg.append('\n')
    msg.append('运势指数(0-100)：{0}'.format(luck_param))
    msg.append('\n')
    msg.append(_draw_luck(luck_param))
    await matcher.send(msg)


def _check_database_table(conn: sqlite3.Connection) -> None:
    sql = 'create table if not exists today_luck (' \
          'user_id integer(10) not null,' \
          'group_id integer(10) not null ,' \
          'luck_param integer(4) not null ,' \
          'date_time date not null);'
    conn.execute(sql)

    sql = 'create unique index if not exists today_luck_index on today_luck(user_id, group_id, date_time);'
    conn.execute(sql)

    conn.commit()
