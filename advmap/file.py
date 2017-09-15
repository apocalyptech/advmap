#!/usr/bin/evn python2
# vim: set expandtab tabstop=4 shiftwidth=4:
#
# Adventure Game Mapper
# Copyright (C) 2010-2017 CJ Kucera
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import io
import os
from struct import pack, unpack

__all__ = [ 'LoadException', 'Savefile' ]

class LoadException(Exception):

    def __init__(self, text, orig_exception=None):
        self.text = text
        self.orig_exception = orig_exception

    def __str__(self):
        return repr(self.text)

class Savefile(object):
    """ Class that wraps around a file object, to simplify things """

    def __init__(self, filename, in_memory=False):
        """
        Empty object.  Pass in `in_memory` = `True` to create an in-memory
        BytesIO object rather than actually using `filename`.  `filename`
        will be completely ignored in that case, and no changes will be
        written to disk, though calling `close`, `open_r` or `open_w` may
        end up overwriting that state.  `in_memory` is basically just designed
        to be used with our unit tests.
        """
        self.filename = filename
        if in_memory:
            self.df = io.BytesIO()
            self.opened_r = True
            self.opened_w = True
        else:
            self.df = None
            self.opened_r = False
            self.opened_w = False

    def exists(self):
        """ Returns true if the file currently exists. """
        return os.path.exists(self.filename)

    def close(self):
        """ Closes the filehandle. """
        if (self.opened_r or self.opened_w):
            self.df.close()
            self.opened_r = False
            self.opened_w = False

    def open_r(self):
        """ Opens a file for reading.  Throws IOError if unavailable"""
        if (self.opened_r or self.opened_w):
            raise IOError('File is already open')
        self.df = open(self.filename, 'rb')
        self.opened_r = True

    def open_w(self):
        """ Opens a file for writing.  Throws IOError if unavailable"""
        if (self.opened_r or self.opened_w):
            raise IOError('File is already open')
        self.df = open(self.filename, 'wb')
        self.df.seek(0)
        self.opened_w = True

    def eof(self):
        """ Test to see if we're at EOF, since Python doesn't provide that for us. """
        # Note that theoretically there's some cases where a file error masquerades as
        # an EOF because of this code.  I can cope with that.
        a = self.df.read(1)
        if (len(a) == 0):
            return True
        else:
            self.df.seek(-1, 1)
            return False

    def seek(self, offset, whence=0):
        """ Passthrough to the internal object. """
        return self.df.seek(offset, whence)

    def tell(self):
        """ Passthrough to the internal object. """
        return self.df.tell()

    def write(self, byteval):
        """ Passthrough to the internal object. """
        return self.df.write(byteval)

    def read(self, length=-1):
        """ Read the rest of the file from the handle. """
        return self.df.read(length)

    def readchar(self):
        """ Read a signed character (1-byte) "integer" from the savefile. """
        if (not self.opened_r):
            raise IOError('File is not open for reading')
        return unpack('b', self.df.read(1))[0]

    def writechar(self, charval):
        """ Write a signed character (1-byte) "integer" to the savefile. """
        if (not self.opened_w):
            raise IOError('File is not open for writing')
        self.df.write(pack('b', charval))

    def readuchar(self):
        """ Read an unsigned character (1-byte) "integer" from the savefile. """
        if (not self.opened_r):
            raise IOError('File is not open for reading')
        return unpack('B', self.df.read(1))[0]

    def writeuchar(self, charval):
        """ Write an unsigned character (1-byte) "integer" to the savefile. """
        if (not self.opened_w):
            raise IOError('File is not open for writing')
        self.df.write(pack('B', charval))

    def readshort(self):
        """ Read a short (2-byte) integer from the savefile. """
        if (not self.opened_r):
            raise IOError('File is not open for reading')
        return unpack('<H', self.df.read(2))[0]

    def writeshort(self, shortval):
        """ Write a short (2-byte) integer to the savefile. """
        if (not self.opened_w):
            raise IOError('File is not open for writing')
        self.df.write(pack('<H', shortval))

    def readint(self):
        """ Read an integer from the savefile. """
        if (not self.opened_r):
            raise IOError('File is not open for reading')
        return unpack('<I', self.df.read(4))[0]

    def writeint(self, intval):
        """ Write an integer to the savefile. """
        if (not self.opened_w):
            raise IOError('File is not open for writing')
        self.df.write(pack('<I', intval))

    def readfloat(self):
        """ Read a float (actually a double) from the savefile. """
        if (not self.opened_r):
            raise IOError('File is not open for reading')
        return unpack('d', self.df.read(8))[0]

    def writefloat(self, floatval):
        """ Write a float (actually a double) to the savefile. """
        if (not self.opened_w):
            raise IOError('File is not open for writing')
        self.df.write(pack('d', floatval))

    def readstr(self):
        """ Read a string from the savefile, read the string length first """
        if (not self.opened_r):
            raise IOError('File is not open for reading')
        length = self.readshort()
        if (length == 0):
            string = ''
        else:
            string = str(self.df.read(length), encoding='utf-8')
        if (len(string) != length):
            raise LoadException('Error reading string, expected %d, read %d' % (length, len(string)))
        # Discard the NULL byte
        self.readchar()
        return string

    def writestr(self, strval):
        """
        Write a string to the savefile, prepended by the length.
        It's a bit silly to both prepend with the length and then pad with a
        NULL, but personally I like having the length, and other C-based apps
        are more comfortable with NULL.  So, whatever.  We can afford one more
        byte per string.
        """
        if (not self.opened_w):
            raise IOError('File is not open for writing')
        if (len(strval) > 65535):
            raise IOError('Maximum string length is currently 65535')
        self.writeshort(len(strval))
        self.df.write(bytes(strval, 'utf-8'))
        self.df.write(b"\0")
