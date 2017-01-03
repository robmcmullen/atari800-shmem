#!/usr/bin/env python
from multiprocessing import Process, Array, RawArray
import ctypes

import pyatari800

debug_frames = False

def frame(mem, ptr):
    global exchange
    addr = ctypes.addressof(exchange)
    buf = ctypes.string_at(addr, 100000)
    if debug_frames:
        print "got frame", exchange, hex(ctypes.addressof(exchange))
        print "DEBUG: string_at", hex(addr), type(buf)
        debug_video(buf)
        buf = ctypes.string_at(ptr, 100000)
        print "DEBUG: ptr", hex(ptr), type(buf)
        debug_video(buf)

        print "DEBUG: mem", id(mem)
        debug_video(mem)
    print "DEBUG: exchange", hex(ctypes.addressof(exchange))
    debug_video(exchange)

def debug_video(mem):
    offset = 336*24 + 640
    for y in range(16):
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

args = [
    "-basic",
    #"-shmem-debug-video",
]

#exchange = RawArray(ctypes.c_ubyte, 100000)
arraytype = ctypes.c_ubyte * 100000
exchange = arraytype(0)
shared = exchange
if debug_frames:
    print exchange[0]
    exchange[650] = 255
    print dir(exchange)
    #shared = exchange.get_obj()
    print dir(shared)
    print len(shared)
    pointer = ctypes.byref(shared)
    print pointer
pyatari800.start_emulator(args, shared, len(shared), frame)
