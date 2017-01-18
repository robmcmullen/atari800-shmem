from libc.stdlib cimport malloc, free
from cpython.string cimport PyString_AsString
import ctypes

ctypedef void (*c_cb_ptr)(unsigned char *)

cdef extern:
    int start_shmem(int, char **, void *, int, c_cb_ptr)
    void SHMEM_DebugVideo(unsigned char *)

cdef char ** to_cstring_array(list_str):
    cdef char **ret = <char **>malloc(len(list_str) * sizeof(char *))
    for i in xrange(len(list_str)):
        ret[i] = PyString_AsString(list_str[i])
    return ret

pycallback = None

debug_frames = False

cdef void callback(unsigned char *mem):
    cdef long ptr = <long>mem
    cdef Py_ssize_t length = 100000
    py_mem = mem[:length]
    if debug_frames:
        print "in cython callback", hex(<long>ptr)
        SHMEM_DebugVideo(mem)
    pycallback(py_mem, ptr)
    if debug_frames:
        print "done"
        SHMEM_DebugVideo(mem)

def start_emulator(args, raw=None, size=0, pycb=None):
    global pycallback
    global debug_frames
    cdef char *fake_args[10]
    cdef char **argv = fake_args
    cdef int argc
    cdef char *progname="pyatari800"
    cdef char **c_args = to_cstring_array(args)
    cdef long ptr = 0
    cdef void *c_raw = NULL
    pycallback = pycb
    cdef c_cb_ptr c_cb = NULL

    if "-shmem-debug-video" in args:
        debug_frames = True

    argc = 1
    fake_args[0] = progname
    for i in xrange(len(args)):
        arg = c_args[i]
        fake_args[argc] = arg
        argc += 1

    if pycb is not None:
        c_cb = &callback
        if debug_frames:
            print "callback", hex(<long>c_cb)

    save = raw
    if save is not None:
        a = ctypes.addressof(save)
        if debug_frames:
            print "CTYPES:", ctypes.byref(save)
            ref = ctypes.byref(save)
            print "ref:", ref
            print "addr:", hex(a)
            print dir(a)
        ptr = a
        c_raw = <void *>ptr
        # for i in xrange(1000):
        #     dummy[i] = 'm';
        start_shmem(argc, argv, c_raw, size, c_cb)
    else:
        start_shmem(argc, argv, NULL, 0, c_cb)

    if debug_frames:
        print "Finished start_shmem"
    free(c_args)
