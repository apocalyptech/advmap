#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import os
import tempfile
import unittest
from advmap.data import Game, Map, SAVEFILE_VER
from advmap.file import Savefile, LoadException

class GameTests(unittest.TestCase):
    """
    Tests for our main Game class
    """

    def getSavefile(self):
        """
        Returns a Savefile object we can use to test load/save
        operations.
        """
        return Savefile('', in_memory=True)

    def setUp(self):
        """
        Create a Game object for all our tests
        """
        self.g = Game('Game')

    def test_initialization(self):
        """
        Test initialization
        """
        self.assertEqual(self.g.name, 'Game')
        self.assertEqual(len(self.g.maps), 0)

    def test_add_map_obj(self):
        """
        Test adding a Map object
        """
        m1 = Map('Map 1')
        m2 = Map('Map 2')
        self.assertEqual(self.g.add_map_obj(m1), 0)
        self.assertEqual(len(self.g.maps), 1)
        self.assertEqual(self.g.add_map_obj(m2), 1)
        self.assertEqual(len(self.g.maps), 2)
        self.assertEqual(self.g.maps[0], m1)
        self.assertEqual(self.g.maps[1], m2)

    def test_add_map(self):
        """
        Test adding a map by name
        """
        (index, obj) = self.g.add_map('Map Name')
        self.assertEqual(len(self.g.maps), 1)
        self.assertEqual(index, 0)
        self.assertEqual(obj.name, 'Map Name')
        self.assertEqual(self.g.maps[0], obj)

    def test_replace_maps(self):
        """
        Test replacing our maps list.
        """
        m1 = Map('Map 1')
        m2 = Map('Map 2')
        self.g.add_map_obj(m1)
        self.assertEqual(self.g.maps[0], m1)
        self.g.replace_maps([m2])
        self.assertEqual(self.g.maps[0], m2)

    def test_save_no_maps(self):
        """
        Test saving when we have no actual maps
        """
        g = Game('Game')

        df = self.getSavefile()
        g._save(df)
        df.seek(0)
        self.assertEqual(df.read(6), b'ADVMAP')
        self.assertEqual(df.readshort(), SAVEFILE_VER)
        self.assertEqual(df.readstr(), 'Game')
        self.assertEqual(df.readshort(), 0)
        self.assertEqual(df.eof(), True)

    def test_save_single_map(self):
        """
        Test saving when we have a single map
        """
        g = Game('Game')
        g.add_map('Map')

        df = self.getSavefile()
        g._save(df)
        df.seek(0)
        self.assertEqual(df.read(6), b'ADVMAP')
        self.assertEqual(df.readshort(), SAVEFILE_VER)
        self.assertEqual(df.readstr(), 'Game')
        self.assertEqual(df.readshort(), 1)

        self.assertEqual(df.readstr(), 'Map')
        self.assertEqual(df.readuchar(), 9)
        self.assertEqual(df.readuchar(), 9)
        self.assertEqual(df.readshort(), 0)
        self.assertEqual(df.readshort(), 0)
        self.assertEqual(df.readshort(), 0)

        self.assertEqual(df.eof(), True)

    def test_save_by_filename(self):
        """
        Test saving to filename
        """

        g = Game('Game')
        (handle, pathname) = tempfile.mkstemp()
        os.close(handle)
        try:
            g.save(pathname)
            df = Savefile(pathname)
            df.open_r()
            self.assertEqual(df.read(6), b'ADVMAP')
            self.assertEqual(df.readshort(), SAVEFILE_VER)
            self.assertEqual(df.readstr(), 'Game')
            self.assertEqual(df.readshort(), 0)
            self.assertEqual(df.eof(), True)
            df.close()
        finally:
            os.unlink(pathname)

    def test_load_no_maps(self):
        """
        Test loading without any maps
        """
        df = self.getSavefile()
        df.write(b'ADVMAP')
        df.writeshort(SAVEFILE_VER)
        df.writestr('Game')
        df.writeshort(0)
        df.seek(0)

        game = Game._load(df)
        self.assertEqual(df.eof(), True)
        self.assertEqual(game.name, 'Game')
        self.assertEqual(len(game.maps), 0)

    def test_load_single_map(self):
        """
        Test loading with a single map
        """
        df = self.getSavefile()
        df.write(b'ADVMAP')
        df.writeshort(SAVEFILE_VER)
        df.writestr('Game')
        df.writeshort(1)

        df.writestr('Map')
        df.writeuchar(9)
        df.writeuchar(9)
        df.writeshort(0)
        df.writeshort(0)
        df.writeshort(0)

        df.seek(0)

        game = Game._load(df)
        self.assertEqual(df.eof(), True)
        self.assertEqual(game.name, 'Game')
        self.assertEqual(len(game.maps), 1)
        self.assertEqual(game.maps[0].name, 'Map')

    def test_load_invalid_map_file(self):
        """
        Test loading when the file isn't valid
        """
        df = self.getSavefile()
        df.write(b'NOTAMAPFILE')
        df.seek(0)

        with self.assertRaises(LoadException) as cm:
            Game._load(df)
        self.assertIn('Invalid Map File specified', cm.exception.text)

    def test_load_empty_map_file(self):
        """
        Test loading when the file isn't valid
        """
        df = self.getSavefile()
        with self.assertRaises(LoadException) as cm:
            Game._load(df)
        self.assertIn('Invalid Map File specified', cm.exception.text)

    def test_load_version_too_high(self):
        """
        Test loading when the mapfile version is higher than we understand
        """
        df = self.getSavefile()
        df.write(b'ADVMAP')
        df.writeshort(SAVEFILE_VER+1)
        df.writestr('Game')
        df.writeshort(0)
        df.seek(0)

        with self.assertRaises(LoadException) as cm:
            game = Game._load(df)
        self.assertIn('Map file is version', cm.exception.text)

    def test_load_from_filename(self):
        """
        Test loading from a filename
        """
        (handle, pathname) = tempfile.mkstemp()
        os.close(handle)
        try:
            df = Savefile(pathname)
            df.open_w()
            df.write(b'ADVMAP')
            df.writeshort(SAVEFILE_VER)
            df.writestr('Game')
            df.writeshort(0)
            df.close()

            g = Game.load(pathname)
            self.assertEqual(g.name, 'Game')
            self.assertEqual(len(g.maps), 0)
        finally:
            os.unlink(pathname)

