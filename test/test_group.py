#!/usr/bin/env python2
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from advmap.data import Room, Group, Map
from advmap.file import Savefile, LoadException

class GroupTests(unittest.TestCase):
    """
    Tests for Group objects
    """

    def setUp(self):
        """
        All our tests are going to require at least two rooms and
        a group, so set that up.  Also set up a third room, just
        for kicks.
        """
        self.r1 = Room(1, 0, 0)
        self.r2 = Room(2, 0, 1)
        self.r3 = Room(3, 0, 2)
        self.g = Group(self.r1, self.r2)

    def getSavefile(self):
        """
        Returns a Savefile object we can use to test load/save
        operations.
        """
        return Savefile('', in_memory=True)

    def test_group_initialization(self):
        """
        Initialize a barebones group
        """
        self.assertEqual(self.g.rooms, [self.r1, self.r2])
        self.assertEqual(self.g.style, Group.STYLE_NORMAL)
        self.assertEqual(self.r1.group, self.g)
        self.assertEqual(self.r2.group, self.g)

    def test_initialization_with_one_group(self):
        """
        Tests initializing with only one room
        """
        with self.assertRaises(Exception) as cm:
            g = Group(self.r1, self.r1)
        self.assertIn('Cannot create a group with only one room', str(cm.exception))

    def test_get_rooms(self):
        """
        Make sure our `get_rooms` func returns rooms
        """
        self.assertEqual(self.g.get_rooms(), [self.r1, self.r2])

    def test_has_room_true(self):
        """
        Make sure `has_room` returns `True` when it should
        """
        self.assertEqual(self.g.has_room(self.r1), True)

    def test_has_room_false(self):
        """
        Make sure `has_room` returns `True` when it should
        """
        self.assertEqual(self.g.has_room(self.r3), False)

    def test_add_room_success(self):
        """
        Make sure adding a new room works
        """
        self.g.add_room(self.r3)
        self.assertEqual(self.g.rooms, [self.r1, self.r2, self.r3])
        self.assertEqual(self.r3.group, self.g)
        self.assertEqual(self.g.has_room(self.r3), True)

    def test_add_room_fail(self):
        """
        Adding a room already in the group should do nothing
        """
        self.g.add_room(self.r1)
        self.assertEqual(self.g.rooms, [self.r1, self.r2])
        self.assertEqual(self.r3.group, None)

    def test_del_room_should_remain(self):
        """
        Test deleting a room when doing so should leave the Group in place
        """
        self.g.add_room(self.r3)
        retval = self.g.del_room(self.r1)
        self.assertEqual(retval, False)
        self.assertEqual(self.g.rooms, [self.r2, self.r3])
        self.assertEqual(self.r1.group, None)
        self.assertEqual(self.r2.group, self.g)
        self.assertEqual(self.r3.group, self.g)

    def test_del_room_should_delete(self):
        """
        Test deleting a room when doing so should cause the Group to get
        deleted.
        """
        retval = self.g.del_room(self.r1)
        self.assertEqual(retval, True)
        self.assertEqual(self.g.rooms, [self.r2])

    def test_del_room_not_in_group(self):
        """
        Attempting to delete a room not actually in the group should do
        nothing.
        """
        retval = self.g.del_room(self.r3)
        self.assertEqual(retval, False)
        self.assertEqual(self.g.rooms, [self.r1, self.r2])

    def test_increment_style(self):
        """
        Test to make sure our `increment_style` does the right thing
        """
        # Currently there are nine total styles
        # Alas, subTests were implemented in Python 3.4 and never got backported to 2.7
        for (current, result) in [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 4),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 8),
                (8, 0),
                ]:
            self.assertEqual(self.g.style, current)
            self.g.increment_style()
            self.assertEqual(self.g.style, result)

    def test_save_only_one_room(self):
        """
        Attempting to save a group should raise an Exception if there's
        only one room in it.
        """
        self.g.del_room(self.r1)
        with self.assertRaises(Exception) as cm:
            self.g.save(self.getSavefile())
        self.assertIn('a group cannot consist of only one room', str(cm.exception))

    def test_save_two_rooms(self):
        """
        Test saving a group with two rooms
        """
        df = self.getSavefile()
        self.g.save(df)
        df.seek(0)
        self.assertEqual(df.readshort(), 2)
        self.assertEqual(df.readuchar(), Group.STYLE_NORMAL)
        self.assertEqual(df.readshort(), 1)
        self.assertEqual(df.readshort(), 2)
        self.assertEqual(df.eof(), True)

    def test_save_three_rooms_and_incremented_style(self):
        """
        Test saving a group with three rooms and an incremented style
        """
        self.g.add_room(self.r3)
        self.g.increment_style()
        df = self.getSavefile()
        self.g.save(df)
        df.seek(0)
        self.assertEqual(df.readshort(), 3)
        self.assertEqual(df.readuchar(), Group.STYLE_RED)
        self.assertEqual(df.readshort(), 1)
        self.assertEqual(df.readshort(), 2)
        self.assertEqual(df.readshort(), 3)
        self.assertEqual(df.eof(), True)

    def test_load_v5(self):
        """
        Test loading a v5 group (v6, so far, has been the only change
        to groups).
        
        Note that we need a full Map object layout in order to do this,
        since it needs to load rooms by the Map's ID index.
        """
        mapobj = Map('Testing')
        r1 = mapobj.add_room_at(0, 0, 'Room 1')
        r2 = mapobj.add_room_at(1, 0, 'Room 2')
        g = Group(r1, r2)
        df = self.getSavefile()
        df.writeshort(2)
        df.writeshort(r1.idnum)
        df.writeshort(r2.idnum)
        df.seek(0)
        new_g = Group.load(df, mapobj, 5)
        self.assertEqual(df.eof(), True)
        self.assertEqual(new_g.style, Group.STYLE_NORMAL)
        self.assertEqual(len(new_g.rooms), 2)

    def test_load_v6_two_rooms(self):
        """
        Tests loading a v6 Group with two rooms
        """
        mapobj = Map('Testing')
        r1 = mapobj.add_room_at(0, 0, 'Room 1')
        r2 = mapobj.add_room_at(1, 0, 'Room 2')
        g = Group(r1, r2)
        g.increment_style()
        df = self.getSavefile()
        df.writeshort(2)
        df.writeuchar(g.style)
        df.writeshort(r1.idnum)
        df.writeshort(r2.idnum)
        df.seek(0)
        new_g = Group.load(df, mapobj, 6)
        self.assertEqual(df.eof(), True)
        self.assertEqual(new_g.style, Group.STYLE_RED)
        self.assertEqual(len(new_g.rooms), 2)

    def test_load_v6_three_rooms(self):
        """
        Tests loading a v6 Group with three rooms
        """
        mapobj = Map('Testing')
        r1 = mapobj.add_room_at(0, 0, 'Room 1')
        r2 = mapobj.add_room_at(1, 0, 'Room 2')
        r3 = mapobj.add_room_at(2, 0, 'Room 3')
        g = Group(r1, r2)
        g.add_room(r3)
        df = self.getSavefile()
        df.writeshort(3)
        df.writeuchar(g.style)
        df.writeshort(r1.idnum)
        df.writeshort(r2.idnum)
        df.writeshort(r3.idnum)
        df.seek(0)
        new_g = Group.load(df, mapobj, 6)
        self.assertEqual(df.eof(), True)
        self.assertEqual(new_g.style, Group.STYLE_NORMAL)
        self.assertEqual(len(new_g.rooms), 3)

    def test_load_v6_without_minimum_rooms(self):
        """
        Tests attempting to load a v6 group definition without at least two rooms.
        """
        df = self.getSavefile()
        df.writeshort(1)
        df.writeuchar(Group.STYLE_NORMAL)
        df.writeshort(42)
        df.seek(0)
        mapobj = Map('Testing')
        with self.assertRaises(LoadException) as cm:
            new_g = Group.load(df, mapobj, 6)
        self.assertIn('Group stated it had only 1 rooms', cm.exception.text)

    def test_load_v6_with_unknown_room(self):
        """
        Tests loading a v6 Group with a room the Map object doesn't know about
        """
        mapobj = Map('Testing')
        df = self.getSavefile()
        df.writeshort(2)
        df.writeuchar(Group.STYLE_NORMAL)
        df.writeshort(42)
        df.writeshort(43)
        df.seek(0)
        with self.assertRaises(LoadException) as cm:
            new_g = Group.load(df, mapobj, 6)
        self.assertIn('Room 42 does not exist while loading group', cm.exception.text)
