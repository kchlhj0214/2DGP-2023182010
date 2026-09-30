"""Drill #8: pico2d 기반 캐릭터 애니메이션 뷰어."""
from animation_data import load_animations

WIDTH, HEIGHT = 800, 600


def draw_frame(sheet, frame):
    x, top, width, height = frame.rect
    # JSON은 좌상단, pico2d.clip_draw는 좌하단 기준이다.
    bottom = sheet.h - top - height
    sheet.clip_draw(x, bottom, width, height, WIDTH / 2, HEIGHT / 2)


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
        while running:
            for event in p.get_events():
                if event.type == p.SDL_QUIT:
                    running = False
            p.clear_canvas()
            draw_frame(sheet, animations[0].frames[0])
            p.update_canvas()
            p.delay(0.01)
    finally:
        p.close_canvas()


if __name__ == "__main__":
    main()
