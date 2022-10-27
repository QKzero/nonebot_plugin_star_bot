import json
import os
import random

from nonebot import on_command, on_message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment

from .. import config, rules

word_path = config.resource_mkdir + '/words/word.json'
sentence_path = config.resource_mkdir + '/words/sentence.json'

def _get_data(path: str) -> set:
    mkdir_path, _ = os.path.split(path)
    if not os.path.exists(mkdir_path):
        os.mkdir(mkdir_path)

    if not os.path.isfile(path):
        return set()
    else:
        with open(path, mode='r') as file:
            data = json.load(file)
        return set(data)

def _save_data(data: set, path: str) -> None:
    with open(path, mode='w') as file:
        json.dump(data, file, skipkeys=True, indent=4)

word_data = _get_data(word_path)
sentence_data = _get_data(sentence_path)

record_words = on_message(rule=rules.standerd_rule, priority=config.priority + 1)

@record_words.handle()
async def _(event: GroupMessageEvent) -> None:
    if not event.message or not event.message[0]:
        return

    for msg in event.message:
        if msg.type == 'text' and len(msg.data['text']) <= 20:
            text = msg.data['text']
            sentence_data.add(text)
            for word in text:
                if _isChinese(word):
                    word_data.add(word)
            _save_data(data=list(sentence_data), path=sentence_path)
            _save_data(data=list(word_data), path=word_path)

speak_sentence = on_command('说点怪话', rule=rules.standerd_rule, block=True, priority=config.priority)

@speak_sentence.handle()
async def _(event: GroupMessageEvent) -> None:
    msg = ''

    sentences = list(sentence_data)
    random.shuffle(sentences)
    i = 0
    while len(msg) <= 40 and i < len(sentences):
        msg += str(sentences[i]) + ','
        i += 1
    msg = msg[:-1]

    await speak_sentence.finish(msg)

def _isChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False