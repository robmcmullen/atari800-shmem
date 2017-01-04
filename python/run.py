#!/usr/bin/env python
from multiprocessing import Process, Array, RawArray
import ctypes
import time

import pyatari800

if __name__ == "__main__":
    emu = pyatari800.Atari800()
    emu.multiprocess()
    while emu.frame_count < 400:
        emu.wait_for_frame()
        print "run.py frame count =", emu.frame_count
        emu.debug_video()
        if emu.frame_count > 100:
            emu.exchange[1] = ord('A')
        emu.next_frame()
    emu.stop_process()
