"""이미지 좌표는 좌상단 기준이며 pico2d로 그릴 때만 좌하단 기준으로 바꾼다."""
import json
import math
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
    size = tuple(data["size"])
    validate(size, animations)
    image_path = path.parent / data["image"]
    if not image_path.is_file():
        raise FileNotFoundError(f"스프라이트 파일이 없습니다: {image_path}")
    return image_path, size, animations


def validate(size, animations):
    if len(size) != 2 or any(n <= 0 for n in size) or not animations:
        raise ValueError("시트 크기와 애니메이션 목록을 확인하세요.")
    if len({a.name for a in animations}) != len(animations):
        raise ValueError("애니메이션 이름은 고유해야 합니다.")
    for animation in animations:
        if not animation.frames or not math.isfinite(animation.fps) or animation.fps <= 0:
            raise ValueError(f"프레임 또는 재생 속도 오류: {animation.name}")
        for frame in animation.frames:
            if len(frame.rect) != 4 or len(frame.offset) != 2 or len(frame.pivot) != 2:
                raise ValueError("프레임 좌표 형식을 확인하세요.")
            x, y, w, h = frame.rect
            if min(x, y) < 0 or min(w, h) <= 0 or x + w > size[0] or y + h > size[1]:
                raise ValueError(f"시트 경계를 벗어난 프레임: {animation.name}")
