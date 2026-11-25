"""把一个汉字变成"一个人写的"笔画点列。

输入是 hanzi-writer-data 的单字 JSON（用它的 medians：每一笔的中线点列，1024 字格，y 朝上）。
输出是若干笔，每笔一串 (x, y)，坐标仍在 1024 字格里、y 已翻成朝下。

这支笔的性子：瘦长、整个字往右上微抬、每笔带一点手抖；一个字只"放开"写一笔
（往下走得最长的那一笔，多拖出去一截）。同一个字每次写出来一样（按字定随机种子），
所以认得出是同一个人的字。想换成你家 AI 的笔迹，改 STYLE 里的数。
"""
import json
import math
import random
from pathlib import Path

STYLE = {
    "rotate_deg": 2.5,     # 右边微微抬起
    "shear_deg": -6,       # 往右倾
    "scale_x": 0.86,       # 瘦
    "scale_y": 1.06,       # 长
    "jitter": 4,           # 每个点的手抖（字格单位）
    "stroke_shift": 8,     # 每一笔整体的随机偏移
    "let_go": 0.22,        # 放开的那一笔多拖出自身长度的多少
}


def _seglen(points):
    return [math.dist(points[k], points[k + 1]) for k in range(len(points) - 1)]


def _catmull(points, k=18):
    """Catmull-Rom 样条：把折线抹成顺的曲线。"""
    if len(points) < 3:
        return points
    padded = [points[0]] + points + [points[-1]]
    out = []
    for i in range(1, len(padded) - 2):
        p0, p1, p2, p3 = padded[i - 1], padded[i], padded[i + 1], padded[i + 2]
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t
                       + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2
                       + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3)
                for a in (0, 1)))
    out.append(points[-1])
    return out


def strokes(char, data_dir):
    """返回 [[(x, y), ...], ...]，一笔一个列表，顺序就是笔顺。"""
    data = json.loads((Path(data_dir) / f"{char}.json").read_text(encoding="utf-8"))
    medians = [[tuple(p) for p in m] for m in data["medians"]]
    rnd = random.Random(ord(char) * 7919)
    rot = math.radians(STYLE["rotate_deg"])
    shear = math.tan(math.radians(STYLE["shear_deg"]))

    def down_length(m):
        return max(0, m[0][1] - m[-1][1]) + 0.3 * sum(_seglen(m))

    let_go = max(range(len(medians)), key=lambda i: down_length(medians[i]))
    result = []
    for index, median in enumerate(medians):
        if len(median) > 2 and math.dist(median[0], median[1]) < 45:
            median = median[1:]                      # 去掉起笔的小钩
        size = min(1.0, sum(_seglen(median)) / 380)
        dx = rnd.uniform(-1, 1) * STYLE["stroke_shift"] * size
        dy = rnd.uniform(-1, 1) * STYLE["stroke_shift"] * size
        points = []
        for x, y in median:
            x += dx + rnd.uniform(-1, 1) * STYLE["jitter"]
            y += dy + rnd.uniform(-1, 1) * STYLE["jitter"]
            cx, cy = (x - 512) * STYLE["scale_x"], (y - 450) * STYLE["scale_y"]
            points.append((cx * math.cos(rot) - cy * math.sin(rot) + 512 - cy * shear,
                           cx * math.sin(rot) + cy * math.cos(rot) + 450))
        if index == let_go and len(points) >= 2:
            (x1, y1), (x2, y2) = points[-2], points[-1]
            seg = math.dist((x1, y1), (x2, y2)) or 1
            extra = max(0, min(STYLE["let_go"] * sum(_seglen(points)), 160, y2 + 60))
            ux, uy = (x2 - x1) / seg, (y2 - y1) / seg
            for k in (0.5, 1.0):
                points.append((x2 + ux * extra * k, y2 + uy * extra * k))
        points = _catmull(points)
        result.append([(x, 900 - y) for x, y in points])   # 翻成屏幕坐标（y 朝下）
    return result
