## 여기를 채우시오.

from pico2d import *

open_canvas(800, 600)
character = load_image('character.png')

character.draw(400, 300)
character.draw(200, 150)
character.draw(600, 450)
update_canvas()
delay(5)
close_canvas()