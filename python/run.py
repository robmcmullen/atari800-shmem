#!/usr/bin/env python
from multiprocessing import Process, Array, RawArray
import ctypes
import time

import pyatari800

if __name__ == "__main__":
    emu = pyatari800.Atari800()
    emu.multiprocess()
    while emu.exchange_input[0].frame_count < 4000:
        emu.wait_for_frame()
        print "run.py frame count =", emu.exchange_input[0].frame_count
        emu.debug_video()
        if emu.exchange_input[0].frame_count > 100:
            emu.exchange[5] = ord('A')
        emu.next_frame()
    emu.stop_process()
