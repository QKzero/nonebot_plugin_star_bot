from io import BytesIO
import os
import pathlib
from PIL import Image, ImageDraw, ImageFont

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent

from .. import config, rules

star = on_command('star', rule=rules.group_rule, block=True, priority=config.lowest_priority)


@star.handle()
async def _(event: GroupMessageEvent) -> None:
    msg = Message()
    msg.append(MessageSegment.at(event.user_id))
    msg.append('这里是星夜酱哦，请愉悦地使用咱吧~')

    await star.send(msg)


star_github = on_command('star github', rule=rules.group_rule, block=True, priority=config.normal_priority)


@star_github.handle()
async def _(event: GroupMessageEvent) -> None:
    msg = Message()
    msg.append('星夜酱身体的秘密都在这里了哦~\n')
    msg.append('https://github.com/QKzero/nonebot_plugin_star_bot')

    await star_github.send(msg)


star_help = on_command('star help', rule=rules.group_rule, block=True, priority=config.normal_priority)


@star_help.handle()
async def _(event: GroupMessageEvent) -> None:
    file_path = pathlib.Path(os.path.dirname(__file__)) / '..' / 'res' / 'help_info.txt'

    with open(file_path, mode='r', encoding='utf-8') as file:
        lines = file.readlines()

        text = ''
        length = 0
        width = len(lines)
        for line in lines:
            text += line
            if len(line) > length:
                length = len(line)

        font_size = 15  # 字体大小
        padding = 5  # 内边距
        length = length * font_size + padding * 2
        width = width * font_size + padding * 3

        img = Image.new('RGB', (length, width), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('simfang.ttf', font_size, encoding='utf-8')

        draw.text((padding, padding), text, fill='#000000', font=font)
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')

        msg = Message()
        msg.append(MessageSegment.image(img_bytes))
        await star_help.send(msg)
