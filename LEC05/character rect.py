from pico2d import *


# open_canvas(800, 600)
open_canvas()

# 여기를 채우시오.

grass = load_image('grass.png')
character = load_image('character.png')

x = 100
y = 100
direction = 0   # 0 left, 1 up, 2 right, 3 down

running = True

while running:
    for event in get_events():
        if event.type == SDL_QUIT:  # 창의 X 버튼
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

    if not running:
        break

    clear_canvas()
    grass.draw(400, 30)
    character.draw(x, y)
    update_canvas()
    if direction == 0:
        x -= 2
        if x < 100:
            direction = 1
            x = 100
    elif direction == 1:
        y += 2
        if y > 500:
            direction = 2
            y = 500
    elif direction == 2:
        x += 2
        if x > 700:
            direction = 3
            x = 700
    elif direction == 3:
        y -= 2
        if y < 100:
            direction = 0
            y = 100
    delay(0.01)

close_canvas()