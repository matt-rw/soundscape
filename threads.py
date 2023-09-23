import os
import sys
import threading

import pygame

from gui import GUI, MyImage
from mixer import MyMixer, MySound

path = 'files'

def read_images() -> dict:
    objects = {}
    obj_id = 0
    for obj in os.listdir(path):
        if obj != '.DS_Store':
            image_file = f'{path}/{obj}/{obj}.png'
            image = MyImage(obj_id, image_file)
            objects[obj_id] = image
            obj_id += 1
    return objects

def read_sounds() -> dict:
    objects = {}
    obj_id = 0
    for obj in os.listdir(path):
        if obj != '.DS_Store':
            sound_file = f'{path}/{obj}/{obj}.mp3'
            sound = MySound(obj_id, sound_file)
            objects[obj_id] = sound
            obj_id += 1
    return objects

def mixer_thread():
    mixer = MyMixer()
    objects = read_sounds()
    for key in objects:
        sound_object = objects[key]
        mixer.add_channel(sound_object)

    while True:
        mixer.update()

if __name__ == '__main__':
    pygame.mixer.pre_init(44100, -16, 2, 2048)  # Adjust these settings as needed
    pygame.init()

    objects = read_images()

    pygame_thread = threading.Thread(target=mixer_thread)
    pygame_thread.start()

    gui = GUI(objects)

    sys.exit(gui.app.exec())
