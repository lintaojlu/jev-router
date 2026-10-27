"""用 macOS Vision 把截图变成带编号的文本元素。像素坐标只留在本机。"""

from __future__ import annotations

from pathlib import Path

from ocrmac import ocrmac
from PIL import Image

# Choice 最多 255 个选项，给 none 留一个位置。
MAX_ELEMENTS = 254


def perceive(image_path: Path) -> dict:
    """读取一张截图，返回元素列表和是否因选项上限被截断。"""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"找不到截图：{path}")

    with Image.open(path) as image:
        width, height = image.size

    raw = ocrmac.OCR(
        str(path),
        framework="vision",
        recognition_level="accurate",
        language_preference=["zh-Hans", "en-US"],
    ).recognize()

    candidates = []
    for item in raw:
        text, confidence, bbox = item[0], float(item[1]), item[2]
        cleaned = " ".join(str(text).split())
        if not cleaned:
            continue
        box = _normalized_box(bbox)
        candidates.append(
            {
                "text": cleaned,
                "ocr_confidence": confidence,
                "bbox": box,
                "position": coarse_position(box),
            }
        )

    truncated = len(candidates) > MAX_ELEMENTS
    if truncated:
        candidates = sorted(candidates, key=lambda item: item["ocr_confidence"], reverse=True)[:MAX_ELEMENTS]

    candidates.sort(key=_reading_order)
    elements = []
    for index, item in enumerate(candidates, start=1):
        elements.append({"id": f"e{index}", **item})

    return {
        "image": str(path),
        "width": width,
        "height": height,
        "elements": elements,
        "truncated": truncated,
        "recognized": len(raw),
    }


def coarse_position(bbox: list[float]) -> str:
    """把归一化框收成粗位置。Vision 的 y 从底部起算。"""
    x, y, width, height = bbox
    cx = x + width / 2
    cy = y + height / 2
    vertical = "上部" if cy >= 2 / 3 else "下部" if cy <= 1 / 3 else "中部"
    horizontal = "偏左" if cx <= 1 / 3 else "偏右" if cx >= 2 / 3 else "居中"
    if horizontal == "居中":
        return f"{vertical}居中"
    return f"{vertical}{horizontal}"


def vision_bbox_to_pixels(bbox: list[float], width: int, height: int) -> list[float]:
    """Vision 归一化框（左下角原点）转成 PIL 像素框 [left, top, right, bottom]。"""
    x, y, box_w, box_h = bbox
    left = x * width
    right = (x + box_w) * width
    top = (1 - (y + box_h)) * height
    bottom = (1 - y) * height
    return [left, top, right, bottom]


def _normalized_box(bbox) -> list[float]:
    values = [float(v) for v in bbox]
    if len(values) != 4:
        raise ValueError(f"无法识别的 OCR 框：{bbox!r}")
    return values


def _reading_order(item: dict) -> tuple[float, float]:
    x, y, _width, height = item["bbox"]
    top = y + height
    return (-top, x)
