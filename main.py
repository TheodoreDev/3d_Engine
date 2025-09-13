import keyboard
import time
import engine as eg
from lib_math import *

square = [
    Triangle3D(vec3(-0.5, -0.5, 1),
                vec3(-0.5, 0.5, 1),
                vec3(0.5, 0.5, 1)),
    Triangle3D(vec3(-0.5, -0.5, 1),
                vec3(0.5, 0.5, 1),
                vec3(0.5, -0.5, 1))
]

light = eg.LightSource(vec3(3, 5, -1))

cam = eg.Camera(vec3(0, 0, -2), 0, 0)

def key_input():
    if keyboard.is_pressed("down arrow"):
        if cam.pitch > -1.57:
            cam.pitch -= 0.01*dt
    if keyboard.is_pressed("up arrow"):
        if cam.pitch < 1.57:
            cam.pitch += 0.01*dt
    if keyboard.is_pressed("right arrow"):
        cam.yaw -= 0.01*dt
    if keyboard.is_pressed("left arrow"):
        cam.yaw += 0.01*dt
    if keyboard.is_pressed("z"):
        cam.pos += cam.get_forward_direction()*0.01*dt
    if keyboard.is_pressed("q"):
        cam.pos += -1*cam.get_right_direction()*0.01*dt
    if keyboard.is_pressed("s"):
        cam.pos += -1*cam.get_forward_direction()*0.01*dt
    if keyboard.is_pressed("d"):
        cam.pos += cam.get_right_direction()*0.01*dt
    if keyboard.is_pressed("space"):
        cam.pos.y += 0.01*dt
    if keyboard.is_pressed("shift"):
        cam.pos.y -= 0.01*dt

cube = eg.loadObj("object.obj")

last = time.time()
while True:
    current = time.time()
    dt = (current - last)*100
    last = current
    eg.reset(' ')
    key_input()
    eg.placeMesh(cube, cam, light)
    eg.draw()