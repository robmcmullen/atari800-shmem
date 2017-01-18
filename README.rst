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

pyatari800 is available through PyPI::

    pip install pyatari800

or you can compile from source::

    git clone https://github.com/robmcmullen/pyatari800.git
    cd pyatari800/python
    python setup install

Your version of python must be able to build C extensions, which should be
automatic in most linux and on OS X. You may have to install the python
development packages on linux distributions like Ubuntu or Linux Mint.

Windows doesn't come with a C compiler, but happily, Microsoft provides a
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

All the following commands are from the atari800/src directoyr. The configure
script must be created with::

    ./autogen.sh

From there, it's the normal GNU-style install::

    ./configure --target=shmem
    make
    ./atari800

Since atari800-shmem is designed to be used as a module for a larger program,
running it at the command line is not very useful. However, there is a simple
display converting Graphics 0 to text "pixels" that displays the upper-left
corner of every frame to show that the emulator is running.

pyatari800
----------

If you check out the pyatari800 source from the git repository or you want to
modify pyatari800 and change the .pyx file, you'll need Cython. The .pyx file
is compiled to C as a side effect of using the command::

    python setup.py sdist

For testing, use::

    python setup.py build_ext --inplace

The test code is located in the ``tests`` directory. A simple wxPython front-
end is included as ``wxatari.py`` and when run on the command line, will pass
through any arguments to the atari800 core. E.g.::

    python wxatari.py jumpman.atr

will run Jumpman in the wxPython window.


Usage
=====



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

