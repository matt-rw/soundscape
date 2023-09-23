from random import randint

import pygame
from pygame.mixer import Channel, Sound


class MySound:
    def __init__(self, sound_id, mp3, location=(0, 0, 0), interval=(0, 0), start=0):
        try:
            self.sound_id = sound_id
            self.name = mp3.split('/')[-1].split('.')[0]
            self.sound = Sound(mp3)
            self.x_loc, self.y_loc, self.z_loc = location
            self.interval_min, self.interval_max = interval
            self.duration = self.sound.get_length()
            self.next_play_time = start * 1000
        except pygame.error as e:
            print(f"Error loading sound '{mp3}': {e}")

    def play(self):
        now = pygame.time.get_ticks()
        if now >= self.next_play_time:
            interval = randint(self.interval_min, self.interval_max)
            print(self.name, now//1000, interval)
            self.sound.play()
            interval = int(interval * 1000)
            duration = int(self.duration * 1000)
            self.next_play_time = now + interval + duration

class MyMixer:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.channels = {}

    def add_channel(self, sound: MySound):
        if sound.duration > 0:
            channel = Channel(len(self.channels))
            self.channels[sound.name] = {
                'channel': channel,
                'sound': sound,
            }
        else:
            print("Sound duration is not valid. Exiting.")
            pygame.quit()

    def update(self):
        for name, channel in self.channels.items():
            channel['sound'].play()

    def play(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update()

        pygame.quit()
