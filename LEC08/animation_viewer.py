"""Drill #8: pico2d 기반 캐릭터 애니메이션 뷰어."""
from animation_data import load_animations
from playback import Player, REPEAT_COUNT, PAUSE_SECONDS
from pathlib import Path
from time import perf_counter

WIDTH, HEIGHT = 800, 600
SCALE = 7  # 몸 높이 48~52px → 336~364px: 화면 높이의 절반 이상
FOOT_Y = 125


def frame_destination(frame):
    _, _, width, height = frame.rect
    offset_x, offset_y = frame.offset
    pivot_x, pivot_y = frame.pivot
    # 같은 발 기준점을 유지하여 잘라낸 프레임 크기가 달라도 흔들리지 않는다.
    return (WIDTH / 2 + (offset_x + width / 2 - pivot_x) * SCALE,
            FOOT_Y + (pivot_y - offset_y - height / 2) * SCALE,
            width * SCALE, height * SCALE)


def draw_frame(sheet, frame):
    x, top, width, height = frame.rect
    # JSON은 좌상단, pico2d.clip_draw는 좌하단 기준이다.
    bottom = sheet.h - top - height
    sheet.clip_draw(x, bottom, width, height, *frame_destination(frame))


def draw_scene(p, sheet, player, font, small_font):
    p.clear_canvas()
    p.draw_rectangle(0, 0, WIDTH, HEIGHT, 20, 27, 40, filled=True)
    font.draw(28, 571, "SWORDSMAN / ANIMATION VIEWER", (232, 240, 250))
    for i, animation in enumerate(player.animations):
        left = 28 + i * 190
        active = i == player.animation_index
        color = (45, 95, 105) if active else (32, 42, 58)
        p.draw_rectangle(left, 519, left + 174, 548, *color, filled=True)
        small_font.draw(left + 12, 534, f"{animation.label}  {len(animation.frames)}F", (225, 237, 242))
    p.draw_line(80, FOOT_Y - 2, WIDTH - 80, FOOT_Y - 2, 65, 86, 109)
    draw_frame(sheet, player.frame)
    if player.finished:
        status = f"PAUSE  {max(0, PAUSE_SECONDS - player.elapsed):.1f}s  /  5 loops complete"
    else:
        status = f"PLAY  {player.completed_loops + 1}/{REPEAT_COUNT}   FRAME {player.frame_index + 1}/{len(player.animation.frames)}"
    font.draw(28, 82, status, (105, 222, 197))
    small_font.draw(28, 47, "ESC Exit   R Restart   F1 Frame bounds", (153, 172, 194))
    small_font.draw(28, 22, "Art: tbbk / CC0     Scale: 7x     5 loops > 1s pause > next", (153, 172, 194))


def main():
    import pico2d as p

    image_path, size, animations = load_animations()
    p.open_canvas(WIDTH, HEIGHT)
    try:
        p.hide_lattice()
        sheet = p.load_image(str(image_path))
        if (sheet.w, sheet.h) != size:
            raise ValueError("PNG 크기와 프레임 데이터가 일치하지 않습니다.")
        font_path = Path(p.__file__).resolve().parent / "data" / "ConsolaMalgun.ttf"
        font = p.load_font(str(font_path), 22)
        small_font = p.load_font(str(font_path), 16)
        running = True
        player = Player(animations)
        previous = perf_counter()
        while running:
            now = perf_counter()
            player.update(now - previous)
            previous = now
            for event in p.get_events():
                if event.type == p.SDL_QUIT or (event.type == p.SDL_KEYDOWN and event.key == p.SDLK_ESCAPE):
                    running = False
                elif event.type == p.SDL_KEYDOWN and event.key == p.SDLK_r:
                    player = Player(animations)
            draw_scene(p, sheet, player, font, small_font)
            p.update_canvas()
            p.delay(0.01)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
