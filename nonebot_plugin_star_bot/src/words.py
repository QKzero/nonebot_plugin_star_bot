import json
import os
import random
import traceback

from nonebot import on_command, on_message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment

from .. import config, rules

word_path = config.resource_mkdir + '/words/word.json'
sentence_path = config.resource_mkdir + '/words/sentence.json'

def _get_data(path: str) -> dict[str: set[str]]:
    mkdir_path, _ = os.path.split(path)
    if not os.path.exists(mkdir_path):
        os.mkdir(mkdir_path)

    if not os.path.isfile(path):
        return dict()
    else:
        with open(path, mode='r') as file:
            data = json.load(file)
        return {k: set(v) for k, v in data.items()}

def _add_data(data: dict, group_id: int, text: str) -> None:
    if str(group_id) not in data:
        data[str(group_id)] = set()

    group_data = data[str(group_id)]
    group_data.add(text)

def _save_data(data: dict, path: str) -> None:
    mkdir_path, _ = os.path.split(path)
    if not os.path.exists(mkdir_path):
        os.mkdir(mkdir_path)

    save_data = {str(k): list(v) for k, v in data.items()}
    with open(path, mode='w') as file:
        json.dump(save_data, file, skipkeys=True, indent=4)
        # json.dump(save_data, file)

word_data = _get_data(word_path)
sentence_data = _get_data(sentence_path)

record_words = on_message(rule=rules.standerd_rule, priority=config.priority + 2)

@record_words.handle()
async def _(event: GroupMessageEvent) -> None:
    try:
        group_id = event.group_id

        if not event.message or not event.message[0]:
            return

        for msg in event.message:
            if msg.type == 'text':
                text = msg.data['text']
                text.strip(' ')
                if len(text) > 0 and len(text) <= 20:
                    _add_data(data=sentence_data, group_id=group_id, text=text)
                    for word in text:
                        if _isChinese(word):
                            _add_data(data=word_data, group_id=group_id, text=word)
                    _save_data(data=sentence_data, path=sentence_path)
                    _save_data(data=word_data, path=word_path)
    except:
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())

speak_sentence = on_command('说点怪话', rule=rules.standerd_rule, block=True, priority=config.priority)

@speak_sentence.handle()
async def _(event: GroupMessageEvent) -> None:
    try:
        msg = ''

        sentences = list(sentence_data[str(event.group_id)])
        random.shuffle(sentences)
        i = 0
        while len(msg) <= 40 and i < len(sentences):
            msg += str(sentences[i]) + '，'
            i += 1
        msg = msg[:-1]

        await speak_sentence.send(msg)
    except:
        logger.error('发生异常，详细如下：\n' + traceback.format_exc())

def _isChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False