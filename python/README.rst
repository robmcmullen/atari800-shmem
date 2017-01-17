==========
pyatari800
==========

Python wrapper for the cross-platform Atari 8-bit emulator atari800. It
includes a new shared-memory driver for atari800 allowing access to the
internals of the emulator, and as an example front-end includes a wxPython
client to display the emulator on Linux, Mac OS X, and Windows.


Prerequisites
=============

* python 2.7 (but not 3.x yet) capable of building C extensions

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
----------

If you check out the pyatari800 source from the git repository or you want to
modify pyatari800 and change the .pyx file, you'll need Cython. The .pyx file
is compiled to C as a side effect of using the command::

    python setup.py sdist



Usage
=====



License
==========

pyatari800, python wrapper for atari800

atari800 is Copyright (c) 1995-1998 David Firth
        and Copyright (c) 1998-2017 Atari800 development team
Dirent is Copyright (c) 2015 Toni Rönkkö
pyatari800 is Copyright (c) 2017 Rob McMullen (feedback@playermissile.com)

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

