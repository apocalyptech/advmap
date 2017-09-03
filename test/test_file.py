#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import io
import os
import tempfile
import unittest
from advmap.file import Savefile, LoadException

class LoadExceptionTests(unittest.TestCase):
    """
    Tests for our LoadException
    """

    def test_raise(self):
        """
        Test a basic raise of the exception
        """
        with self.assertRaises(LoadException) as cm:
            raise LoadException('Testing')
        self.assertEqual(cm.exception.text, 'Testing')
        self.assertEqual(str(cm.exception), '\'Testing\'')
        self.assertEqual(cm.exception.orig_exception, None)

    def test_raise_with_original_exception(self):
        """
        Test a raise where an original exception is attached
        """
        with self.assertRaises(LoadException) as cm:
            try:
                x = 4/0
            except Exception as e:
                raise LoadException('Testing', e)
        self.assertEqual(cm.exception.text, 'Testing')
        self.assertEqual(type(cm.exception.orig_exception), ZeroDivisionError)

class SavefileTests(unittest.TestCase):
    """
    Tests of our Savefile object.  If this ever gets ported to Python 3,
    we'll have some work to do re: bytes vs. strings.
    """

    def get_temp_filename(self):
        """
        Gets a temp filename created by `tempfile.mkstemp`
        """
        (handle, pathname) = tempfile.mkstemp()
        os.close(handle)
        return pathname

    def get_in_memory(self):
        """
        Returns an in-memory Savefile
        """
        return Savefile('', in_memory=True)

    def test_initialization_filename(self):
        """
        Tests initialization with a filename
        """
        df = Savefile('filename')
        self.assertEqual(df.filename, 'filename')
        self.assertEqual(df.df, None)
        self.assertEqual(df.opened_r, False)
        self.assertEqual(df.opened_w, False)

    def test_initialization_in_memory(self):
        """
        Tests initialization in-memory
        """
        df = self.get_in_memory()
        self.assertEqual(df.filename, '')
        self.assertEqual(type(df.df), io.BytesIO)
        self.assertEqual(df.opened_r, True)
        self.assertEqual(df.opened_w, True)

    def test_exists_true(self):
        """
        Tests for a file which should exist
        """
        df = Savefile(__file__)
        self.assertEqual(df.exists(), True)

    def test_exists_false(self):
        """
        Tests for a file which should not exist
        """
        df = Savefile('%s-ifthisexistssomethingisweird' % (__file__))
        self.assertEqual(df.exists(), False)

    def test_close_already_closed(self):
        """
        Tests closing a file that's already not open
        """
        filename = self.get_temp_filename()
        try:
            df = Savefile(filename)
            self.assertEqual(df.opened_r, False)
            self.assertEqual(df.opened_w, False)
            df.close()
            self.assertEqual(df.opened_r, False)
            self.assertEqual(df.opened_w, False)
        finally:
            os.unlink(filename)

    def test_open_for_reading_and_close(self):
        """
        Tests closing a file that's been open for reading.
        This is technically testing a few functions in here but
        it's impossible to separate them really.
        """
        filename = self.get_temp_filename()
        try:
            df = Savefile(filename)
            df.open_r()
            self.assertEqual(df.opened_r, True)
            self.assertEqual(df.opened_w, False)
            df.close()
            self.assertEqual(df.opened_r, False)
            self.assertEqual(df.opened_w, False)
        finally:
            os.unlink(filename)

    def test_open_for_writing_and_close(self):
        """
        Tests closing a file that's been open for writing.
        This is technically testing a few functions in here but
        it's impossible to separate them really.
        """
        filename = self.get_temp_filename()
        try:
            df = Savefile(filename)
            df.open_w()
            self.assertEqual(df.opened_r, False)
            self.assertEqual(df.opened_w, True)
            df.close()
            self.assertEqual(df.opened_r, False)
            self.assertEqual(df.opened_w, False)
        finally:
            os.unlink(filename)

    def test_open_r_already_open_r(self):
        """
        Tests attempting to open a file for reading which is already
        open for reading.
        """
        filename = self.get_temp_filename()
        try:
            df = Savefile(filename)
            df.open_r()
            with self.assertRaises(IOError) as cm:
                df.open_r()
            self.assertIn('File is already open', str(cm.exception))
            df.close()
        finally:
            os.unlink(filename)

    def test_open_r_already_open_w(self):
        """
        Tests attempting to open a file for reading which is already
        open for reading.
        """
        filename = self.get_temp_filename()
        try:
            df = Savefile(filename)
            df.open_w()
            with self.assertRaises(IOError) as cm:
                df.open_r()
            self.assertIn('File is already open', str(cm.exception))
            df.close()
        finally:
            os.unlink(filename)

    def test_open_w_already_open_r(self):
        """
        Tests attempting to open a file for reading which is already
        open for reading.
        """
        filename = self.get_temp_filename()
        try:
            df = Savefile(filename)
            df.open_r()
            with self.assertRaises(IOError) as cm:
                df.open_w()
            self.assertIn('File is already open', str(cm.exception))
            df.close()
        finally:
            os.unlink(filename)

    def test_open_w_already_open_w(self):
        """
        Tests attempting to open a file for reading which is already
        open for reading.
        """
        filename = self.get_temp_filename()
        try:
            df = Savefile(filename)
            df.open_w()
            with self.assertRaises(IOError) as cm:
                df.open_w()
            self.assertIn('File is already open', str(cm.exception))
            df.close()
        finally:
            os.unlink(filename)

    def test_eof_true(self):
        """
        Test for end-of-file when that is the case.
        """
        df = self.get_in_memory()
        self.assertEqual(df.eof(), True)

    def test_eof_false(self):
        """
        Test for end-of-file when that is not the case.
        """
        df = self.get_in_memory()
        df.write(b'test')
        df.seek(0)
        self.assertEqual(df.eof(), False)
        self.assertEqual(df.tell(), 0)

    def test_seek_base(self):
        """
        Test basic `seek()` functionality.
        """
        df = self.get_in_memory()
        df.write(b'0123456789')
        df.seek(5)
        self.assertEqual(df.read(1), b'5')

    def test_seek_whence_cur(self):
        """
        Test `seek()` functionality using the `whence` arg os.SEEK_CUR
        """
        df = self.get_in_memory()
        df.write(b'0123456789')
        df.seek(-2, os.SEEK_CUR)
        self.assertEqual(df.read(1), b'8')

    def test_seek_whence_end(self):
        """
        Test `seek()` functionality using the `whence` arg os.SEEK_END
        """
        df = self.get_in_memory()
        df.write(b'0123456789')
        df.seek(-3, os.SEEK_END)
        self.assertEqual(df.read(1), b'7')

    def test_tell(self):
        """
        Test `tell()` functionality
        """
        df = self.get_in_memory()
        df.write(b'0123456789')
        self.assertEqual(df.tell(), 10)
        df.seek(0)
        self.assertEqual(df.tell(), 0)

    def test_write(self):
        """
        Test writing arbitrary data
        """
        df = self.get_in_memory()
        df.write(b'hello')
        df.seek(0)
        self.assertEqual(df.read(5), b'hello')

    def test_read_specific(self):
        """
        Tests reading a certain amount of data
        """
        df = self.get_in_memory()
        df.write(b'hello')
        df.seek(0)
        self.assertEqual(df.read(1), b'h')

    def test_read_all(self):
        """
        Tests reading the rest of the data in the file
        """
        df = self.get_in_memory()
        df.write(b'hello')
        df.seek(0)
        self.assertEqual(df.read(), b'hello')

    def test_reading_on_unopened_file(self):
        """
        Tests read functions when the file hasn't been opened for reading
        """
        df = self.get_in_memory()
        df.close()
        # Alas for not having unittest.subTest in Py2
        for func in [df.readchar, df.readuchar, df.readshort, df.readint,
                df.readfloat, df.readstr]:
            with self.assertRaises(IOError) as cm:
                func()
            self.assertIn('File is not open for reading', str(cm.exception))

    def test_writing_on_unopened_file(self):
        """
        Tests write functions when the file hasn't been opened for writing.
        """
        df = self.get_in_memory()
        df.close()
        # Alas for not having unittest.subTest in Py2
        for func in [df.writechar, df.writeuchar, df.writeshort, df.writeint,
                df.writefloat, df.writestr]:
            with self.assertRaises(IOError) as cm:
                func(3)
            self.assertIn('File is not open for writing', str(cm.exception))

    def test_read_write_char(self):
        """
        Tests reading and writing a char.
        """
        df = self.get_in_memory()
        df.writechar(-4)
        self.assertEqual(df.tell(), 1)
        df.seek(0)
        self.assertEqual(df.readchar(), -4)
        self.assertEqual(df.tell(), 1)

    def test_read_write_uchar(self):
        """
        Tests reading and writing a uchar.
        """
        df = self.get_in_memory()
        df.writeuchar(230)
        self.assertEqual(df.tell(), 1)
        df.seek(0)
        self.assertEqual(df.readuchar(), 230)
        self.assertEqual(df.tell(), 1)

    def test_read_write_short(self):
        """
        Tests reading and writing a short.
        """
        df = self.get_in_memory()
        df.writeshort(65500)
        self.assertEqual(df.tell(), 2)
        df.seek(0)
        self.assertEqual(df.readshort(), 65500)
        self.assertEqual(df.tell(), 2)

    def test_read_write_int(self):
        """
        Tests reading and writing an int
        """
        df = self.get_in_memory()
        df.writeint(4294967200)
        self.assertEqual(df.tell(), 4)
        df.seek(0)
        self.assertEqual(df.readint(), 4294967200)
        self.assertEqual(df.tell(), 4)

    def test_read_write_float(self):
        """
        Tests reading and writing a float (actually a double)
        """
        df = self.get_in_memory()
        df.writefloat(123.456)
        self.assertEqual(df.tell(), 8)
        df.seek(0)
        self.assertAlmostEqual(df.readfloat(), 123.456)
        self.assertEqual(df.tell(), 8)

    def test_read_write_str(self):
        """
        Tests reading and writing a string
        """
        df = self.get_in_memory()
        df.writestr('Testing')
        self.assertEqual(df.tell(), 10)
        df.seek(0)
        self.assertEqual(df.readstr(), 'Testing')
        self.assertEqual(df.tell(), 10)

        # Do a few additional asserts about the format we
        # expect 'em to have.
        df.seek(0)
        length = df.readshort()
        self.assertEqual(length, 7)
        df.seek(9)
        null = df.readuchar()
        self.assertEqual(null, 0)

    def test_write_str_too_long(self):
        """
        Tests writing a string too long for our string encoding method
        """
        df = self.get_in_memory()
        with self.assertRaises(IOError) as cm:
            df.writestr('a'*65536)
        self.assertIn('Maximum string length is currently 65535', str(cm.exception))

    def test_read_str_not_complete(self):
        """
        Tests a truncated string that's shorter than we expect it to be.
        """
        df = self.get_in_memory()
        df.writeshort(10)
        df.write(b'hi')
        df.seek(0)
        with self.assertRaises(LoadException) as cm:
            df.readstr()
        self.assertIn('Error reading string, expected', cm.exception.text)

    def test_read_write_empty_str(self):
        """
        Tests reading and writing an empty string (there's a special case for this
        in the code so we don't try to `read(0)`
        """
        df = self.get_in_memory()
        df.writestr('')
        self.assertEqual(df.tell(), 3)
        df.seek(0)
        self.assertEqual(df.readstr(), '')
        self.assertEqual(df.tell(), 3)
