import bisect
import random


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
