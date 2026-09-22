from pathlib import Path

from pico2d import *


# 실습 과제 1: 오른쪽 -> 위 -> 왼쪽 -> 아래 순서로 사각 운동
open_canvas(800, 600)

# 현재 파이썬 파일과 같은 폴더에 있는 PNG를 사용한다.
image_folder = Path(__file__).resolve().parent
grass = load_image(str(image_folder / 'grass.png'))
character = load_image(str(image_folder / 'character.png'))

left, right = 100, 700
bottom, top = 100, 500
x, y = left, bottom
direction = 'right'
speed = 2  # 한 프레임에 이동하는 픽셀 수
running = True

while running:
    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

    if not running:
        break

    clear_canvas()
    grass.draw(400, 30)
    character.draw(x, y)
    update_canvas()

    # 모서리에 도착하면 좌표를 맞추고 다음 방향으로 전환한다.
    if direction == 'right':
        x += speed
        if x >= right:
            x = right
            direction = 'up'
    elif direction == 'up':
        y += speed
        if y >= top:
            y = top
            direction = 'left'
    elif direction == 'left':
        x -= speed
        if x <= left:
            x = left
            direction = 'down'
    elif direction == 'down':
        y -= speed
        if y <= bottom:
            y = bottom
            direction = 'right'

    delay(0.01)

close_canvas()
