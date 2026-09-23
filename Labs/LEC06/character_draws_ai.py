from pico2d import *
import math
from pathlib import Path
from time import perf_counter, sleep


SPEED = 250.0  # 초당 이동 거리(픽셀)
FRAME_TIME = 1.0 / 60
character = None


def draw_character(x, y):
    for event in get_events():
        if event.type == SDL_QUIT or (
            event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE
        ):
            raise SystemExit

    clear_canvas()
    character.draw(x, y)
    update_canvas()


def follow_path(position_at, duration):
    """경과 시간으로 위치를 계산해 프레임 수와 이동 속도를 분리한다."""
    started = perf_counter()
    while True:
        frame_started = perf_counter()
        progress = min((frame_started - started) / duration, 1.0)
        draw_character(*position_at(progress))

        remaining = FRAME_TIME - (perf_counter() - frame_started)
        if remaining > 0:
            sleep(remaining)
        if progress >= 1.0:
            return


def move_circle():
    # 중심 (400, 300), 반지름 200. 하단 중앙에서 반시계 방향으로 출발.
    def position_at(progress):
        angle = -math.pi / 2 + math.tau * progress
        return (400 + 200 * math.cos(angle),
                300 + 200 * math.sin(angle))

    follow_path(position_at, math.tau * 200 / SPEED)


def follow_polygon(points):
    # 각 변의 길이를 이용해 모서리를 지나도 같은 속도를 유지한다.
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1])
               for a, b in zip(points, points[1:])]
    total_length = sum(lengths)

    def position_at(progress):
        distance = progress * total_length
        for start, end, length in zip(points, points[1:], lengths):
            if distance <= length:
                ratio = distance / length
                return (start[0] + (end[0] - start[0]) * ratio,
                        start[1] + (end[1] - start[1]) * ratio)
            distance -= length
        return points[-1]

    follow_path(position_at, total_length / SPEED)


def move_rectangle():
    follow_polygon([(400, 100), (600, 100), (600, 500),
                    (200, 500), (200, 100), (400, 100)])


def move_triangle():
    follow_polygon([(400, 100), (600, 100), (400, 500),
                    (200, 100), (400, 100)])


def main():
    global character
    open_canvas(800, 600, sync=False)
    try:
        image_path = Path(__file__).resolve().with_name('character.png')
        character = load_image(str(image_path))
        while True:
            move_circle()
            move_rectangle()
            move_triangle()
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
