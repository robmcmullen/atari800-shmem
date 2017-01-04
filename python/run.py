#!/usr/bin/env python
from multiprocessing import Process, Array, RawArray
import ctypes
import time

import pyatari800

if __name__ == "__main__":
    emu = pyatari800.Atari800()
    emu.multiprocess()
