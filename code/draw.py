#!/usr/bin/env python3
"""在 iPhone「信息」的画板上，照 handwriting.py 的笔迹一笔一笔画字。只画，不发送。

  python3 draw.py --pad 0,58,896,271 --data ./hanzi 年          # 手写板（横屏）
  python3 draw.py --pad 109,589,196,244 --margin 50 --min-ms 45 --data ./hanzi 年   # 数码点触（竖屏）
  python3 draw.py --dry --pad 0,58,896,271 --data ./hanzi 年    # 只算坐标不碰手机

--pad 是画板在屏幕上的 x,y,宽,高（单位是点，不是像素）。每台机器不一样，
用 `python3 wda.py source out.xml` 在页面结构里找（见 docs/01-教程.md 第 5、6 步）。
"""
import argparse
import math
import time

import handwriting
import wda


def plan(chars, pad, margin, data_dir, points_per_stroke=14):
    """返回 [[(x, y), ...], ...]：每一笔在屏幕上的点。"""
    x, y, width, height = pad
    size = min(height - margin, (width - margin) / max(1, len(chars)))
    left = x + (width - size * len(chars)) / 2
    top = y + (height - size) / 2
    result = []
    for index, char in enumerate(chars):
        for stroke in handwriting.strokes(char, data_dir):
            step = max(1, len(stroke) // points_per_stroke)
            picked = stroke[::step]
            if picked[-1] != stroke[-1]:
                picked.append(stroke[-1])
            # 字形在 1024 字格里偏上，+60 让它落在画板中间
            result.append([(left + index * size + px / 1024 * size,
                            top + (py + 60) / 1024 * size) for px, py in picked])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("chars", nargs="+")
    parser.add_argument("--pad", required=True, help="画板 x,y,宽,高")
    parser.add_argument("--data", required=True, help="hanzi-writer-data 单字 JSON 所在目录")
    parser.add_argument("--margin", type=float, default=95, help="字离画板边的余量")
    parser.add_argument("--min-ms", type=int, default=20, help="每小段最少走多少毫秒；数码点触要 45 以上才留痕")
    parser.add_argument("--gap", type=float, default=0.25, help="两笔之间停多少秒")
    parser.add_argument("--dry", action="store_true", help="只打印，不碰手机")
    args = parser.parse_args()
    pad = tuple(float(v) for v in args.pad.split(","))
    for number, stroke in enumerate(plan(args.chars, pad, args.margin, args.data), 1):
        if args.dry:
            print(number, len(stroke), "points", [tuple(round(v) for v in stroke[0]), tuple(round(v) for v in stroke[-1])])
            continue
        actions = [{"type": "pointerMove", "duration": 0, "x": stroke[0][0], "y": stroke[0][1]},
                   {"type": "pointerDown", "button": 0}]
        for a, b in zip(stroke, stroke[1:]):
            actions.append({"type": "pointerMove", "duration": max(args.min_ms, int(math.dist(a, b) * 4)),
                            "x": b[0], "y": b[1]})
        actions.append({"type": "pointerUp", "button": 0})
        wda.pointer(actions)
        print("stroke", number, "done")
        time.sleep(args.gap)


if __name__ == "__main__":
    main()
