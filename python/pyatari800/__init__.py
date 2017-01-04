from multiprocessing import Process, Array, RawArray
import ctypes
import time
import numpy as np

from pyatari800 import start_emulator
from _metadata import __version__

debug_frames = False

def debug_video(mem):
    offset = 336*24 + 640
    for y in range(32):
        print "%x:" % offset,
        for x in range(8,60):
            c = mem[x + offset]
            if (c == 0 or c == '\x00'):
                print " ",
            elif (c == 0x94 or c == '\x94'):
                print ".",
            elif (c == 0x9a or c == '\x9a'):
                print "X",
            else:
                try:
                    print ord(c),
                except TypeError:
                    print repr(c),
        print
        offset += 336;

def create_exchange():
    shared = RawArray(ctypes.c_ubyte, 100000)
    if debug_frames:
        pointer = ctypes.byref(shared)
        print pointer
    return shared

class Atari800(object):
    def __init__(self, args=None):
        self.args = self.normalize_args(args)
        self.exchange = create_exchange()
        self.process = None
        self.width = 336
        self.height = 240
        self.raw = np.frombuffer(self.exchange, dtype=np.uint8, count=336*240, offset=640)
        self.raw.shape = (240, 336)
        self.screen = np.empty((self.height, self.width, 3), np.uint8)
        self.bmp = None

    def normalize_args(self, args):
        if args is None:
            args = [
                "-basic",
                "-shmem-debug-video",
            ]
        return args

    def single_process(self):
        start_emulator(self.args, self.exchange, len(self.exchange))

    def multiprocess(self):
        self.process = Process(target=start_emulator, args=(self.args, self.exchange, len(self.exchange)))
        self.process.start()
        count = 0
        while count < 200:
            while True:
                # wait for screen to be ready
                if self.exchange[0] == 1:
                    break
                time.sleep(0.001)
            print "parent", count
            debug_video(self.exchange)
            if count > 100:
                self.exchange[1] = ord('A')
            # tell emulator that input is ready
            self.exchange[0] = 0;
            count += 1
        self.exchange[0] = 0xff
        self.process.join()

    def wait_for_frame(self):
        while True:
            # wait for screen to be ready
            if self.exchange[0] == 1:
                break
            time.sleep(0.001)

    def next_frame(self):
        self.exchange[0] = 0

    def get_frame(self):
        self.screen[:,:,0] = self.raw
        self.screen[:,:,1] = self.raw
        self.screen[:,:,2] = self.raw

    def get_bitmap(self):
        try:
            import wx
        except ImportError:
            return None
        self.get_frame()
        image = wx.ImageFromData(self.width, self.height, self.screen.tostring())
        self.bmp = wx.BitmapFromImage(image)
        return self.bmp

