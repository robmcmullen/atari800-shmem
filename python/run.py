#!/usr/bin/env python
from multiprocessing import Process, Array, RawArray
import ctypes

import pyatari800

def frame(mem):
    global exchange
    print "got frame", exchange, hex(ctypes.addressof(exchange))
    addr = ctypes.addressof(exchange)
    buf = ctypes.string_at(addr, 100000)
    print "DEBUG: string_at", hex(addr), type(buf)
    debug_video(buf)

    for i in range(100000):
        if exchange[i] > 0:
            print "first:", i
            break
    print "fake:", len(mem), type(mem)
    for i in range(len(mem)):
        if mem[i] > 0:
            print "first (fake):", i
            break
    print "DEBUG: mem", id(mem)
    debug_video(mem)
    print "DEBUG: exchange", hex(ctypes.addressof(exchange))
    debug_video(exchange)

def debug_video(mem):
    offset = 336*24
    for y in range(16):
        for x in range(8,60):
            c = mem[x + offset]
            print c,
            # if (c == 0):
            #     print " ",
            # elif (c == 0x94):
            #     print ".",
            # elif (c == 0x9a):
            #     print "X",
            # else:
            #     print "?",
        print
        offset += 336;

exchange = RawArray(ctypes.c_ubyte, 100000)
arraytype = ctypes.c_ubyte * 100000
exchange = arraytype(0)
print exchange[0]
exchange[650] = 255
print dir(exchange)
#shared = exchange.get_obj()
shared = exchange
print dir(shared)
print len(shared)
pointer = ctypes.byref(shared)
print pointer
pyatari800.start_emulator(["-basic", "-shmem-debug-video"], shared, len(shared), frame)
