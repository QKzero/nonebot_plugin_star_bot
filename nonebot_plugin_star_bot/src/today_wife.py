import datetime
import random
import sqlite3
import traceback
from typing import Type

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment

from .. import config, rules

today_wife = on_command('star wife', rule=rules.group_rule, aliases={'今日老婆'}, block=True, priority=config.priority)


@today_wife.handle()
async def _(bot: Bot, event: GroupMessageEvent) -> None:
    try:
        conn = sqlite3.connect(config.database_path)

        try:
            bot_id = int(bot.self_id)
            user_id = event.user_id
            group_id = event.group_id
            member_list = await bot.get_group_member_list(group_id=group_id)
            member_list = [member['user_id'] for member in member_list]

            _check_database_table(conn)

            cursor = conn.execute('select wife_id from today_wife '
                                  'where user_id={0} and group_id={1} and date_time="{2}"'
                                  .format(user_id, group_id, _get_date()))
            record = [i[0] for i in cursor.fetchall()]

            if len(record) == 0:
                wife_id = draw_wife(conn=conn, bot_id=bot_id, user_id=user_id, group_id=group_id,
                                    member_list=member_list)
                if wife_id == -1:
                    await today_wife.send(no_wife_message(user_id=user_id))
                else:
                    conn.execute('insert into today_wife(user_id, group_id, wife_id, date_time) values '
                                 '({0}, {1}, {2}, "{3}")'.format(user_id, group_id, wife_id, _get_date()))
                    conn.execute('insert into today_wife(user_id, group_id, wife_id, date_time) values '
                                 '({0}, {1}, {2}, "{3}")'.format(wife_id, group_id, user_id, _get_date()))
                    conn.commit()
                    await send_wife(matcher=today_wife, bot=bot, user_id=user_id, wife_id=wife_id, group_id=group_id,
                                    member_list=member_list)
            else:
                wife_id = record[0]
                await send_wife(matcher=today_wife, bot=bot, user_id=user_id, wife_id=wife_id, group_id=group_id,
                                member_list=member_list)

        except:
            raise

    except:
        await today_wife.send('星夜坏掉啦，请帮忙叫主人吧')
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
    sql = 'create table if not exists today_wife (' \
          'user_id integer(10) primary key not null,' \
          'group_id integer(10) not null ,' \
          'wife_id integer(10) not null ,' \
          'date_time date not null);'
    conn.execute(sql)

    sql = 'create unique index if not exists wife_index on today_wife(user_id, group_id, date_time);'
    conn.execute(sql)

    conn.commit()


def draw_wife(conn: sqlite3.Connection, bot_id: int, user_id: int, group_id: int, member_list: list[int]) -> int:
    pool = []

    cursor = conn.execute('select wife_id from today_wife where group_id={0} and date_time="{1}"'
                          .format(group_id, _get_date()))
    record = {i[0] for i in cursor.fetchall()}

    for member_id in member_list:
        if member_id not in record and member_id != user_id and member_id != bot_id:
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
