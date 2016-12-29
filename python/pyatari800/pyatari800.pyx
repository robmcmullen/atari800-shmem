cdef extern:
    int main(int, char **)

def start_emulator(source):
    cdef char **argv
    cdef char *fake_args[10]
    cdef int argc
    cdef char *progname="pyatari800"

    argc = 1
    fake_args[0] = progname
    argv = fake_args

    main(argc, argv)
