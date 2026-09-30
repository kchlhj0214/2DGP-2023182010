"""실제 SDL 렌더링과 종료/재시작 입력을 검사하고 _preview에 화면을 저장한다."""
import ctypes
import importlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image
import pico2d as p

import animation_viewer as viewer
from animation_data import load_animations
from playback import Player

ROOT = Path(__file__).resolve().parent
backend = importlib.import_module("pico2d.pico2d")


def capture(path):
    pixels = (ctypes.c_ubyte * (viewer.WIDTH * viewer.HEIGHT * 4))()
    result = p.SDL_RenderReadPixels(backend.renderer, None, p.SDL_PIXELFORMAT_ABGR8888,
                                  pixels, viewer.WIDTH * 4)
    if result != 0:
        raise RuntimeError(p.SDL_GetError())
    Image.frombytes("RGBA", (viewer.WIDTH, viewer.HEIGHT), bytes(pixels)).save(path)


def verify():
    output = ROOT / "_preview"
    output.mkdir(exist_ok=True)
    image_path, _, animations = load_animations()
    p.open_canvas(viewer.WIDTH, viewer.HEIGHT)
    try:
        p.SDL_HideWindow(backend.window)
        p.hide_lattice()
        sheet = p.load_image(str(image_path))
        player = Player(animations)
        for i, animation in enumerate(animations):
            player.animation_index = i
            for j in range(len(animation.frames)):
                player.frame_index = j
                viewer.draw_scene(p, sheet, player)
                capture(output / f"{animation.name}-{j}.png")
                p.update_canvas()
        player.finished = True
        player.completed_loops = 5
        player.elapsed = 0.5
        viewer.draw_scene(p, sheet, player)
        capture(output / "pause.png")
        p.update_canvas()
    finally:
        p.close_canvas()

    real_open = p.open_canvas

    def hidden_open(*args):
        real_open(*args)
        p.SDL_HideWindow(backend.window)

    # 실제 main 루프를 실행하며 입력만 주입한다.
    key = lambda value: SimpleNamespace(type=p.SDL_KEYDOWN, key=value)
    for events in ([[key(p.SDLK_r)], [key(p.SDLK_ESCAPE)]],
                   [[SimpleNamespace(type=p.SDL_QUIT)]]):
        with patch.object(p, "open_canvas", side_effect=hidden_open), \
             patch.object(p, "get_events", side_effect=events), \
             patch.object(p, "delay"):
            viewer.main()
    print("실제 SDL 렌더링 19프레임 + 정지 화면, R/ESC/창 닫기 검증 완료")


if __name__ == "__main__":
    verify()
