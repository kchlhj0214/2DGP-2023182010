from pico2d import *
import math


# open_canvas(800, 600)
open_canvas()

# 여기를 채우시오.

grass = load_image('grass.png')
character = load_image('character.png')

cx = 400
cy = 300
r = 200
radius = 0

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
    x = cx + r * math.cos(math.radians(radius))
    y = cy + r * math.sin(math.radians(radius))
    character.draw(x, y)
    update_canvas()

    radius += 2
    if radius >= 360:
        radius = 0
    delay(0.01)

close_canvas()