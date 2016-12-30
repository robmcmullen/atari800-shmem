from libc.stdlib cimport malloc, free
from cpython.string cimport PyString_AsString

cdef extern:
    int start_shmem(int, char **)

cdef char ** to_cstring_array(list_str):
    cdef char **ret = <char **>malloc(len(list_str) * sizeof(char *))
    for i in xrange(len(list_str)):
        ret[i] = PyString_AsString(list_str[i])
    return ret

def start_emulator(args):
    cdef char *fake_args[10]
    cdef char **argv = fake_args
    cdef int argc
    cdef char *progname="pyatari800"
    cdef char **c_args = to_cstring_array(args)

    argc = 1
    fake_args[0] = progname
    for i in xrange(len(args)):
        arg = c_args[i]
        print arg
        fake_args[argc] = arg
        argc += 1

    start_shmem(argc, argv)

    free(c_args)
