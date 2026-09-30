"""Drill #8: pico2d 기반 캐릭터 애니메이션 뷰어."""
from animation_data import load_animations
from playback import Player
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


def main():
    import pico2d as p

    image_path, size, animations = load_animations()
    p.open_canvas(WIDTH, HEIGHT)
    try:
        p.hide_lattice()
        sheet = p.load_image(str(image_path))
        if (sheet.w, sheet.h) != size:
            raise ValueError("PNG 크기와 프레임 데이터가 일치하지 않습니다.")
        running = True
        player = Player(animations)
        previous = perf_counter()
        while running:
            now = perf_counter()
            player.update(now - previous)
            previous = now
            for event in p.get_events():
                if event.type == p.SDL_QUIT:
                    running = False
            p.clear_canvas()
            draw_frame(sheet, player.frame)
            p.update_canvas()
            p.delay(0.01)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
