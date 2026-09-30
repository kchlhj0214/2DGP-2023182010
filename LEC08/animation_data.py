"""이미지 좌표는 좌상단 기준이며 pico2d로 그릴 때만 좌하단 기준으로 바꾼다."""
import json
from dataclasses import dataclass
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"


@dataclass(frozen=True)
class Frame:
    rect: tuple
    offset: tuple
    pivot: tuple


@dataclass(frozen=True)
class Animation:
    name: str
    label: str
    fps: float
    frames: tuple


def load_animations(path=ASSETS / "swordsman.json"):
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    animations = tuple(
        Animation(item["name"], item["label"], item["fps"],
                  tuple(Frame(tuple(f["rect"]), tuple(f["offset"]), tuple(f["pivot"]))
                        for f in item["frames"]))
        for item in data["animations"])
    return path.parent / data["image"], tuple(data["size"]), animations
