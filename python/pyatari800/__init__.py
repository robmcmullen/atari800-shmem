from multiprocessing import Process, Array, RawArray
import ctypes
import time
import numpy as np

from pyatari800 import start_emulator
from shmem import *
from _metadata import __version__

debug_frames = False

def debug_video(mem):
    offset = 336*24 + 128
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

def clamp(val):
    if val < 0.0:
        return 0
    elif val > 255.0:
        return 255
    return int(val)

ntsc_iq_lookup = [
    [  0.000,  0.000 ],
    [  0.144, -0.189 ],
    [  0.231, -0.081 ],
    [  0.243,  0.032 ],
    [  0.217,  0.121 ],
    [  0.117,  0.216 ],
    [  0.021,  0.233 ],
    [ -0.066,  0.196 ],
    [ -0.139,  0.134 ],
    [ -0.182,  0.062 ],
    [ -0.175, -0.022 ],
    [ -0.136, -0.100 ],
    [ -0.069, -0.150 ],
    [  0.005, -0.159 ],
    [  0.071, -0.125 ],
    [  0.124, -0.089 ],
    ]

def gtia_ntsc_to_rgb_table(val):
    # This is a better representation of the NTSC colors using a lookup table
    # rather than the phase calculations. Also from the same thread:
    # http://atariage.com/forums/topic/107853-need-the-256-colors/page-2#entry1319398
    cr = (val >> 4) & 15;
    lm = val & 15;

    y = 255*(lm+1)/16;
    i = ntsc_iq_lookup[cr][0] * 255
    q = ntsc_iq_lookup[cr][1] * 255

    r = y + 0.956*i + 0.621*q;
    g = y - 0.272*i - 0.647*q;
    b = y - 1.107*i + 1.704*q;

    return clamp(r), clamp(g), clamp(b)

def ntsc_color_map():
    rmap = np.empty(256, dtype=np.uint8)
    gmap = np.empty(256, dtype=np.uint8)
    bmap = np.empty(256, dtype=np.uint8)

    for i in range(256):
        r, g, b = gtia_ntsc_to_rgb_table(i)
        rmap[i] = r
        gmap[i] = g
        bmap[i] = b

    return rmap, gmap, bmap

class Atari800(object):
    def __init__(self, args=None):
        self.args = self.normalize_args(args)
        self.exchange = create_exchange()
        self.exchange_input = self.create_input_view(self.exchange)
        self.process = None
        self.width = 336
        self.height = 240
        self.raw = np.frombuffer(self.exchange, dtype=np.uint8, count=336*240, offset=128)
        self.raw.shape = (240, 336)
        self.audio = np.frombuffer(self.exchange, dtype=np.uint8, count=2048, offset=128 + np.alen(self.raw))
        self.frame_count = 0
        self.rmap, self.gmap, self.bmap = ntsc_color_map()
        self.frame_event = []
        self.set_scale(1)

    def create_input_view(self, source):
        size = INPUT_DTYPE.itemsize
        if not isinstance(source, np.ndarray):
            source = np.frombuffer(source, dtype=np.uint8)
        view = source[0:size].view(INPUT_DTYPE, type=np.recarray)
        return view

    def normalize_args(self, args):
        if args is None:
            args = [
                "-basic",
                #"-shmem-debug-video",
                #"jumpman.atr"
            ]
        return args

    def single_process(self):
        start_emulator(self.args, self.exchange, len(self.exchange))

    def multiprocess(self):
        self.process = Process(target=start_emulator, args=(self.args, self.exchange, len(self.exchange)))
        self.process.start()

    def stop_process(self):
        if self.process is not None:
            self.wait_for_frame()
            self.exchange_input[0].main_semaphore = 0xff
            self.process.join()
            self.process = None
        else:
            print "already stopped"

    def is_frame_ready(self):
        return self.exchange_input[0].main_semaphore == 1

    def wait_for_frame(self):
        while True:
            # wait for screen to be ready
            if self.exchange_input[0].main_semaphore == 1:
                break
            time.sleep(0.001)

    def debug_video(self):
        debug_video(self.exchange)

    def next_frame(self):
        self.exchange_input[0].main_semaphore = 0
        self.frame_count += 1
        self.process_frame_events()

    def process_frame_events(self):
        still_waiting = []
        for count, callback in self.frame_event:
            if self.frame_count >= count:
                print "processing %s", callback
                callback()
            else:
                still_waiting.append((count, callback))
        self.frame_event = still_waiting

    def set_scale(self, scale=1):
        self.screen_scale = scale
        newdims = np.asarray((self.height * scale, self.width * scale))
        base = np.indices(newdims)
        d = []
        d.append(base[0]/self.screen_scale)
        d.append(base[1]/self.screen_scale)
        cd = np.array(d)
        self.raw_scaled_lookup = list(cd)
        self.screen = np.empty((self.height * self.screen_scale, self.width * self.screen_scale, 3), np.uint8)

    def scale_raw(self):
        scaled = self.raw
        if self.screen_scale > 1:
            scaled = scaled[self.raw_scaled_lookup]
            print "raw scale: %d, %s" % (self.screen_scale, scaled.shape)
        return scaled

    def get_frame(self, scale=1):
        raw = self.scale_raw()
        self.screen[:,:,0] = self.rmap[raw]
        self.screen[:,:,1] = self.gmap[raw]
        self.screen[:,:,2] = self.bmap[raw]
        return self.screen

    def send_char(self, key_char):
        self.exchange[1:4] = [key_char, 0, 0]

    def send_keycode(self, keycode):
        self.exchange[1:4] = [0, keycode, 0]

    def send_special_key(self, key_id):
        self.exchange[1:4] = [0, 0, key_id]
        if key_id in [2, 3]:
            self.frame_event.append((self.frame_count + 2, self.clear_keys))

    def clear_keys(self):
        self.exchange[1:4] = [0, 0, 0]

    def set_option(self, state):
        self.exchange_input[0].option = state

    def set_select(self, state):
        self.exchange_input[0].select = state

    def set_start(self, state):
        self.exchange_input[0].start = state

