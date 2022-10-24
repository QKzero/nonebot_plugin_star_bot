from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import Event, MessageEvent, MessageSegment

from star_bot.config import group_white_list

async def _standerd_checker(event: Event) -> bool:
    try:
        session_id = event.get_session_id()
        if session_id.startswith('group'):
            _, group_id, _ = session_id.split('_')
            group_id = int(group_id)
            return group_id in group_white_list

    except:
        return False

standerd_rule = Rule(_standerd_checker)

async def _font_atme_checker(event: MessageEvent) -> None:
    # ensure message not empty
    if not event.original_message or not event.original_message[0]:
        return False

    def _is_at_me_seg(segment: MessageSegment):
        return segment.type == "at" and str(segment.data.get("qq", "")) == str(event.self_id)

    return _is_at_me_seg(event.original_message[0])

font_atme_rule = Rule(_font_atme_checker)