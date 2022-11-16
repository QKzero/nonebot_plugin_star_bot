import datetime
import sqlite3
import traceback
from typing import Type

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message, MessageSegment

from . import util
from .. import config, rules

today_wife = on_command('star wife', rule=rules.group_rule, aliases={'今日老婆'}, block=True,
                        priority=config.normal_priority)


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

            util.check_database_table(conn)

            cursor = conn.execute('select wife_id from today_wife '
                                  'where user_id={0} and group_id={1} and date_time="{2}"'
                                  .format(user_id, group_id, util.get_wife_date()))
            record = [i[0] for i in cursor.fetchall()]

            if len(record) == 0:
                wife_id = _draw_wife(conn=conn, bot_id=bot_id, user_id=user_id, group_id=group_id,
                                     member_list=member_list)
                if wife_id == -1:
                    await today_wife.send(_no_wife_message(user_id=user_id))
                else:
                    conn.execute('insert into today_wife(user_id, group_id, wife_id, date_time) values '
                                 '({0}, {1}, {2}, "{3}")'.format(user_id, group_id, wife_id, util.get_wife_date()))
                    conn.execute('insert into today_wife(user_id, group_id, wife_id, date_time) values '
                                 '({0}, {1}, {2}, "{3}")'.format(wife_id, group_id, user_id, util.get_wife_date()))
                    conn.commit()
                    await _send_wife(matcher=today_wife, bot=bot, user_id=user_id, wife_id=wife_id, group_id=group_id,
                                     member_list=member_list)
            else:
                wife_id = record[0]
                await _send_wife(matcher=today_wife, bot=bot, user_id=user_id, wife_id=wife_id, group_id=group_id,
                                 member_list=member_list)

                await util.wife_date_remind(matcher=today_wife)

        except:
            raise

    except:
        await today_wife.send('星夜坏掉啦，请帮忙叫主人吧')
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())


def _draw_wife(conn: sqlite3.Connection, bot_id: int, user_id: int, group_id: int, member_list: list[int]) -> int:
    cursor = conn.execute('select wife_id from today_wife where group_id={0} and date_time="{1}"'
                          .format(group_id, util.get_wife_date()))
    exclusion = {i[0] for i in cursor.fetchall()}

    pool = []
    for member_id in member_list:
        if member_id not in exclusion and member_id != user_id and member_id != bot_id:
            pool.append(member_id)

    if len(pool) > 0:
        cursor = conn.execute('select wife_id, count(wife_id) as counts '
                              'from today_wife '
                              'where group_id={0} and user_id={1} '
                              'group by wife_id '
                              'order by counts;'
                              .format(group_id, user_id))
        draw_count = {i[0]: i[1] for i in cursor.fetchall()}

        index = util.wife_pseudorandom(pool, draw_count)
        return pool[index]
    else:
        return -1


async def _send_wife(matcher: Type[Matcher], bot: Bot, user_id: int, wife_id: int, group_id: int,
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


def _no_wife_message(user_id: int) -> Message:
    msg = Message()
    msg.append(MessageSegment.at(user_id=user_id))
    msg.append('今天老婆已经抽完啦，明天再来吧~')
    return msg
