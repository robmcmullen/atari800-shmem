================================================
pyatari800 and the atari800 shared memory driver
================================================

A new shared-memory driver for the cross-platform Atari 8-bit emulator atari800
allowing custom front-ends in any language that supports shared memory access.
It provides two-way communication to the underlying emulator, sending inputs to
the core and receiving the screen and sound information for every frame.

As an example, pyatari800 is a python wrapper that has no user interface
dependencies, and can be used by any python program or GUI toolkit.

As a further example, there is a small demo front-end for wxPython that will
operate on all 3 major platforms: Linux, Mac OS X, and Windows.


Prerequisites
=============

atari800-shmem
--------------

* C compiler

pyatari800
----------

* python 2.7 (but not 3.x yet) capable of building C extensions
* numpy

The wxPython front-end additionally requires:

* wxPython 3.0.2 (classic, not Phoenix yet)
* pyopengl


Installation
============

pyatari800 will eventually be available through PyPI, but currently you have to
compile from source::

    git clone https://github.com/robmcmullen/pyatari800.git
    cd pyatari800/python
    python setup.py sdist && python setup.py build_ext --inplace

Your version of python must be able to build C extensions, which should be
automatic in most linux and on OS X. You may have to install the python
development packages on linux distributions like Ubuntu or Linux Mint.

Windows doesn't come with a C compiler, but happily Microsoft provides a
cut-down version of their Visual Studio compiler just for compiling Python
extensions! Download and install it from
`here <https://www.microsoft.com/en-us/download/details.aspx?id=44266>`_.

Windows compatibility code was used in pyatari800:

* Dirent (a windows port of dirent.h) from https://github.com/tronkko/dirent
  and licensed under the MIT license which is GPL compatible


Developers
==========

If you check out the code from the git repository, you will have to build a few
files that are included with source distributions but are not in the repository
because they are generated files.

atari800-shmem
--------------

The shared memory "platform" is designed to be used as an embedded module for a
larger program, so it's not really useful as a platform for the atari800
executable. But for demo purposes a sample version can be compiled that will
capture every display frame and convert the upper left corner of the screen
into ASCII characters that will be displayed in the terminal. After checking out the source with::

    git clone https://github.com/robmcmullen/pyatari800.git

the configure script must be created with::

    cd atari800/src
    ./autogen.sh

From there, it's the normal GNU-style build::

    ./configure --target=shmem
    make
    ./atari800

Embedding in other programs
---------------------------

The shared memory ("shmem") target is designed to be an interface between the
atari800 emulator core and some other programming language. If the language can
compile C extensions (like Python can) and can create shared memory blocks, you
should be able to control and view the atari800 emulator from within your
program.

My use case was directly embedding the emulator in a Python program so that I
could display the emulated screen inside my program. Longer term goals were to
be able to step through the code and create a GUI debugger as in the `Altirra
emulator <http://www.virtualdub.org/altirra.html>`_, except unlike Altirra
would be cross-platform.

I chose shared memory rather than direct function calls to the emulator to
allow the emulator to be run in a separate thread or process to allow the
wrapper program to remain in control even if the emulator should hang or crash.

The operation of the shmem platform requires the wrapper program to create a
block of shared memory at least ``SHMEM_TOTAL_SIZE`` bytes long (aligned to a
32 bit boundary if the platform requires it to access 32 bit values) and pass
the address into the initialization routine, ``start_shmem``. This initializes
the emulator (through the ``Atari800_Initialise`` routine) and generates the
first frame of the emulation.

The shared memory block is broken up into sections: the input section, the
video section, and the sound section. The input section is 128 bytes long and
has specific memory locations for the wrapper program to set everything that
the emulator needs for input: key values, joystick values, special keys, and
mouse buttons.

It also includes 2 locations that the shmem target will set: the frame count,
and the main semaphore. The semaphore is how the synchronization between the
embedded emulator and the wrapper program takes place. The location
``main_semaphore`` can take 3 values:

* 0: wrapper sets the value to 0 when all input is ready to be processed for the next frame
* 1: the emulator changes the value to 1 when the screen is ready
* 255: exit the emulator

The semaphore is initialized at 0 so the first frame of emulation is
automatically generated after platform initialization. The wrapper can do other
things while the emulator is generating the frame, periodically checking for a
1 in ``main_semaphore``. The wrapper will have to check quite often, of course,
because frames happen 50 or 60 times per second. In my example wxPython
wrapper, I implement this check as a poll and sleep loop where it sleeps .001
seconds before checking again.

Detecting a 1 means that the emulator is reporting that the screen is ready to
be shown and any sound samples are ready to be played. The wrapper gets the
data out of the video and sound areas of the shared memory and presents them to
the user in whatever wrapper-specific ways it can.

The data in the video area is a 336x240 pixel array in the same format as the
internal ``Screen_atari`` array: one byte per pixel where the byte is one of
the Atari colors. It's up to the wrapper to convert the Atari color to an RGB
value to be displayed to the user.

The sound support is still under development, so currently no sound is returned
to the wrapper.

As quickly an the wrapper can, it should set the ``main_semaphore`` to 0 to
indicate to the emulator that it can start its timing loop before generating
the next frame.

The wrapper is also responsible for getting user input to the emulator. During
the time after setting ``main_semaphore`` to 0, where the wrapper is otherwise
waiting for the emulator to report 1, it should be polling or using events to
determine what keys have been pressed and if there has been any joystick or
mouse activity that should be reported.

This loop happens for the duration of the emulation, until the wrapper sets
``main_semaphore`` to 255, which will exit the emulator.

A feature of this semaphore system is that it's easy to implement a pause
feature: simply wait to report a 0 and the emulation will be frozen in time.


Example embedding: pyatari800
-----------------------------

If you check out the pyatari800 source from the git repository::

    git clone https://github.com/robmcmullen/pyatari800.git

or you want to modify pyatari800 and change the .pyx file, you'll need Cython. The .pyx file is compiled to C as a side effect of using the command::

    cd python
    python setup.py sdist

For testing, use::

    python setup.py build_ext --inplace

The test code is located in the ``tests`` directory. A simple wxPython front-
end is included as ``wxatari.py`` and when run on the command line, will pass
through any arguments to the atari800 core. E.g.::

    cd tests
    python wxatari.py jumpman.atr

will run Jumpman in the wxPython window (assuming you have the ATR image of
Jumpman as jumpman.atr, of course.  See ).


License
==========

pyatari800 (python wrapper for atari800) and atari800-shmem (shared memory
driver for atari800)

* atari800 is Copyright (c) 1995-1998 David Firth
* and Copyright (c) 1998-2017 Atari800 development team
* Dirent is Copyright (c) 2015 Toni Rönkkö
* pyatari800 and atari800-shmem is Copyright (c) 2017 Rob McMullen (feedback@playermissile.com)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

