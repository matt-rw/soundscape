import os
import sys
import threading

import pygame
from gui import GUI
from PyQt6.QtWidgets import QApplication

from mixer import MyMixer, MySound

# Initialize Pygame and the mixer only if this module is run as the main script
if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()

# Create a lock to prevent conflicts between threads
lock = threading.Lock()

# Function to run the Pygame mixer in its own thread
def pygame_mixer_thread():
    with lock:
        mixer = MyMixer()

    while True:
        # Your Pygame mixer logic here
        with lock:
            mixer.update()

# Function to run the PyQt GUI in its own thread
def qt_gui_thread():
    app = QApplication([])

    # Your code to create GUI objects and start the Qt event loop
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

    gui = GUI(objects, mixer)  # Assuming you pass the mixer instance to the GUI

    app.exec()

# Create threads for Pygame and Qt
pygame_thread = threading.Thread(target=pygame_mixer_thread)
qt_thread = threading.Thread(target=qt_gui_thread)

# Start both threads
pygame_thread.start()
qt_thread.start()

# Wait for both threads to finish (this won't exit the application)
pygame_thread.join()
qt_thread.join()
