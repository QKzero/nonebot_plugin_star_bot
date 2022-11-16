import bisect
import datetime
import random
import sqlite3
from typing import Type

from nonebot.internal.matcher import Matcher


def wife_pseudorandom(pool: list[int], draw_count: dict[int, int]) -> int:
    weight = []
    if len(draw_count) > 0:
        max_count = max(draw_count.values())
    else:
        max_count = 0

    for p in pool:
        pre_weight = 0
        if len(weight) > 0:
            pre_weight += weight[len(weight) - 1]
        if p in draw_count:
            weight.append(pre_weight + max_count - draw_count[p] + 1)
        else:
            weight.append(pre_weight + max_count + 1)

    return bisect.bisect_right(weight, random.randint(weight[0], weight[len(weight) - 1])) - 1


def get_wife_date() -> datetime.date:
    _datetime = datetime.datetime.today()
    date = _datetime.date()
    hour = _datetime.time().hour
    if 0 <= hour < 6:
        return date - datetime.timedelta(days=1)
    else:
        return date


async def wife_date_remind(matcher: Type[Matcher]) -> None:
    if datetime.date.today() != get_wife_date():
        await matcher.send('老婆在早上六点才会刷新噢，早点休息吧~')


def check_database_table(conn: sqlite3.Connection) -> None:
    sql = 'create table if not exists today_wife (' \
          'user_id integer(10) primary key not null,' \
          'group_id integer(10) not null ,' \
          'wife_id integer(10) not null ,' \
          'date_time date not null);'
    conn.execute(sql)

    sql = 'create unique index if not exists today_wife_index on today_wife(user_id, group_id, date_time);'
    conn.execute(sql)

    conn.commit()
