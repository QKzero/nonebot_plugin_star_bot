from distutils.command.config import config
from io import BytesIO
import traceback
from typing import Type

from prettytable import PrettyTable
from PIL import Image, ImageDraw, ImageFont

from nonebot import on_command
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .. import config, rules

analyser = on_command('star analyse', rule=rules.group_rule, aliases={'赛后分析'}, block=True, priority=config.normal_priority)


@analyser.got('star analyse', prompt='请输入比赛数据')
async def _(text: str = ArgPlainText('star analyse')) -> None:
    try:
        image = await damageAnalyse(text)

        await send(analyser, image=image)

    except Exception as e:
        args = e.args
        if 'Format Error' in args:
            await analyser.send('格式不合法，请从控制台复制发送')
        elif len(args) > 0:
            await analyser.send('发生异常，请联系管理员')
            logger.error('发生异常，详细如下：\n' + traceback.format_exc())


async def damageAnalyse(data: str) -> Image.Image:
    attackers = []
    victims = []

    damages = {}
    stuns = {}
    slows = {}

    # read data
    attacker = ''
    data = data.split('\n')
    for line in data:
        if '---' in line:
            attacker = line.split()[1]
            if attacker not in damages:
                damages[attacker] = {}
            if attacker not in attackers:
                attackers.append(attacker)

        elif 'to ' in line:
            assert attacker != '', 'Format Error'
            info = line.split()
            assert len(info) > 2, 'Format Error'
            victim = info[1].strip(':')
            damage = int(info[2])
            damages[attacker][victim] = damage
            if victim not in victims:
                victims.append(victim)

        elif 'Total Stuns' in line:
            assert attacker != '', 'Format Error'
            stuns[attacker] = float(line.split()[2])

        elif 'Total Slows' in line:
            assert attacker != '', 'Format Error'
            slows[attacker] = float(line.split()[2])

    assert len(attackers) != 0 and len(victims) != 0, 'Format Error'

    # analyse data
    header = ['受害者\\攻击者']
    header.extend(attackers)
    header.append('受伤总和')

    rows = [header]

    for victim in victims:
        row = [victim]
        for attacker in attackers:
            if attacker in damages and victim in damages[attacker]:
                row.append(damages[attacker][victim])
            else:
                row.append(0)
        row.append(sum([row[i] for i in range(1, len(row))]))
        rows.append(row)

    row = [sum([rows[i][j] for i in range(1, len(rows))]) for j in range(1, len(rows[0]) - 1)]
    row.insert(0, '伤害总和')
    row.append('-')
    rows.append(row)

    row = ['眩晕时长']
    for attacker in attackers:
        if attacker in stuns:
            row.append(stuns[attacker])
        else:
            row.append(0)
    row.append('-')
    rows.append(row)

    row = ['减速时长']
    for attacker in attackers:
        if attacker in slows:
            row.append(slows[attacker])
        else:
            row.append(0)
    row.append('-')
    rows.append(row)

    # create table
    table = PrettyTable()
    table.field_names = rows[0]
    table.add_rows([rows[i] for i in range(1, len(rows))])

    # create img
    space = 5
    font = ImageFont.truetype('simfang.ttf', 15, encoding='utf-8')
    img = Image.new('RGB', (10, 10), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img, 'RGB')
    img_size = draw.multiline_textsize(str(table), font=font)

    img = img.resize((img_size[0] + space * 2, img_size[1] + space * 2))
    draw = ImageDraw.Draw(img, 'RGB')
    draw.multiline_text((space, space), str(table), fill=(0, 0, 0), font=font)

    return img


async def send(matcher: Type[Matcher], text: str = None, image: Image.Image = None) -> None:
    if not (text or image):
        await matcher.finish()
    msg = Message()
    if text:
        msg.append(text)
    if image:
        img_bytes = BytesIO()
        image.save(img_bytes, format='JPEG')
        msg.append(MessageSegment.image(img_bytes))
    await matcher.finish(msg)
