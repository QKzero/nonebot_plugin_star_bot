import traceback
from io import BytesIO
import os
import pathlib

from PIL import Image, ImageDraw, ImageFont

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent

from nonebot_plugin_star_bot.nonebot_plugin_star_bot import config, rules
from nonebot_plugin_star_bot.nonebot_plugin_star_bot.log import logger

star_help = on_command('star help', rule=rules.group_rule, block=True, priority=config.normal_priority)


@star_help.handle()
async def _(event: GroupMessageEvent) -> None:
    try:
        file_path = pathlib.Path(os.path.dirname(__file__)) / '..' / '..' / 'res' / 'help_info.txt'

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
            length = length * (font_size - 1) + padding * 2
            width = width * (font_size + 2) + padding * 2

            img = Image.new('RGB', (length, width), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype('simfang.ttf', font_size, encoding='utf-8')

            draw.text((padding, padding), text, fill='#000000', font=font)
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG')

            msg = Message()
            msg.append(MessageSegment.image(img_bytes))
            await star_help.send(msg)

    except:
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())
