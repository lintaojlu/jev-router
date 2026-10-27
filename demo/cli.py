"""命令行：任务说明 + 截图 → 下一步建议。不发送键鼠事件。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from demo.decide import api_key, build_state, call_jev, judge, questions_payload
from demo.perceive import perceive, vision_bbox_to_pixels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="根据已有任务和屏幕截图，判断下一步该做什么。只输出建议，不操作键鼠。",
    )
    parser.add_argument("--task", required=True, help="已经确定的任务说明")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--image", help="截图路径（PNG 或 JPG）")
    source.add_argument("--capture", action="store_true", help="抓取当前屏幕再判断，仍然不点击")
    parser.add_argument("--out", default="runs", help="输出目录，默认 runs/")
    args = parser.parse_args(argv)

    run_dir = Path(args.out) / datetime.now().strftime("%Y%m%dT%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    if args.capture:
        image_path = run_dir / "screen.png"
        _capture(image_path)
    else:
        image_path = Path(args.image)

    observation = perceive(image_path)
    state = build_state(args.task, observation["elements"])
    questions = questions_payload(observation["elements"])
    _write(run_dir / "elements.json", observation)
    _write(run_dir / "request_state.json", {"model": _model_name(), "state": state, "questions": questions})

    key = api_key()
    if key is None:
        decision = {
            "task": args.task,
            "jev_called": False,
            "message": "未设置 TYPESAFE_API_KEY，已完成本机 OCR 并写好请求体，没有调用 Jev，也没有编造选择。",
            "elements_sent": len(observation["elements"]),
            "elements_truncated": observation["truncated"],
        }
        _write(run_dir / "decision.json", decision)
        annotate(image_path, observation["elements"], None, run_dir / "annotated.png")
        print(decision["message"])
        print(f"元素 {len(observation['elements'])} 个，请求体：{run_dir / 'request_state.json'}")
        return 2

    try:
        answers = call_jev(state, observation["elements"])
    except Exception as exc:
        decision = {
            "task": args.task,
            "jev_called": False,
            "message": f"Jev 调用失败：{exc}",
            "elements_sent": len(observation["elements"]),
            "elements_truncated": observation["truncated"],
        }
        _write(run_dir / "decision.json", decision)
        annotate(image_path, observation["elements"], None, run_dir / "annotated.png")
        print(decision["message"], file=sys.stderr)
        print(f"本机结果仍在 {run_dir}")
        return 1

    judged = judge(
        args.task,
        observation["elements"],
        answers["operation"],
        answers["target"],
        answers["goal_complete"],
    )
    decision = {
        "jev_called": True,
        "model": answers["model"],
        "image": str(image_path),
        "elements_sent": len(observation["elements"]),
        "elements_truncated": observation["truncated"],
        "usage": answers["usage"],
        **judged,
    }
    _write(run_dir / "decision.json", decision)
    annotate(image_path, observation["elements"], decision["target"]["choice"], run_dir / "annotated.png")
    print(decision["recommendation"])
    if decision["uncertainty_reason"]:
        print(decision["uncertainty_reason"])
    print(f"详情：{run_dir / 'decision.json'}")
    return 0


def annotate(image_path: Path, elements: list[dict], target_id: str | None, dest: Path) -> None:
    """在截图上标出 OCR 框。选中的目标用更粗的框。"""
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for item in elements:
        left, top, right, bottom = vision_bbox_to_pixels(item["bbox"], width, height)
        chosen = item["id"] == target_id
        color = (196, 72, 48) if chosen else (70, 110, 160)
        draw.rectangle([left, top, right, bottom], outline=color, width=4 if chosen else 1)
        if chosen:
            label = f"{item['id']} {item['text']}"
            draw.text((left, max(0, top - 14)), label, fill=color)
    image.save(dest)


def _capture(dest: Path) -> None:
    subprocess.run(["screencapture", "-x", str(dest)], check=True)


def _model_name() -> str:
    import os

    return os.environ.get("JEV_MODEL", "").strip() or "jev-latest"


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
