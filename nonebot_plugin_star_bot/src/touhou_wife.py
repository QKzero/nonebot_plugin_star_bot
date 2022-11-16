import datetime
import os
import sqlite3
import traceback
from typing import Type

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment

from . import util
from .. import config, rules

picture_path = config.resource_mkdir / 'touhou_wife' / 'picture'

touhou_wife = on_command('star touhou', rule=rules.group_rule, aliases={'车万老婆', '东方老婆'}, block=True,
                         priority=config.priority)


@touhou_wife.handle()
async def _(bot: Bot, event: GroupMessageEvent) -> None:
    try:
        conn = sqlite3.connect(config.database_path)
        try:
            user_id = event.user_id
            group_id = event.group_id

            _check_database_table(conn)

            cursor = conn.execute('select wife_name from touhou_wife '
                                  'where user_id={0} and group_id={1} and date_time="{2}"'
                                  .format(user_id, group_id, _get_date()))
            record = [i[0] for i in cursor.fetchall()]

            if len(record) == 0:
                wife_name = draw_wife(conn, group_id, user_id)

                if wife_name == '':
                    await touhou_wife.send(no_wife_message(user_id=user_id))
                else:
                    conn.execute('insert into touhou_wife(user_id, group_id, wife_name, date_time) values '
                                 '({0}, {1}, "{2}", "{3}")'.format(user_id, group_id, wife_name, _get_date()))
                    conn.commit()
                    await send_wife(matcher=touhou_wife, user_id=user_id, wife_name=wife_name)
            else:
                wife_name = record[0]
                await send_wife(matcher=touhou_wife, user_id=user_id, wife_name=wife_name)

        except:
            raise

        finally:
            conn.close()

    except:
        await touhou_wife.send('星夜坏掉啦，请帮忙叫主人吧')
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())


def _get_date() -> datetime.date:
    _datetime = datetime.datetime.today()
    date = _datetime.date()
    hour = _datetime.time().hour
    if 0 <= hour < 6:
        return date - datetime.timedelta(days=1)
    else:
        return date


def _check_database_table(conn: sqlite3.Connection) -> None:
    sql = 'create table if not exists touhou_wife (' \
          'user_id integer(10) primary key not null,' \
          'group_id integer(10) not null ,' \
          'wife_name text(20) not null ,' \
          'date_time date not null);'
    conn.execute(sql)

    sql = 'create unique index if not exists touhou_wife_index on touhou_wife(user_id, group_id, date_time);'
    conn.execute(sql)

    conn.commit()


def draw_wife(conn: sqlite3.Connection, group_id: int, user_id: int) -> str:
    def _exclude_data(data: list, exclusion: set) -> list:
        data_dp = []
        for d in data:
            if d not in exclusion:
                data_dp.append(d)
        return data_dp

    pictures = os.listdir(picture_path)
    pictures = [i.split('.')[0] for i in pictures]

    cursor = conn.execute('select wife_name from touhou_wife where group_id={0} and date_time="{1}"'
                          .format(group_id, _get_date()))
    pool = _exclude_data(pictures, {i[0] for i in cursor.fetchall()})

    if len(pool) > 0:
        cursor = conn.execute('select wife_name, count(*) as counts '
                              'from touhou_wife where group_id={0} and user_id={1} '
                              'group by wife_name order by counts;'
                              .format(group_id, user_id))
        draw_count = {i[0]: i[1] for i in cursor.fetchall()}

        index = util.wife_pseudorandom(pool, draw_count)
        return pool[index]

    else:
        return ''


async def send_wife(matcher: Type[Matcher], user_id: int, wife_name: str) -> None:
    file_path = picture_path
    try:
        pictures = os.listdir(picture_path)
        for p in pictures:
            if wife_name in p:
                file_path = picture_path / p
                break

        msg = Message()
        msg.append(MessageSegment.at(user_id=user_id))
        msg.append('你今日的车万老婆是\n')
        if file_path:
            msg.append(MessageSegment.image(file_path))
        msg.append('「' + wife_name + '」')
        await matcher.send(msg)

    except:
        logger.error('发生异常，此时发送的文件为：' + str(file_path) + '\n回溯如下：\n' + traceback.format_exc())


def no_wife_message(user_id: int) -> Message:
    msg = Message()
    msg.append(MessageSegment.at(user_id=user_id))
    msg.append('今天老婆已经抽完啦，明天再来吧~')
    return msg
