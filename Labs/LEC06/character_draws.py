# 실습 과제 진행

from pico2d import *
import math

open_canvas(800, 600)
boy = load_image('character.png')

def draw_boy(x, y):
    clear_canvas()
    boy.draw(x, y)
    update_canvas()
    delay(0.01)

# def move_circle():
#     for degree in range(360):
#         theta = math.radians(degree + 270)
#         x = 400 + 200 * math.cos(theta)
#         y = 300 + 200 * math.sin(theta)

#         draw_boy(x, y)

# def move_top():
#     for x in range(600, 200, -5):
#             draw_boy(x, 500)

# def move_right():
#     for y in range(100, 500, 5):
#             draw_boy(600, y)

# def move_bottom_1():
#     for x in range(400, 600, 5):
#         draw_boy(x, 100)

# def move_bottom_2():
#     for x in range(200, 400, 5):
#         draw_boy(x, 100)

# def move_left():
#     for y in range(500, 100, -5):
#             draw_boy(200, y)


# def move_rectangle():     
#     move_bottom_1()
#     move_right()
#     move_top()
#     move_left()
#     move_bottom_2()

def move_triangle_1():
    print('triangle1')

def move_triangle_2():
    print('triangle2')

def move_triangle_3():
    print('triangle3')

def move_triangle():
    move_triangle_1()
    move_triangle_2()
    move_triangle_3() 

while True:
    # move_circle()
    # move_rectangle()
    move_triangle()
    break
