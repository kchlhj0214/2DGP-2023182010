import math
from pathlib import Path

from pico2d import *


# 실습 과제 2: 화면 중앙을 중심으로 반시계 방향 원운동
open_canvas(800, 600)

image_folder = Path(__file__).resolve().parent
grass = load_image(str(image_folder / 'grass.png'))
character = load_image(str(image_folder / 'character.png'))

center_x, center_y = 400, 300
radius = 200
angle = 0  # 도 단위 각도. 0도는 원의 오른쪽 끝이다.
angle_step = 1  # 한 프레임에 증가하는 각도
running = True

while running:
    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

    if not running:
        break

    # sin, cos는 라디안 단위 각도를 받으므로 도 단위를 변환한다.
    radian = math.radians(angle)
    x = center_x + radius * math.cos(radian)
    y = center_y + radius * math.sin(radian)

    clear_canvas()
    grass.draw(400, 30)
    character.draw(x, y)
    update_canvas()

    # 360도에 도달하면 0도로 돌아가 같은 원을 계속 돈다.
    angle = (angle + angle_step) % 360
    delay(0.01)

close_canvas()
