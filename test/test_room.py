#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from advmap.data import Room, Group, Map, Connection, ConnectionEnd
from advmap.data import DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW, DIR_W, DIR_NW
from advmap.file import Savefile

class RoomTests(unittest.TestCase):
    """
    Tests for Room objects.  Note that a lot of Room logic actually ends
    up happening in the Map object - bad me!
    """

    def getSavefile(self):
        """
        Returns a Savefile object we can use to test load/save
        operations.
        """
        return Savefile('', in_memory=True)

    def get_basic_connection(self):
        """
        Creates two rooms and connects them.  Returns a
        tuple of (r1, r2, c)
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        c = r1.connect(DIR_N, r2)
        self.assertEqual(len(r1.conns), 1)
        self.assertIn(DIR_N, r1.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(len(r2.conns), 1)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r2.conns[DIR_S], c)
        return (r1, r2, c)

    def test_room_initialization(self):
        """
        Initialize a barebones room
        """
        r = Room(1, 2, 3)
        self.assertEqual(r.idnum, 1)
        self.assertEqual(r.x, 2)
        self.assertEqual(r.y, 3)
        self.assertEqual(r.name, '')
        self.assertEqual(r.notes, '')
        self.assertEqual(r.up, '')
        self.assertEqual(r.down, '')
        self.assertEqual(r.door_in, '')
        self.assertEqual(r.door_out, '')
        self.assertEqual(r.type, Room.TYPE_NORMAL)
        self.assertEqual(r.color, Room.COLOR_BW)
        self.assertEqual(r.offset_x, False)
        self.assertEqual(r.offset_y, False)
        self.assertEqual(len(r.loopbacks), 0)

    def test_duplicate(self):
        """
        Test our duplication method
        """
        r = Room(1, 2, 3)
        r.name = 'Room'
        r.notes = 'Notes'
        r.up = 'Up'
        r.down = 'Down'
        r.door_in = 'In'
        r.door_out = 'Out'
        r.type = Room.TYPE_FAINT
        r.color = Room.COLOR_CYAN
        r.offset_x = True
        r.offset_y = True
        r.set_loopback(DIR_S)
        r2 = r.duplicate()
        self.assertNotEqual(r, r2)
        self.assertEqual(r2.idnum, 1)
        self.assertEqual(r2.x, 2)
        self.assertEqual(r2.y, 3)
        self.assertEqual(r2.name, 'Room')
        self.assertEqual(r2.notes, 'Notes')
        self.assertEqual(r2.up, 'Up')
        self.assertEqual(r2.down, 'Down')
        self.assertEqual(r2.door_in, 'In')
        self.assertEqual(r2.door_out, 'Out')
        self.assertEqual(r2.type, Room.TYPE_FAINT)
        self.assertEqual(r2.color, Room.COLOR_CYAN)
        self.assertEqual(r2.offset_x, True)
        self.assertEqual(r2.offset_y, True)
        self.assertEqual(len(r2.loopbacks), 1)
        self.assertIn(DIR_S, r2.loopbacks)
        self.assertEqual(r2.loopbacks[DIR_S], True)

    def test_unexplored_true(self):
        """
        Test our special-case of unexplored room which should be `True`
        """
        r = Room(1, 0, 0)
        r.name = '(unexplored)'
        self.assertEqual(r.unexplored(), True)

    def test_unexplored_false(self):
        """
        Test our special-case of unexplored room which should be `False
        """
        r = Room(1, 0, 0)
        r.name = 'Room Five'
        self.assertEqual(r.unexplored(), False)

    def test_set_loopback_no_conns(self):
        """
        Setting a loopback where there isn't already a connection
        """
        r = Room(1, 0, 0)
        self.assertEqual(len(r.loopbacks), 0)
        r.set_loopback(DIR_N)
        self.assertEqual(len(r.loopbacks), 1)
        self.assertIn(DIR_N, r.loopbacks)
        self.assertEqual(r.loopbacks[DIR_N], True)

    def test_set_loopback_already_conn(self):
        """
        Attempt setting a loopback when there's already a connection
        in place; we'll NOT create the loopback.
        """
        r = Room(1, 0, 0)
        r2 = Room(2, 1, 1)
        r.connect(DIR_N, r2)
        self.assertEqual(len(r.loopbacks), 0)
        self.assertEqual(len(r.conns), 1)
        r.set_loopback(DIR_N)
        self.assertEqual(len(r.loopbacks), 0)
        self.assertEqual(len(r.conns), 1)

    def test_connect_opposite_direction(self):
        """
        Test to make sure connect will automatically go to the
        opposite direction
        """
        # Again, a shame that Python 2.7 doesn't have unittest.subTest
        for (direction, opposite) in [
                    (DIR_N, DIR_S),
                    (DIR_NE, DIR_SW),
                    (DIR_E, DIR_W),
                    (DIR_SE, DIR_NW),
                    (DIR_S, DIR_N),
                    (DIR_SW, DIR_NE),
                    (DIR_W, DIR_E),
                    (DIR_NW, DIR_SE),
                ]:
            r1 = Room(1, 1, 1)
            r2 = Room(2, 2, 2)
            c = r1.connect(direction, r2)
            self.assertEqual(len(r1.conns), 1)
            self.assertIn(direction, r1.conns)
            self.assertEqual(r1.conns[direction], c)
            self.assertEqual(len(r2.conns), 1)
            self.assertIn(opposite, r2.conns)
            self.assertEqual(r2.conns[opposite], c)

    def test_connect_specified_direction(self):
        """
        Test connecting with a specified direction rather than the
        implicit default.
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        c = r1.connect(DIR_N, r2, DIR_NW)
        self.assertEqual(len(r1.conns), 1)
        self.assertIn(DIR_N, r1.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(len(r2.conns), 1)
        self.assertIn(DIR_NW, r2.conns)
        self.assertEqual(r2.conns[DIR_NW], c)

    def test_connect_blocked_r1_loopback(self):
        """
        Test connecting where r1 blocks it with a loopback
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        r1.set_loopback(DIR_N)
        c = r1.connect(DIR_N, r2)
        self.assertEqual(c, None)
        self.assertEqual(len(r1.conns), 0)
        self.assertEqual(len(r2.conns), 0)

    def test_connect_blocked_r2_loopback(self):
        """
        Test connecting where r2 blocks it with a loopback
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        r2.set_loopback(DIR_S)
        c = r1.connect(DIR_N, r2)
        self.assertEqual(c, None)
        self.assertEqual(len(r1.conns), 0)
        self.assertEqual(len(r2.conns), 0)

    def test_connect_blocked_r1_connection(self):
        """
        Test connecting where r1 blocks it with a connection
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        r3 = Room(3, 3, 3)
        conn_first = r1.connect(DIR_N, r3)
        conn_new = r1.connect(DIR_N, r2)
        self.assertNotEqual(conn_first, None)
        self.assertEqual(conn_new, None)
        self.assertEqual(len(r1.conns), 1)
        self.assertEqual(len(r2.conns), 0)
        self.assertEqual(len(r3.conns), 1)
        self.assertIn(DIR_N, r1.conns)
        self.assertEqual(r1.conns[DIR_N], conn_first)
        self.assertIn(DIR_S, r3.conns)
        self.assertEqual(r3.conns[DIR_S], conn_first)

    def test_detach_without_conns_or_loopbacks(self):
        """
        Test detaching when there's nothing to detach
        """
        r1 = Room(1, 1, 1)
        with self.assertRaises(Exception) as cm:
            r1.detach(DIR_N)
        self.assertIn('No connections or loopbacks to detach', str(cm.exception))

    def test_detach_loopback(self):
        """
        Test detaching a loopback
        """
        r1 = Room(1, 1, 1)
        r1.set_loopback(DIR_N)
        self.assertEqual(len(r1.loopbacks), 1)
        self.assertIn(DIR_N, r1.loopbacks)
        self.assertEqual(r1.loopbacks[DIR_N], True)
        rv = r1.detach(DIR_N)
        self.assertEqual(rv, False)
        self.assertEqual(len(r1.loopbacks), 0)

    def test_detach_connection_basic(self):
        """
        Test detaching a basic connection.
        """
        (r1, r2, c) = self.get_basic_connection()
        rv = r1.detach(DIR_N)
        self.assertEqual(rv, True)
        self.assertEqual(len(r1.conns), 0)
        self.assertEqual(len(r2.conns), 0)

    def test_detach_connection_with_extra_no_delete_keep_primary(self):
        """
        Test detaching a connection which has two Ends onto
        the direction being detached, so the connection itself
        remains intact.  The primary connection direction does not change.
        """
        (r1, r2, c) = self.get_basic_connection()
        c.ends1[DIR_NE] = ConnectionEnd(r1, DIR_NE)
        r1.conns[DIR_NE] = c
        self.assertEqual(len(r1.conns), 2)
        self.assertIn(DIR_NE, r1.conns)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.dir2, DIR_S)
        rv = r1.detach(DIR_NE)
        self.assertEqual(rv, False)
        self.assertEqual(len(r1.conns), 1)
        self.assertIn(DIR_N, r1.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(len(r2.conns), 1)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r2.conns[DIR_S], c)

    def test_detach_connection_with_extra_no_delete_change_primary(self):
        """
        Test detaching a connection which has two Ends onto
        the direction being detached, so the connection itself
        remains intact.  The primary connection direction will change
        """
        (r1, r2, c) = self.get_basic_connection()
        c.ends1[DIR_NE] = ConnectionEnd(r1, DIR_NE)
        r1.conns[DIR_NE] = c
        self.assertEqual(len(r1.conns), 2)
        self.assertIn(DIR_NE, r1.conns)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.dir2, DIR_S)
        rv = r1.detach(DIR_N)
        self.assertEqual(rv, False)
        self.assertEqual(len(r1.conns), 1)
        self.assertIn(DIR_NE, r1.conns)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(c.dir1, DIR_NE)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(len(r2.conns), 1)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r2.conns[DIR_S], c)

    def test_detach_connection_with_extra_no_delete_change_primary_on_other_side_of_conn(self):
        """
        Test detaching a connection which has two Ends onto
        the direction being detached, so the connection itself
        remains intact.  The primary connection direction will change,
        on the 'other' side of the internal Connection structure
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        c = r2.connect(DIR_S, r1)

        self.assertEqual(len(r1.conns), 1)
        self.assertIn(DIR_N, r1.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(len(r2.conns), 1)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r2.conns[DIR_S], c)

        c.ends2[DIR_NE] = ConnectionEnd(r1, DIR_NE)
        r1.conns[DIR_NE] = c
        self.assertEqual(len(r1.conns), 2)
        self.assertIn(DIR_NE, r1.conns)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(c.dir2, DIR_N)
        self.assertEqual(c.dir1, DIR_S)
        rv = r1.detach(DIR_N)
        self.assertEqual(rv, False)
        self.assertEqual(len(r1.conns), 1)
        self.assertIn(DIR_NE, r1.conns)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(c.dir2, DIR_NE)
        self.assertEqual(c.dir1, DIR_S)
        self.assertEqual(len(r2.conns), 1)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r2.conns[DIR_S], c)

    def test_detach_connection_with_extra_on_far_side(self):
        """
        Test detaching a connection which has two Ends on
        the far side, so the connection should get removed regardless.
        """
        (r1, r2, c) = self.get_basic_connection()
        c.ends2[DIR_SW] = ConnectionEnd(r2, DIR_SW)
        r2.conns[DIR_SW] = c
        self.assertEqual(len(r2.conns), 2)
        self.assertIn(DIR_SW, r2.conns)
        self.assertEqual(r2.conns[DIR_SW], c)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.dir2, DIR_S)
        rv = r1.detach(DIR_N)
        self.assertEqual(rv, True)
        self.assertEqual(len(r1.conns), 0)
        self.assertEqual(len(r2.conns), 0)

    def test_get_loopback_exists(self):
        """
        Tests getting loopback when it does
        """
        r1 = Room(1, 1, 1)
        r1.set_loopback(DIR_N)
        self.assertEqual(r1.get_loopback(DIR_N), True)

    def test_get_loopback_does_not_exist(self):
        """
        Tests getting loopback when it doesn't
        """
        r1 = Room(1, 1, 1)
        self.assertEqual(r1.get_loopback(DIR_N), False)

    def test_get_conn_with_connection(self):
        """
        Tests getting a connection when one exists.
        """
        (r1, r2, c) = self.get_basic_connection()
        c_ret = r1.get_conn(DIR_N)
        self.assertEqual(c_ret, c)

    def test_get_conn_with_no_connection(self):
        """
        Tests getting a connection when one does not exist
        """
        r1 = Room(1, 1, 1)
        c = r1.get_conn(DIR_N)
        self.assertEqual(c, None)

    def test_in_group_with_when_not_in_group(self):
        """
        Tests group membership when the room isn't in a group
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        r3 = Room(3, 3, 3)
        g = Group(r2, r3)
        self.assertEqual(r1.in_group_with(r2), False)

    def test_in_group_with_when_target_not_in_group(self):
        """
        Tests group membership when the target isn't in a group
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        r3 = Room(3, 3, 3)
        g = Group(r1, r2)
        self.assertEqual(r1.in_group_with(r3), False)

    def test_in_group_with_when_not_in_same_group(self):
        """
        Tests group membership when the room isn't the same group
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        r3 = Room(3, 3, 3)
        r4 = Room(4, 4, 4)
        g1 = Group(r1, r2)
        g2 = Group(r3, r4)
        self.assertEqual(r1.in_group_with(r3), False)

    def test_in_group_with_when_in_same_group(self):
        """
        Tests group membership when the room is in the same group
        """
        r1 = Room(1, 1, 1)
        r2 = Room(2, 2, 2)
        g = Group(r1, r2)
        self.assertEqual(r1.in_group_with(r2), True)

    def test_increment_type(self):
        """
        Tests increment_type
        """
        # Shame about unittest.subTest not being in Py2
        r = Room(1, 1, 1)
        for (current, result) in [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 4),
                (4, 0),
                ]:
            self.assertEqual(r.type, current)
            r.increment_type()
            self.assertEqual(r.type, result)

    def test_increment_color(self):
        """
        Tests increment_color
        """
        # Shame about unittest.subTest not being in Py2
        r = Room(1, 1, 1)
        for (current, result) in [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 4),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 0),
                ]:
            self.assertEqual(r.color, current)
            r.increment_color()
            self.assertEqual(r.color, result)

    def test_save_basic_room_no_loopbacks_or_flags(self):
        """
        Test saving a basic room with no loopbacks or flags
        (note: connections are NOT saved with the Rooms)
        """
        df = self.getSavefile()
        r = Room(1, 2, 3)
        r.name = 'Room'
        r.type = Room.TYPE_FAINT
        r.color = Room.COLOR_GREEN
        r.up = 'Up'
        r.down = 'Down'
        r.door_in = 'In'
        r.door_out = 'Out'
        r.notes = 'Notes'
        r.save(df)
        df.seek(0)
        self.assertEqual(df.readshort(), 1)
        self.assertEqual(df.readuchar(), 2)
        self.assertEqual(df.readuchar(), 3)
        self.assertEqual(df.readstr(), 'Room')
        self.assertEqual(df.readuchar(), Room.TYPE_FAINT)
        self.assertEqual(df.readuchar(), Room.COLOR_GREEN)
        self.assertEqual(df.readstr(), 'Up')
        self.assertEqual(df.readstr(), 'Down')
        self.assertEqual(df.readstr(), 'In')
        self.assertEqual(df.readstr(), 'Out')
        self.assertEqual(df.readstr(), 'Notes')
        self.assertEqual(df.readuchar(), 0)
        self.assertEqual(df.readuchar(), 0)
        self.assertEqual(df.eof(), True)

    def test_save_basic_room_with_all_loopbacks_or_flags(self):
        """
        Test saving a basic room with all available loopbacks and
        flags (note: connections are NOT saved with the Rooms)
        """
        df = self.getSavefile()
        r = Room(1, 2, 3)
        r.name = 'Room'
        r.type = Room.TYPE_FAINT
        r.color = Room.COLOR_BLUE
        r.up = 'Up'
        r.down = 'Down'
        r.door_in = 'In'
        r.door_out = 'Out'
        r.notes = 'Notes'
        for direction in [DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S,
                DIR_SW, DIR_W, DIR_NW]:
            r.set_loopback(direction)
        r.offset_x = True
        r.offset_y = True
        r.save(df)
        df.seek(0)
        self.assertEqual(df.readshort(), 1)
        self.assertEqual(df.readuchar(), 2)
        self.assertEqual(df.readuchar(), 3)
        self.assertEqual(df.readstr(), 'Room')
        self.assertEqual(df.readuchar(), Room.TYPE_FAINT)
        self.assertEqual(df.readuchar(), Room.COLOR_BLUE)
        self.assertEqual(df.readstr(), 'Up')
        self.assertEqual(df.readstr(), 'Down')
        self.assertEqual(df.readstr(), 'In')
        self.assertEqual(df.readstr(), 'Out')
        self.assertEqual(df.readstr(), 'Notes')
        self.assertEqual(df.readuchar(), 3)
        self.assertEqual(df.readuchar(), 255)
        self.assertEqual(df.eof(), True)

    def test_load_v2_with_no_flags(self):
        """
        Tests loading a v2 room with no flags
        """
        df = self.getSavefile()
        df.writeshort(1)
        df.writeuchar(2)
        df.writeuchar(3)
        df.writestr('Room')
        df.writeuchar(5) # v2 code for "Faint"
        df.writestr('Up')
        df.writestr('Down')
        df.writestr('In')
        df.writestr('Out')
        df.writestr('Notes')
        df.writeuchar(0)
        df.seek(0)
        r = Room.load(df, 2)
        self.assertEqual(df.eof(), True)
        self.assertEqual(r.idnum, 1)
        self.assertEqual(r.x, 2)
        self.assertEqual(r.y, 3)
        self.assertEqual(r.name, 'Room')
        self.assertEqual(r.notes, 'Notes')
        self.assertEqual(r.up, 'Up')
        self.assertEqual(r.down, 'Down')
        self.assertEqual(r.door_in, 'In')
        self.assertEqual(r.door_out, 'Out')
        self.assertEqual(r.type, Room.TYPE_FAINT)
        self.assertEqual(r.color, Room.COLOR_BW)
        self.assertEqual(r.offset_x, False)
        self.assertEqual(r.offset_y, False)
        self.assertEqual(len(r.loopbacks), 0)

    def test_load_v2_with_all_flags(self):
        """
        Tests loading a v2 room with all flags
        """
        df = self.getSavefile()
        df.writeshort(1)
        df.writeuchar(2)
        df.writeuchar(3)
        df.writestr('Room')
        df.writeuchar(5) # v2 code for "Faint"
        df.writestr('Up')
        df.writestr('Down')
        df.writestr('In')
        df.writestr('Out')
        df.writestr('Notes')
        df.writeuchar(3)
        df.seek(0)
        r = Room.load(df, 2)
        self.assertEqual(df.eof(), True)
        self.assertEqual(r.idnum, 1)
        self.assertEqual(r.x, 2)
        self.assertEqual(r.y, 3)
        self.assertEqual(r.name, 'Room')
        self.assertEqual(r.notes, 'Notes')
        self.assertEqual(r.up, 'Up')
        self.assertEqual(r.down, 'Down')
        self.assertEqual(r.door_in, 'In')
        self.assertEqual(r.door_out, 'Out')
        self.assertEqual(r.type, Room.TYPE_FAINT)
        self.assertEqual(r.color, Room.COLOR_BW)
        self.assertEqual(r.offset_x, True)
        self.assertEqual(r.offset_y, True)
        self.assertEqual(len(r.loopbacks), 0)

    def test_load_v3_with_no_flags_and_loopbacks(self):
        """
        Tests loading a v3 room with no flags and loopbacks
        """
        df = self.getSavefile()
        df.writeshort(1)
        df.writeuchar(2)
        df.writeuchar(3)
        df.writestr('Room')
        df.writeuchar(5) # v3 code for Faint
        df.writestr('Up')
        df.writestr('Down')
        df.writestr('In')
        df.writestr('Out')
        df.writestr('Notes')
        df.writeuchar(0)
        df.writeuchar(0)
        df.seek(0)
        r = Room.load(df, 3)
        self.assertEqual(df.eof(), True)
        self.assertEqual(r.idnum, 1)
        self.assertEqual(r.x, 2)
        self.assertEqual(r.y, 3)
        self.assertEqual(r.name, 'Room')
        self.assertEqual(r.notes, 'Notes')
        self.assertEqual(r.up, 'Up')
        self.assertEqual(r.down, 'Down')
        self.assertEqual(r.door_in, 'In')
        self.assertEqual(r.door_out, 'Out')
        self.assertEqual(r.type, Room.TYPE_FAINT)
        self.assertEqual(r.color, Room.COLOR_BW)
        self.assertEqual(r.offset_x, False)
        self.assertEqual(r.offset_y, False)
        self.assertEqual(len(r.loopbacks), 0)

    def test_load_v3_with_all_flags_and_loopbacks(self):
        """
        Tests loading a v3 room with all flags and loopback
        """
        df = self.getSavefile()
        df.writeshort(1)
        df.writeuchar(2)
        df.writeuchar(3)
        df.writestr('Room')
        df.writeuchar(5) # v3 code for Faint
        df.writestr('Up')
        df.writestr('Down')
        df.writestr('In')
        df.writestr('Out')
        df.writestr('Notes')
        df.writeuchar(3)
        df.writeuchar(255)
        df.seek(0)
        r = Room.load(df, 3)
        self.assertEqual(df.eof(), True)
        self.assertEqual(r.idnum, 1)
        self.assertEqual(r.x, 2)
        self.assertEqual(r.y, 3)
        self.assertEqual(r.name, 'Room')
        self.assertEqual(r.notes, 'Notes')
        self.assertEqual(r.up, 'Up')
        self.assertEqual(r.down, 'Down')
        self.assertEqual(r.door_in, 'In')
        self.assertEqual(r.door_out, 'Out')
        self.assertEqual(r.type, Room.TYPE_FAINT)
        self.assertEqual(r.color, Room.COLOR_BW)
        self.assertEqual(r.offset_x, True)
        self.assertEqual(r.offset_y, True)
        self.assertEqual(len(r.loopbacks), 8)
        for direction in [DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S,
                DIR_SW, DIR_W, DIR_NW]:
            self.assertEqual(r.get_loopback(direction), True)

    def test_load_v3_type_color_changes(self):
        """
        v8 changed our type/color attributes to be split, as opposed to
        having everything in a single "type" field (the type field has
        been otherwise unchanged since v1).  This tests our translation,
        to make sure that old maps get assigned the proper colors.
        """
        old_to_new = [
                (0, (Room.TYPE_NORMAL, Room.COLOR_BW)), # Normal
                (1, (Room.TYPE_NORMAL, Room.COLOR_GREEN)), # Green
                (2, (Room.TYPE_LABEL, Room.COLOR_BW)), # Label
                (3, (Room.TYPE_NORMAL, Room.COLOR_BLUE)), # Blue
                (4, (Room.TYPE_NORMAL, Room.COLOR_RED)), # Red
                (5, (Room.TYPE_FAINT, Room.COLOR_BW)), # Faint
                (6, (Room.TYPE_NORMAL, Room.COLOR_YELLOW)), # Yellow
                (7, (Room.TYPE_NORMAL, Room.COLOR_PURPLE)), # Purple
                (8, (Room.TYPE_NORMAL, Room.COLOR_CYAN)), # Cyan
                (9, (Room.TYPE_DARK, Room.COLOR_BW)), # Dark
                (10, (Room.TYPE_NORMAL, Room.COLOR_BW)), # Invalid, should default to Normal/BW
            ]

        # Alas for not having unittest.subTest in py2
        for (orig_type, (new_type, new_color)) in old_to_new:
            df = self.getSavefile()
            df.writeshort(1)
            df.writeuchar(2)
            df.writeuchar(3)
            df.writestr('Room')
            df.writeuchar(orig_type)
            df.writestr('Up')
            df.writestr('Down')
            df.writestr('In')
            df.writestr('Out')
            df.writestr('Notes')
            df.writeuchar(0)
            df.writeuchar(0)
            df.seek(0)
            r = Room.load(df, 3)
            self.assertEqual(df.eof(), True)
            self.assertEqual(r.idnum, 1)
            self.assertEqual(r.x, 2)
            self.assertEqual(r.y, 3)
            self.assertEqual(r.name, 'Room')
            self.assertEqual(r.notes, 'Notes')
            self.assertEqual(r.up, 'Up')
            self.assertEqual(r.down, 'Down')
            self.assertEqual(r.door_in, 'In')
            self.assertEqual(r.door_out, 'Out')
            self.assertEqual(r.type, new_type)
            self.assertEqual(r.color, new_color)
            self.assertEqual(r.offset_x, False)
            self.assertEqual(r.offset_y, False)
            self.assertEqual(len(r.loopbacks), 0)

    def test_load_v8_basic(self):
        """
        Tests loading a basic v8 room (with color specified)
        """
        df = self.getSavefile()
        df.writeshort(1)
        df.writeuchar(2)
        df.writeuchar(3)
        df.writestr('Room')
        df.writeuchar(Room.TYPE_DARK)
        df.writeuchar(Room.COLOR_ORANGE)
        df.writestr('Up')
        df.writestr('Down')
        df.writestr('In')
        df.writestr('Out')
        df.writestr('Notes')
        df.writeuchar(0)
        df.writeuchar(0)
        df.seek(0)
        r = Room.load(df, 8)
        self.assertEqual(df.eof(), True)
        self.assertEqual(r.idnum, 1)
        self.assertEqual(r.x, 2)
        self.assertEqual(r.y, 3)
        self.assertEqual(r.name, 'Room')
        self.assertEqual(r.notes, 'Notes')
        self.assertEqual(r.up, 'Up')
        self.assertEqual(r.down, 'Down')
        self.assertEqual(r.door_in, 'In')
        self.assertEqual(r.door_out, 'Out')
        self.assertEqual(r.type, Room.TYPE_DARK)
        self.assertEqual(r.color, Room.COLOR_ORANGE)
        self.assertEqual(r.offset_x, False)
        self.assertEqual(r.offset_y, False)
        self.assertEqual(len(r.loopbacks), 0)
