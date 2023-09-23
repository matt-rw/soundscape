# main.py
import os

from PyQt6.QtWidgets import QApplication

from mixer import MyMixer, MySound
from gui import GUI, MyImage

if __name__ == '__main__':
    mixer = MyMixer()
    objects = {}
    obj_id = 0
    path = 'files'
    for obj in os.listdir(path):
        if obj != '.DS_Store':
            image_file = f'{path}/{obj}/{obj}.png'
            sound_file = f'{path}/{obj}/{obj}.mp3'
            image = MyImage(obj_id, image_file)
            sound = MySound(obj_id, sound_file)
            objects[obj_id] = ({'image': image, 'sound': sound})
            obj_id += 1
    app = QApplication([])
    gui = GUI(objects)
    app.exec()
