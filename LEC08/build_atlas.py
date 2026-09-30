"""원본의 투명 여백을 잘라 비정형 시트와 좌표 JSON을 재생성한다. Pillow 필요."""
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent


def cells(columns, count):
    return [(i % columns * 64, i // columns * 64,
             i % columns * 64 + 64, i // columns * 64 + 64)
            for i in range(count)]


# 공격 두 번째 프레임은 칼 이펙트가 64px 칸을 넘어간다.
# 해당 프레임을 80px 영역으로 읽어 이펙트를 보존한다.
SPECS = [
    ("idle", "IDLE", 4, cells(1, 2)),
    ("run", "RUN", 10, cells(3, 8)),
    ("jump", "JUMP", 6, cells(2, 4)),
    ("attack", "ATTACK", 9,
     [(0, 0, 64, 64), (64, 0, 144, 64), (192, 0, 256, 64),
      (256, 0, 320, 64), (320, 0, 384, 64)]),
]


def build():
    animations, tiles = [], []
    y, atlas_width = 2, 0
    for key, label, fps, regions in SPECS:
        source = Image.open(ROOT / "assets" / "source" / f"{key}.png").convert("RGBA")
        frames, x, row_height = [], 2, 0
        for region in regions:
            original = source.crop(region)
            bounds = original.getbbox()
            if bounds is None:
                raise ValueError(f"빈 프레임: {key} {region}")
            tile = original.crop(bounds)
            width, height = tile.size
            frames.append({"rect": [x, y, width, height],
                           "offset": list(bounds[:2]), "pivot": [32, 64]})
            tiles.append((tile, (x, y)))
            x += width + 2
            row_height = max(row_height, height)
        atlas_width = max(atlas_width, x)
        y += row_height + 2
        animations.append({"name": key, "label": label, "fps": fps, "frames": frames})
    atlas = Image.new("RGBA", (atlas_width, y))
    for tile, position in tiles:
        atlas.paste(tile, position)
    atlas.save(ROOT / "assets" / "swordsman.png")
    data = {"image": "swordsman.png", "size": list(atlas.size), "animations": animations}
    (ROOT / "assets" / "swordsman.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("Atlas:", atlas.size, [(a["name"], len(a["frames"])) for a in animations])


if __name__ == "__main__":
    build()
