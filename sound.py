import threading
import time
from gensound import *


class SoundServer(threading.Thread):
    def __init__(self, sound_duration=0.1):
        threading.Thread.__init__(self)
        self.stop_sound_server_signal = threading.Event()
        self.sound_lock = threading.Lock()
        self.sound_to_play = []
        self.sound_duration = sound_duration  # seconds

    def run(self):
        while not self.stop_sound_server_signal.is_set():
            self.sound_lock.acquire(blocking=False)
            if not self.sound_lock.locked():
                time.sleep(self.sound_duration)
                continue

            if len(self.sound_to_play) == 0:
                self.sound_lock.release()
                time.sleep(self.sound_duration / 100)
            else:
                first_pending_sound = Sine(frequency=sum(self.sound_to_play) / len(self.sound_to_play),
                                           duration=self.sound_duration * 1000)
                # print("playin {}".format(first_pending_sound))
                self.sound_to_play = []
                self.sound_lock.release()
                first_pending_sound.play(sample_rate=32000)

    def stop_sound_server(self):
        self.stop_sound_server_signal.set()

    def add_sound_runable(self, freq):
        with self.sound_lock:
            if type(freq) is int:
                self.sound_to_play.append(freq)
            elif type(freq) is list:
                self.sound_to_play += freq
            else:
                raise TypeError


class AAST(threading.Thread):
    def __init__(self, server_obj: SoundServer, freq):
        threading.Thread.__init__(self)
        self.freq = freq
        self.server_obj = server_obj

    def run(self):
        # print("aast run")
        self.server_obj.sound_lock.acquire(blocking=True)
        self.server_obj.sound_to_play.append(self.freq)
        self.server_obj.sound_lock.release()


def add_sound_async(server_obj: SoundServer, freq):
    # print("sdd_sound_async")
    obj = AAST(server_obj, freq)
    obj.start()
