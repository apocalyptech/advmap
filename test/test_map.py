#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from advmap.data import Map, Connection, ConnectionEnd, Room, Group
from advmap.data import DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW, DIR_W, DIR_NW
from advmap.file import Savefile, LoadException

class MapTests(unittest.TestCase):
    """
    Tests for our main Map class
    """

    def getSavefile(self):
        """
        Returns a Savefile object we can use to test load/save
        operations.
        """
        return Savefile('', in_memory=True)

    def test_initialization(self):
        """
        Tests basic initialization
        """
        mapobj = Map('Map')
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(len(mapobj.rooms), 0)
        self.assertEqual(len(mapobj.roomxy), 9)
        for i in range(9):
            with self.subTest(i=i):
                self.assertEqual(len(mapobj.roomxy[i]), 9)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertEqual(mapobj.cur_id, 0)

    def test_set_map_size(self):
        """
        Test of `set_map_size`
        """
        # Populate with a bunch of data which should get wiped
        # out by the call.
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(0, 0, 'Room 1')
        r2 = mapobj.add_room_at(1, 1, 'Room 2')
        mapobj.connect(r1, DIR_SE, r2)
        mapobj.group_rooms(r1, r2)

        mapobj.set_map_size(4, 4)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(len(mapobj.rooms), 0)
        self.assertEqual(len(mapobj.roomxy), 4)
        for i in range(4):
            with self.subTest(i=i):
                self.assertEqual(len(mapobj.roomxy[i]), 4)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertEqual(mapobj.cur_id, 0)

    def test_duplicate_same_name(self):
        """
        Test a simple duplication where the map has the same name
        """
        original = Map('Original')
        new = original.duplicate()
        self.assertEqual(new.name, 'Original')

    def test_duplicate_new_name(self):
        """
        Test a simple duplication where the map has a new name
        """
        original = Map('Original')
        new = original.duplicate(newname='New')
        self.assertEqual(new.name, 'New')

    def test_duplicate_single_room(self):
        """
        Test duplication of a map with a single room.
        """
        original = Map('Original')
        orig_room = original.add_room_at(1, 2, 'Room')
        new = original.duplicate()
        self.assertEqual(len(new.rooms), 1)
        new_room = new.get_room_at(1, 2)
        self.assertNotEqual(orig_room, new_room)
        self.assertEqual(new_room.name, 'Room')
        self.assertEqual(new_room.x, 1)
        self.assertEqual(new_room.y, 2)
        self.assertEqual(new_room.group, None)
        self.assertEqual(new.roomxy[2][1], new_room)
        self.assertEqual(new.rooms[orig_room.idnum], new_room)

    def test_duplicate_two_rooms(self):
        """
        Test duplication of a map with two rooms.
        """
        original = Map('Original')
        orig_room1 = original.add_room_at(0, 0, 'Room1')
        orig_room2 = original.add_room_at(1, 1, 'Room2')
        new = original.duplicate()
        self.assertEqual(len(new.rooms), 2)
        new_room1 = new.get_room_at(0, 0)
        self.assertNotEqual(orig_room1, new_room1)
        self.assertEqual(new_room1.name, 'Room1')
        self.assertEqual(new_room1.group, None)
        self.assertEqual(new.roomxy[0][0], new_room1)
        self.assertEqual(new.rooms[orig_room1.idnum], new_room1)
        new_room2 = new.get_room_at(1, 1)
        self.assertNotEqual(orig_room2, new_room2)
        self.assertEqual(new_room2.name, 'Room2')
        self.assertEqual(new_room2.group, None)
        self.assertEqual(new.roomxy[1][1], new_room2)
        self.assertEqual(new.rooms[orig_room2.idnum], new_room2)

    def test_duplicate_one_connection_symmetric_basic(self):
        """
        Test duplication with a single symmetric connection using the
        connection defaults
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        c = original.connect(r1, DIR_N, r2, DIR_S)
        new = original.duplicate()
        self.assertEqual(len(new.conns), 1)
        new_c = new.conns[0]
        self.assertNotEqual(c, new_c)
        self.assertNotEqual(c.r1, new_c.r1)
        self.assertNotEqual(c.r2, new_c.r2)
        self.assertEqual(new_c.r1.idnum, r1.idnum)
        self.assertEqual(new_c.dir1, DIR_N)
        self.assertEqual(new_c.r2.idnum, r2.idnum)
        self.assertEqual(new_c.dir2, DIR_S)
        self.assertEqual(new_c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(new_c.symmetric, True)
        self.assertEqual(len(new_c.ends1), 1)
        self.assertEqual(len(new_c.ends2), 1)
        for ends in [new_c.ends1, new_c.ends2]:
            for end in ends.values():
                with self.subTest(end=end):
                    self.assertEqual(end.conn_type, ConnectionEnd.CONN_REGULAR)
                    self.assertEqual(end.render_type, ConnectionEnd.RENDER_REGULAR)
                    self.assertEqual(end.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_duplicate_one_connection_symmetric_changed(self):
        """
        Test duplication with a single symmetric connection whose
        attributes have all been changed from the defaults.
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        c = original.connect(r1, DIR_N, r2, DIR_S)
        c.set_ladder(r1, DIR_N)
        c.set_render_midpoint_a(r1, DIR_N);
        c.set_stub_length(r1, DIR_N, 3);
        c.set_oneway_b();
        new = original.duplicate()
        self.assertEqual(len(new.conns), 1)
        new_c = new.conns[0]
        self.assertNotEqual(c, new_c)
        self.assertNotEqual(c.r1, new_c.r1)
        self.assertNotEqual(c.r2, new_c.r2)
        self.assertEqual(new_c.r1.idnum, r1.idnum)
        self.assertEqual(new_c.dir1, DIR_N)
        self.assertEqual(new_c.r2.idnum, r2.idnum)
        self.assertEqual(new_c.dir2, DIR_S)
        self.assertEqual(new_c.passage, Connection.PASS_ONEWAY_B)
        self.assertEqual(new_c.symmetric, True)
        self.assertEqual(len(new_c.ends1), 1)
        self.assertEqual(len(new_c.ends2), 1)
        for ends in [new_c.ends1, new_c.ends2]:
            for end in ends.values():
                with self.subTest(end=end):
                    self.assertEqual(end.conn_type, ConnectionEnd.CONN_LADDER)
                    self.assertEqual(end.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
                    self.assertEqual(end.stub_length, 3)

    def test_duplicate_one_connection_nonsymmetric_r1_changed(self):
        """
        Test duplication with a single nonsymmetric connection whose
        r1 attributes have all been changed from the defaults.
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        c = original.connect(r1, DIR_N, r2, DIR_S)
        c.set_symmetric(False)
        c.set_ladder(r1, DIR_N)
        c.set_render_midpoint_a(r1, DIR_N);
        c.set_stub_length(r1, DIR_N, 3);
        new = original.duplicate()
        self.assertEqual(len(new.conns), 1)
        new_c = new.conns[0]
        self.assertNotEqual(c, new_c)
        self.assertNotEqual(c.r1, new_c.r1)
        self.assertNotEqual(c.r2, new_c.r2)
        self.assertEqual(new_c.r1.idnum, r1.idnum)
        self.assertEqual(new_c.dir1, DIR_N)
        self.assertEqual(new_c.r2.idnum, r2.idnum)
        self.assertEqual(new_c.dir2, DIR_S)
        self.assertEqual(new_c.symmetric, False)
        self.assertEqual(len(new_c.ends1), 1)
        self.assertEqual(len(new_c.ends2), 1)
        self.assertEqual(new_c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(new_c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(new_c.ends1[DIR_N].stub_length, 3)
        self.assertEqual(new_c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(new_c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(new_c.ends2[DIR_S].stub_length, ConnectionEnd.STUB_REGULAR)

    def test_duplicate_one_connection_nonsymmetric_r2_changed(self):
        """
        Test duplication with a single nonsymmetric connection whose
        r2 attributes have all been changed from the defaults.
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        c = original.connect(r1, DIR_N, r2, DIR_S)
        c.set_symmetric(False)
        c.set_ladder(r2, DIR_S)
        c.set_render_midpoint_a(r2, DIR_S);
        c.set_stub_length(r2, DIR_S, 3);
        new = original.duplicate()
        self.assertEqual(len(new.conns), 1)
        new_c = new.conns[0]
        self.assertNotEqual(c, new_c)
        self.assertNotEqual(c.r1, new_c.r1)
        self.assertNotEqual(c.r2, new_c.r2)
        self.assertEqual(new_c.r1.idnum, r1.idnum)
        self.assertEqual(new_c.dir1, DIR_N)
        self.assertEqual(new_c.r2.idnum, r2.idnum)
        self.assertEqual(new_c.dir2, DIR_S)
        self.assertEqual(new_c.symmetric, False)
        self.assertEqual(len(new_c.ends1), 1)
        self.assertEqual(len(new_c.ends2), 1)
        self.assertEqual(new_c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(new_c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(new_c.ends1[DIR_N].stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(new_c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(new_c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(new_c.ends2[DIR_S].stub_length, 3)

    def test_duplicate_one_connection_symmetric_two_extras(self):
        """
        Test duplication with a single symmetric connection using the
        connection defaults, with two extra ends, one on each side
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        c = original.connect(r1, DIR_N, r2, DIR_S)
        c.connect_extra(r1, DIR_NE)
        c.connect_extra(r2, DIR_SW)
        new = original.duplicate()
        self.assertEqual(len(new.conns), 1)
        new_c = new.conns[0]
        self.assertNotEqual(c, new_c)
        self.assertNotEqual(c.r1, new_c.r1)
        self.assertNotEqual(c.r2, new_c.r2)
        self.assertEqual(new_c.r1.idnum, r1.idnum)
        self.assertEqual(new_c.dir1, DIR_N)
        self.assertEqual(new_c.r2.idnum, r2.idnum)
        self.assertEqual(new_c.dir2, DIR_S)
        self.assertEqual(len(new_c.ends1), 2)
        self.assertEqual(len(new_c.ends2), 2)
        for ends in [new_c.ends1, new_c.ends2]:
            for end in ends.values():
                with self.subTest(end=end):
                    self.assertEqual(end.conn_type, ConnectionEnd.CONN_REGULAR)
                    self.assertEqual(end.render_type, ConnectionEnd.RENDER_REGULAR)
                    self.assertEqual(end.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_duplicate_one_connection_nonsymmetric_three_ends(self):
        """
        Test duplication with a single nonsymmetric connection with
        an extra end.  Each end will have unique attributes
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        c = original.connect(r1, DIR_N, r2, DIR_S)
        c.connect_extra(r1, DIR_NE)
        c.set_symmetric(False)
        c.set_ladder(r1, DIR_NE)
        c.set_render_midpoint_a(r1, DIR_NE);
        c.set_stub_length(r1, DIR_NE, 2);
        c.set_dotted(r2, DIR_S)
        c.set_render_midpoint_b(r2, DIR_S);
        c.set_stub_length(r2, DIR_S, 3);
        new = original.duplicate()
        self.assertEqual(len(new.conns), 1)
        new_c = new.conns[0]
        self.assertNotEqual(c, new_c)
        self.assertNotEqual(c.r1, new_c.r1)
        self.assertNotEqual(c.r2, new_c.r2)
        self.assertEqual(new_c.r1.idnum, r1.idnum)
        self.assertEqual(new_c.dir1, DIR_N)
        self.assertEqual(new_c.r2.idnum, r2.idnum)
        self.assertEqual(new_c.dir2, DIR_S)
        self.assertEqual(new_c.symmetric, False)
        self.assertEqual(len(new_c.ends1), 2)
        self.assertEqual(len(new_c.ends2), 1)
        self.assertEqual(new_c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(new_c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(new_c.ends1[DIR_N].stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(new_c.ends1[DIR_NE].conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(new_c.ends1[DIR_NE].render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(new_c.ends1[DIR_NE].stub_length, 2)
        self.assertEqual(new_c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_DOTTED)
        self.assertEqual(new_c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(new_c.ends2[DIR_S].stub_length, 3)

    def test_duplicate_connectionend_construction_error(self):
        """
        We do some sanity checking in the `duplicate` code which can raise
        an Exception.  I don't think it should be possible to ever get there
        under ordinary circumstances, but if you muck with the data structures
        it's possible.  To trigger it we're setting up an extra end on a
        connection but also setting that direction to be a loopback in the room.
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        c = original.connect(r1, DIR_N, r2, DIR_S)
        c.connect_extra(r1, DIR_NE)
        r1.loopbacks[DIR_NE] = True

        with self.assertRaises(Exception) as cm:
            original.duplicate()
        self.assertIn('Unable to get ConnectionEnd for duplicated Map', str(cm.exception))

    def test_duplicate_single_group_two_rooms(self):
        """
        Test duplicating a map when there's a single two-room group
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        original.group_rooms(r1, r2)
        r1.group.style = Group.STYLE_GREEN
        new = original.duplicate()
        self.assertEqual(len(new.groups), 1)
        self.assertNotEqual(original.groups[0], new.groups[0])
        new_group = new.groups[0]
        self.assertEqual(len(new_group.rooms), 2)
        self.assertEqual(new_group.rooms[0].idnum, r1.idnum)
        self.assertEqual(new_group.rooms[1].idnum, r2.idnum)
        self.assertEqual(new_group.style, Group.STYLE_GREEN)

    def test_duplicate_single_group_three_rooms(self):
        """
        Test duplicating a map when there's a single three-room group
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        r3 = original.add_room_at(2, 2, 'Room 3')
        original.group_rooms(r1, r2)
        original.group_rooms(r3, r1)
        r1.group.style = Group.STYLE_RED
        new = original.duplicate()
        self.assertEqual(len(new.groups), 1)
        self.assertNotEqual(original.groups[0], new.groups[0])
        new_group = new.groups[0]
        self.assertEqual(len(new_group.rooms), 3)
        self.assertEqual(new_group.rooms[0].idnum, r1.idnum)
        self.assertEqual(new_group.rooms[1].idnum, r2.idnum)
        self.assertEqual(new_group.rooms[2].idnum, r3.idnum)
        self.assertEqual(new_group.style, Group.STYLE_RED)

    def test_duplicate_two_groups_four_rooms(self):
        """
        Test duplicating a map when there's a two groups, each with two rooms.
        """
        original = Map('Original')
        r1 = original.add_room_at(0, 0, 'Room 1')
        r2 = original.add_room_at(1, 1, 'Room 2')
        r3 = original.add_room_at(2, 2, 'Room 3')
        r4 = original.add_room_at(3, 3, 'Room 3')
        original.group_rooms(r1, r2)
        original.group_rooms(r3, r4)
        r1.group.style = Group.STYLE_BLUE
        r3.group.style = Group.STYLE_YELLOW
        new = original.duplicate()
        self.assertEqual(len(new.groups), 2)
        self.assertNotEqual(original.groups[0], new.groups[0])
        self.assertNotEqual(original.groups[1], new.groups[1])
        new_group1 = new.groups[0]
        self.assertEqual(len(new_group1.rooms), 2)
        self.assertEqual(new_group1.rooms[0].idnum, r1.idnum)
        self.assertEqual(new_group1.rooms[1].idnum, r2.idnum)
        self.assertEqual(new_group1.style, Group.STYLE_BLUE)
        new_group2 = new.groups[1]
        self.assertEqual(len(new_group2.rooms), 2)
        self.assertEqual(new_group2.rooms[0].idnum, r3.idnum)
        self.assertEqual(new_group2.rooms[1].idnum, r4.idnum)
        self.assertEqual(new_group2.style, Group.STYLE_YELLOW)

    def test_roomlist_no_rooms(self):
        """
        Test when there's no rooms
        """
        mapobj = Map('Map')
        self.assertEqual(mapobj.roomlist(), [])

    def test_roomlist_two_rooms(self):
        """
        Test when there's two rooms
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(0, 0, 'Room 1')
        r2 = mapobj.add_room_at(1, 1, 'Room 2')
        rooms = mapobj.roomlist()
        self.assertEqual(len(rooms), 2)
        self.assertIn(r1, rooms)
        self.assertIn(r2, rooms)

    def test_grab_id_available(self):
        """
        Tests grabbing a new Room ID when they are available
        """
        mapobj = Map('Map')
        self.assertEqual(mapobj.grab_id(), 0)
        mapobj.cur_id = 42
        self.assertEqual(mapobj.grab_id(), 42)

    def test_grab_id_skip(self):
        """
        Tests grabbing a new Room ID when there's a room in
        the way of the next ID.
        """
        mapobj = Map('Map')
        mapobj.add_room_at(1, 1, 'Room')
        mapobj.cur_id = 0
        self.assertEqual(mapobj.grab_id(), 1)

    def test_grab_id_loop(self):
        """
        Tests grabbing a new Room ID when the ID is due to
        be looped around to zero again.
        """
        mapobj = Map('Map')
        mapobj.cur_id = 65535
        mapobj.add_room_at(1, 1, 'Room')
        self.assertEqual(mapobj.grab_id(), 0)

    def test_grab_loop_id_exhausted(self):
        """
        We support 65535 rooms.  (This test takes
        about twice the time of all the other tests
        combined.  Yay!)
        """
        mapobj = Map('Map')
        for i in range(65536):
            mapobj.rooms[i] = True
        with self.assertRaises(Exception) as cm:
            mapobj.grab_id()
        self.assertIn('No free room IDs', str(cm.exception))

    def test_inject_room_obj(self):
        """
        Test injecting a room object - this is only used in
        loading from disk and duplicating.
        """
        mapobj = Map('Map')
        r = Room(1, 2, 3)
        mapobj.inject_room_obj(r)
        self.assertEqual(len(mapobj.rooms), 1)
        self.assertEqual(mapobj.rooms[1], r)
        self.assertEqual(mapobj.roomxy[3][2], r)

    def test_inject_room_fail_duplicate_xy(self):
        """
        Test injecting a room object where the x/y location is
        already claimed.
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(1, 1, 'Room')
        with self.assertRaises(Exception) as cm:
            mapobj.inject_room_obj(r)
        self.assertIn('Attempt to overwrite existing room at', str(cm.exception))

    def test_inject_room_fail_duplicate_id(self):
        """
        Test injecting a room object where the id number is
        already taken.
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(1, 1, 'Room')
        r2 = Room(0, 2, 2)
        with self.assertRaises(Exception) as cm:
            mapobj.inject_room_obj(r2)
        self.assertIn('Room ID 0 already exists', str(cm.exception))

    def test_add_room_at_basic(self):
        """
        Tests basic `add_room_at` functionality (already pretty well
        tested by this point in other tests, but whatever)
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(1, 2, 'Room')
        self.assertEqual(r.idnum, 0)
        self.assertEqual(r.name, 'Room')
        self.assertEqual(len(mapobj.rooms), 1)
        self.assertEqual(mapobj.rooms[0], r)
        self.assertEqual(mapobj.roomxy[2][1], r)

    def test_add_room_at_too_many_rooms(self):
        """
        Test adding a room when we already have too many.
        """
        mapobj = Map('Map')
        for i in range(65535):
            mapobj.rooms[i] = True
        with self.assertRaises(Exception) as cm:
            mapobj.add_room_at(1, 1, 'Room')
        self.assertIn('Can only have 65535 rooms', str(cm.exception))

    def test_add_room_at_coords_already_taken(self):
        """
        Test adding a room when the coordinates are already taken
        """
        mapobj = Map('Map')
        mapobj.add_room_at(1, 1, 'Room')
        with self.assertRaises(Exception) as cm:
            mapobj.add_room_at(1, 1, 'Room 2')
        self.assertIn('A room already exists at', str(cm.exception))

    def test_get_room_success(self):
        """
        Test getting a room by ID when the room exists
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(1, 1, 'Room')
        r2 = mapobj.get_room(0)
        self.assertEqual(r, r2)

    def test_get_room_fail(self):
        """
        Test getting a room by ID when the room does not exist
        """
        mapobj = Map('Map')
        r = mapobj.get_room(0)
        self.assertEqual(r, None)

    def test_get_room_at_success(self):
        """
        Test of getting a room at a coordinate, where it exists
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(2, 3, 'Room')
        r2 = mapobj.get_room_at(2, 3)
        self.assertEqual(r, r2)

    def test_get_room_at_fail(self):
        """
        Test getting a room by coordinate when the room does not exist
        """
        mapobj = Map('Map')
        r = mapobj.get_room_at(2, 3)
        self.assertEqual(r, None)

    def test_get_room_at_out_of_bounds(self):
        """
        Test getting a room by coordinate when the specified coordinate
        is out of bounds.
        """
        mapobj = Map('Map')
        with self.assertRaises(IndexError) as cm:
            mapobj.get_room_at(90, 90)

    def test_connect_basic_no_direction_specified(self):
        """
        Testing connecting rooms without specifying the secondary
        direction
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect(r1, DIR_N, r2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)

    def test_connect_basic_with_direction_specified(self):
        """
        Testing connecting rooms with specifying the secondary
        direction
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect(r1, DIR_N, r2, DIR_E)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_E)

    def test_connect_failed_r1_loopback(self):
        """
        A connect that failed because r1 already has a loopback
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r1.set_loopback(DIR_N)
        c = mapobj.connect(r1, DIR_N, r2, DIR_S)
        self.assertEqual(c, None)
        self.assertEqual(len(mapobj.conns), 0)

    def test_connect_failed_r2_loopback(self):
        """
        A connect that failed because r2 already has a loopback
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r2.set_loopback(DIR_S)
        c = mapobj.connect(r1, DIR_N, r2, DIR_S)
        self.assertEqual(c, None)
        self.assertEqual(len(mapobj.conns), 0)

    def test_connect_failed_r1_connection(self):
        """
        A connect that failed because r1 already has a connection
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 2')
        c1 = mapobj.connect(r1, DIR_N, r3)
        c2 = mapobj.connect(r1, DIR_N, r2, DIR_S)
        self.assertEqual(c2, None)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c1)

    def test_connect_failed_r2_connection(self):
        """
        A connect that failed because r2 already has a connection
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 2')
        c1 = mapobj.connect(r3, DIR_N, r2)
        c2 = mapobj.connect(r1, DIR_N, r2, DIR_S)
        self.assertEqual(c2, None)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c1)

    def test_connect_failed_r1_extra_connection(self):
        """
        A connect that failed because r1 already has an
        extra connection
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 2')
        c1 = mapobj.connect(r1, DIR_E, r3)
        c1.connect_extra(r1, DIR_N)
        c2 = mapobj.connect(r1, DIR_N, r2, DIR_S)
        self.assertEqual(c2, None)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c1)

    def test_connect_failed_r2_extra_connection(self):
        """
        A connect that failed because r2 already has an
        extra connection
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 2')
        c1 = mapobj.connect(r2, DIR_E, r3)
        c1.connect_extra(r2, DIR_S)
        c2 = mapobj.connect(r1, DIR_N, r2, DIR_S)
        self.assertEqual(c2, None)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c1)

    def test_connect_id_with_default_other_dir(self):
        """
        Connecting two rooms by ID, leaving the other direction to
        the default.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect_id(0, DIR_N, 1)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)

    def test_connect_id_with_other_dir_specified(self):
        """
        Connecting two rooms by ID, specifying the other direction
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect_id(0, DIR_N, 1, DIR_E)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_E)

    def test_connect_id_r1_missing(self):
        """
        Connecting two rooms by ID, where the first ID doesn't exist
        """
        mapobj = Map('Map')
        r2 = mapobj.add_room_at(1, 1, 'Room 1')
        with self.assertRaises(Exception) as cm:
            mapobj.connect_id(1, DIR_N, 0)
        self.assertIn('Must specify two valid rooms', str(cm.exception))

    def test_connect_id_r2_missing(self):
        """
        Connecting two rooms by ID, where the second ID doesn't exist
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        with self.assertRaises(Exception) as cm:
            mapobj.connect_id(0, DIR_N, 1)
        self.assertIn('Must specify two valid rooms', str(cm.exception))

    def test_connect_failed_too_many_connections(self):
        """
        Our file format "only" supports 65535 connections per map.  Check
        for that.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        for i in range(65535):
            mapobj.conns.append(True)
        with self.assertRaises(Exception) as cm:
            mapobj.connect(r1, DIR_N, r2)
        self.assertIn('Can only have 65535 connections', str(cm.exception))

    def test_detach_without_anything_to_do(self):
        """
        Test detaching when there's nothing to detach.  Should just be
        a NOOP.
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(1, 1, 'Room 1')
        mapobj.detach(r, DIR_N)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertEqual(len(r.conns), 0)

    def test_detach_loopback(self):
        """
        Test detaching when there's a loopback.
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(1, 1, 'Room 1')
        r.set_loopback(DIR_N)
        self.assertEqual(len(r.loopbacks), 1)
        self.assertIn(DIR_N, r.loopbacks)
        mapobj.detach(r, DIR_N)
        self.assertEqual(len(r.loopbacks), 0)

    def test_detach_connection_remove_conn(self):
        """
        Test detaching when doing so will remove a connection
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect(r1, DIR_N, r2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(len(r1.conns), 1)
        self.assertEqual(len(r2.conns), 1)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        mapobj.detach(r1, DIR_N)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertEqual(len(r1.conns), 0)
        self.assertEqual(len(r2.conns), 0)

    def test_detach_connection_remove_extra(self):
        """
        Test detaching when it just detaches an 'extra' end on
        a connection.  The connection should remain in place.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect(r1, DIR_N, r2)
        c.connect_extra(r1, DIR_NE)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(len(r1.conns), 2)
        self.assertEqual(len(r2.conns), 1)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(r2.conns[DIR_S], c)
        mapobj.detach(r1, DIR_NE)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(len(r1.conns), 1)
        self.assertEqual(len(r2.conns), 1)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)

    def test_detach_connection_remove_primary(self):
        """
        Test detaching when it detaches the primary end on
        a connection.  The connection should remain in place.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect(r1, DIR_N, r2)
        c.connect_extra(r1, DIR_NE)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(len(r1.conns), 2)
        self.assertEqual(len(r2.conns), 1)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(r2.conns[DIR_S], c)
        mapobj.detach(r1, DIR_N)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(len(r1.conns), 1)
        self.assertEqual(len(r2.conns), 1)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(r2.conns[DIR_S], c)

    def test_detach_connection_remove_conn_extra_on_far_end(self):
        """
        Test detaching when doing so will remove a connection (with
        extra ends on the far end)
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect(r1, DIR_N, r2)
        c.connect_extra(r2, DIR_E)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(mapobj.conns[0], c)
        self.assertEqual(len(r1.conns), 1)
        self.assertEqual(len(r2.conns), 2)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(r2.conns[DIR_E], c)
        mapobj.detach(r1, DIR_N)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertEqual(len(r1.conns), 0)
        self.assertEqual(len(r2.conns), 0)

    def test_detach_id(self):
        """
        Test detaching by ID - this is a pretty thin wrapper around
        `detach` so we're not going to test for all the combinations
        we'd tested for, above.
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(1, 1, 'Room 1')
        r.set_loopback(DIR_N)
        self.assertEqual(len(r.loopbacks), 1)
        self.assertIn(DIR_N, r.loopbacks)
        mapobj.detach_id(0, DIR_N)
        self.assertEqual(len(r.loopbacks), 0)

    def test_detach_id_invalid_room(self):
        """
        Test with an invalid ID number specified
        """
        mapobj = Map('Map')
        with self.assertRaises(Exception) as cm:
            mapobj.detach_id(0, DIR_N)
        self.assertIn('Must specify a valid room', str(cm.exception))

    def test_del_room_basic(self):
        """
        Test deleting a basic room with no connections or groups
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(1, 1, 'Room 1')
        self.assertEqual(len(mapobj.rooms), 1)
        self.assertEqual(mapobj.roomxy[1][1], r)
        mapobj.del_room(r)
        self.assertEqual(len(mapobj.rooms), 0)
        self.assertEqual(mapobj.roomxy[1][1], None)

    def test_del_room_single_connection(self):
        """
        Test deleting a room which has a single connection to another room.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        mapobj.connect(r1, DIR_N, r2)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(mapobj.roomxy[1][1], r1)
        self.assertEqual(mapobj.roomxy[2][2], r2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertIn(DIR_S, r2.conns)

        mapobj.del_room(r1)
        self.assertEqual(len(mapobj.rooms), 1)
        self.assertEqual(mapobj.roomxy[1][1], None)
        self.assertEqual(mapobj.roomxy[2][2], r2)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertNotIn(DIR_S, r2.conns)

    def test_del_room_two_connections(self):
        """
        Test deleting a room which has a two connections
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 2')
        mapobj.connect(r1, DIR_N, r2)
        mapobj.connect(r1, DIR_S, r3)
        mapobj.connect(r2, DIR_E, r3)
        self.assertEqual(len(mapobj.rooms), 3)
        self.assertEqual(mapobj.roomxy[1][1], r1)
        self.assertEqual(mapobj.roomxy[2][2], r2)
        self.assertEqual(mapobj.roomxy[3][3], r3)
        self.assertEqual(len(mapobj.conns), 3)
        self.assertIn(DIR_S, r2.conns)
        self.assertIn(DIR_E, r2.conns)
        self.assertIn(DIR_N, r3.conns)
        self.assertIn(DIR_W, r3.conns)

        mapobj.del_room(r1)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(mapobj.roomxy[1][1], None)
        self.assertEqual(mapobj.roomxy[2][2], r2)
        self.assertEqual(mapobj.roomxy[3][3], r3)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertNotIn(DIR_S, r2.conns)
        self.assertNotIn(DIR_N, r3.conns)
        self.assertIn(DIR_E, r2.conns)
        self.assertIn(DIR_W, r3.conns)

    def test_del_room_single_connection_extras_on_near_side(self):
        """
        Test deleting a room which has a single connection to another room,
        with extra ends on the room being deleted
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect(r1, DIR_N, r2)
        c.connect_extra(r1, DIR_NE)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(mapobj.roomxy[1][1], r1)
        self.assertEqual(mapobj.roomxy[2][2], r2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertIn(DIR_S, r2.conns)

        mapobj.del_room(r1)
        self.assertEqual(len(mapobj.rooms), 1)
        self.assertEqual(mapobj.roomxy[1][1], None)
        self.assertEqual(mapobj.roomxy[2][2], r2)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertNotIn(DIR_S, r2.conns)

    def test_del_room_single_connection_extras_on_far_side(self):
        """
        Test deleting a room which has a single connection to another room,
        with extra ends on the far end
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        c = mapobj.connect(r1, DIR_N, r2)
        c.connect_extra(r2, DIR_SW)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(mapobj.roomxy[1][1], r1)
        self.assertEqual(mapobj.roomxy[2][2], r2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertIn(DIR_S, r2.conns)
        self.assertIn(DIR_SW, r2.conns)

        mapobj.del_room(r1)
        self.assertEqual(len(mapobj.rooms), 1)
        self.assertEqual(mapobj.roomxy[1][1], None)
        self.assertEqual(mapobj.roomxy[2][2], r2)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertNotIn(DIR_S, r2.conns)
        self.assertNotIn(DIR_SW, r2.conns)

    def test_del_room_with_group_del_group(self):
        """
        Test deleting a room which is in a group, and the group gets deleted too.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        mapobj.group_rooms(r1, r2)
        self.assertNotEqual(r2.group, None)
        self.assertEqual(r2.group, r1.group)
        self.assertEqual(len(mapobj.groups), 1)
        mapobj.del_room(r1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertEqual(r2.group, None)

    def test_del_room_with_group_keep_group(self):
        """
        Test deleting a room which is in a group, and the group will remain in
        place.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 3')
        mapobj.group_rooms(r1, r2)
        mapobj.group_rooms(r3, r2)
        self.assertNotEqual(r2.group, None)
        self.assertEqual(r2.group, r1.group)
        self.assertEqual(r2.group, r3.group)
        self.assertEqual(len(mapobj.groups), 1)
        g = mapobj.groups[0]
        self.assertEqual(len(g.rooms), 3)
        mapobj.del_room(r1)
        self.assertNotEqual(r2.group, None)
        self.assertEqual(r2.group, r3.group)
        self.assertEqual(r2.group, g)
        self.assertEqual(len(g.rooms), 2)

    def test_dir_coord_basic(self):
        """
        Test getting relative direction coordinates
        """
        mapobj = Map('Map')
        r = mapobj.add_room_at(4, 4, 'Room 1')
        for (direction, answer) in [
                (DIR_NW, (3, 3)),
                (DIR_N, (4, 3)),
                (DIR_NE, (5, 3)),
                (DIR_E, (5, 4)),
                (DIR_SE, (5, 5)),
                (DIR_S, (4, 5)),
                (DIR_SW, (3, 5)),
                (DIR_W, (3, 4)),
                ]:
            with self.subTest(direction=direction):
                result = mapobj.dir_coord(r, direction)
                self.assertEqual(result, answer)

    def test_dir_coord_invalid(self):
        """
        Test getting relative direction coordinates when the
        specified direction is invalid (due to the original room
        being right at the map boundaries)
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(0, 0, 'NW corner')
        r2 = mapobj.add_room_at(8, 8, 'SE corner')
        for (room, invalid_dirs) in [
                (r1, [DIR_SW, DIR_W, DIR_NW, DIR_N, DIR_NE]),
                (r2, [DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW]),
                ]:
            for direction in invalid_dirs:
                with self.subTest(room=room, direction=direction):
                    self.assertEqual(mapobj.dir_coord(room, direction), None)

    def test_dir_coord_allow_invalid(self):
        """
        Test getting relative direction coordinates when the
        specified direction is invalid (due to the original room
        being right at the map boundaries), but we specifically allow
        for invalid coordinates to be returned.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(0, 0, 'NW corner')
        r2 = mapobj.add_room_at(8, 8, 'SE corner')
        for (room, direction, result) in [
                (r1, DIR_SW, (-1, 1)),
                (r1, DIR_W, (-1, 0)),
                (r1, DIR_NW, (-1, -1)),
                (r1, DIR_N, (0, -1)),
                (r1, DIR_NE, (1, -1)),
                (r2, DIR_NE, (9, 7)),
                (r2, DIR_E, (9, 8)),
                (r2, DIR_SE, (9, 9)),
                (r2, DIR_S, (8, 9)),
                (r2, DIR_SW, (7, 9)),
                ]:
            with self.subTest(room=room, direction=direction):
                self.assertEqual(mapobj.dir_coord(room, direction, True), result)

    def test_move_room_success(self):
        """
        Tests moving a room to a new location
        """
        for (direction, (new_x, new_y)) in [
                (DIR_NW, (3, 3)),
                (DIR_N, (4, 3)),
                (DIR_NE, (5, 3)),
                (DIR_E, (5, 4)),
                (DIR_SE, (5, 5)),
                (DIR_S, (4, 5)),
                (DIR_SW, (3, 5)),
                (DIR_W, (3, 4)),
                ]:
            with self.subTest(direction=direction):
                mapobj = Map('Map')
                r = mapobj.add_room_at(4, 4, 'Room 1')
                result = mapobj.move_room(r, direction)
                self.assertEqual(result, True)
                self.assertEqual(r.x, new_x)
                self.assertEqual(r.y, new_y)
                self.assertEqual(mapobj.roomxy[4][4], None)
                self.assertEqual(mapobj.roomxy[new_y][new_x], r)

    def test_move_room_blocked_by_other_room(self):
        """
        Tests attempting to move a room to a new location,
        but being blocked by another room
        """
        mapobj = Map('Map')
        rooms = []
        for x in range(3, 6):
            for y in range(3, 6):
                rooms.append(mapobj.add_room_at(x, y, 'Room %d,%d' % (x, y)))
        for direction in [DIR_NW, DIR_N, DIR_NE, DIR_E,
                DIR_SE, DIR_S, DIR_SW, DIR_W]:
            with self.subTest(direction=direction):
                result = mapobj.move_room(rooms[4], direction)
                self.assertEqual(result, False)
                self.assertEqual(rooms[4].x, 4)
                self.assertEqual(rooms[4].y, 4)
                self.assertEqual(mapobj.roomxy[4][4], rooms[4])

    def test_move_room_blocked_by_map(self):
        """
        Tests attempting to move a room to a new location,
        but being blocked by the edge of the map.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(0, 0, 'NW corner')
        r2 = mapobj.add_room_at(8, 8, 'SE corner')
        for (room, (cur_x, cur_y), invalid_dirs) in [
                (r1, (0, 0), [DIR_SW, DIR_W, DIR_NW, DIR_N, DIR_NE]),
                (r2, (8, 8), [DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW]),
                ]:
            for direction in invalid_dirs:
                with self.subTest(room=room, direction=direction):
                    rv = mapobj.move_room(room, direction)
                    self.assertEqual(rv, False)
                    self.assertEqual(room.x, cur_x)
                    self.assertEqual(room.y, cur_y)
                    self.assertEqual(mapobj.roomxy[cur_y][cur_x], room)

    def test_nudge_blocked(self):
        """
        Tests attempting to nudge an entire map, but having it blocked in
        all directions.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(0, 0, 'NW corner')
        r2 = mapobj.add_room_at(8, 8, 'SE corner')
        r3 = mapobj.add_room_at(0, 8, 'SW corner')
        r4 = mapobj.add_room_at(8, 0, 'NE corner')
        r5 = mapobj.add_room_at(4, 4, 'Middle')

        for direction in [DIR_NW, DIR_N, DIR_NE, DIR_E,
                DIR_SE, DIR_S, DIR_SW, DIR_W]:
            with self.subTest(direction=direction):
                rv = mapobj.nudge(direction)
                self.assertEqual(rv, False)
                self.assertEqual(r1.x, 0)
                self.assertEqual(r1.y, 0)
                self.assertEqual(r2.x, 8)
                self.assertEqual(r2.y, 8)
                self.assertEqual(r3.x, 0)
                self.assertEqual(r3.y, 8)
                self.assertEqual(r4.x, 8)
                self.assertEqual(r4.y, 0)
                self.assertEqual(r5.x, 4)
                self.assertEqual(r5.y, 4)
                self.assertEqual(mapobj.roomxy[0][0], r1)
                self.assertEqual(mapobj.roomxy[8][8], r2)
                self.assertEqual(mapobj.roomxy[8][0], r3)
                self.assertEqual(mapobj.roomxy[0][8], r4)
                self.assertEqual(mapobj.roomxy[4][4], r5)

    def test_nudge_worked(self):
        """
        Tests nudging an entire map and having it work.
        """
        dir_mods = {
                DIR_NW: (-1, -1),
                DIR_N: (0, -1),
                DIR_NE: (1, -1),
                DIR_E: (1, 0),
                DIR_SE: (1, 1),
                DIR_S: (0, 1),
                DIR_SW: (-1, 1),
                DIR_W: (-1, 0),
            }

        for direction in [DIR_NW, DIR_N, DIR_NE, DIR_E,
                DIR_SE, DIR_S, DIR_SW, DIR_W]:

            with self.subTest(direction=direction):

                mapobj = Map('Map')
                r1 = mapobj.add_room_at(4, 4, 'Room 1')
                r2 = mapobj.add_room_at(5, 4, 'Room 2')
                r3 = mapobj.add_room_at(4, 5, 'Room 3')
                r4 = mapobj.add_room_at(5, 5, 'Room 4')

                rv = mapobj.nudge(direction)
                self.assertEqual(rv, True)
                self.assertEqual(r1.x, 4+dir_mods[direction][0])
                self.assertEqual(r1.y, 4+dir_mods[direction][1])
                self.assertEqual(r2.x, 5+dir_mods[direction][0])
                self.assertEqual(r2.y, 4+dir_mods[direction][1])
                self.assertEqual(r3.x, 4+dir_mods[direction][0])
                self.assertEqual(r3.y, 5+dir_mods[direction][1])
                self.assertEqual(r4.x, 5+dir_mods[direction][0])
                self.assertEqual(r4.y, 5+dir_mods[direction][1])
                self.assertEqual(mapobj.roomxy[4+dir_mods[direction][1]][4+dir_mods[direction][0]], r1)
                self.assertEqual(mapobj.roomxy[4+dir_mods[direction][1]][5+dir_mods[direction][0]], r2)
                self.assertEqual(mapobj.roomxy[5+dir_mods[direction][1]][4+dir_mods[direction][0]], r3)
                self.assertEqual(mapobj.roomxy[5+dir_mods[direction][1]][5+dir_mods[direction][0]], r4)

    def test_nudge_subset_blocked(self):
        """
        Tests attempting to nudge a subset of a map, but having
        it blocked in all directions by other rooms which aren't part of the
        set.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'NW corner')
        r2 = mapobj.add_room_at(7, 7, 'SE corner')
        r3 = mapobj.add_room_at(1, 7, 'SW corner')
        r4 = mapobj.add_room_at(7, 1, 'NE corner')
        r5 = mapobj.add_room_at(4, 4, 'Middle')
        subset = set([r1, r2, r3, r4, r5])

        blockers = []
        for (idx, (x, y)) in enumerate([(3, 3), (4, 3), (5, 3), (3, 4), (5, 4),
                (3, 5), (4, 5), (5, 5)]):
            blockers.append((idx, x, y, mapobj.add_room_at(x, y, 'Blocker %d' % (idx+1))))

        for direction in [DIR_NW, DIR_N, DIR_NE, DIR_E,
                DIR_SE, DIR_S, DIR_SW, DIR_W]:

            with self.subTest(direction=direction):
                rv = mapobj.nudge(direction, subset)
                self.assertEqual(rv, False)
                self.assertEqual(r1.x, 1)
                self.assertEqual(r1.y, 1)
                self.assertEqual(r2.x, 7)
                self.assertEqual(r2.y, 7)
                self.assertEqual(r3.x, 1)
                self.assertEqual(r3.y, 7)
                self.assertEqual(r4.x, 7)
                self.assertEqual(r4.y, 1)
                self.assertEqual(r5.x, 4)
                self.assertEqual(r5.y, 4)
                self.assertEqual(mapobj.roomxy[1][1], r1)
                self.assertEqual(mapobj.roomxy[7][7], r2)
                self.assertEqual(mapobj.roomxy[7][1], r3)
                self.assertEqual(mapobj.roomxy[1][7], r4)
                self.assertEqual(mapobj.roomxy[4][4], r5)
                for (idx, x, y, blocker) in blockers:
                    with self.subTest(x=x, y=y):
                        self.assertEqual(blocker.x, x)
                        self.assertEqual(blocker.y, y)
                        self.assertEqual(mapobj.roomxy[y][x], blocker)

    def test_nudge_subset_worked(self):
        """
        Tests nudging a subset of a map and having it work.
        """
        dir_mods = {
                DIR_NW: (-1, -1),
                DIR_N: (0, -1),
                DIR_NE: (1, -1),
                DIR_E: (1, 0),
                DIR_SE: (1, 1),
                DIR_S: (0, 1),
                DIR_SW: (-1, 1),
                DIR_W: (-1, 0),
            }

        for direction in [DIR_NW, DIR_N, DIR_NE, DIR_E,
                DIR_SE, DIR_S, DIR_SW, DIR_W]:

            with self.subTest(direction=direction):

                mapobj = Map('Map')
                r1 = mapobj.add_room_at(4, 4, 'Room 1')
                r2 = mapobj.add_room_at(5, 4, 'Room 2')
                r3 = mapobj.add_room_at(4, 5, 'Room 3')
                r4 = mapobj.add_room_at(5, 5, 'Room 4')
                subset = set([r1, r2, r3, r4])

                blockers = []
                for (idx, (x, y)) in enumerate([(1, 1), (7, 7), (1, 7), (7, 1)]):
                    blockers.append((idx, x, y, mapobj.add_room_at(x, y, 'Blocker %d' % (idx+1))))

                rv = mapobj.nudge(direction, subset)
                self.assertEqual(rv, True)
                self.assertEqual(r1.x, 4+dir_mods[direction][0])
                self.assertEqual(r1.y, 4+dir_mods[direction][1])
                self.assertEqual(r2.x, 5+dir_mods[direction][0])
                self.assertEqual(r2.y, 4+dir_mods[direction][1])
                self.assertEqual(r3.x, 4+dir_mods[direction][0])
                self.assertEqual(r3.y, 5+dir_mods[direction][1])
                self.assertEqual(r4.x, 5+dir_mods[direction][0])
                self.assertEqual(r4.y, 5+dir_mods[direction][1])
                self.assertEqual(mapobj.roomxy[4+dir_mods[direction][1]][4+dir_mods[direction][0]], r1)
                self.assertEqual(mapobj.roomxy[4+dir_mods[direction][1]][5+dir_mods[direction][0]], r2)
                self.assertEqual(mapobj.roomxy[5+dir_mods[direction][1]][4+dir_mods[direction][0]], r3)
                self.assertEqual(mapobj.roomxy[5+dir_mods[direction][1]][5+dir_mods[direction][0]], r4)
                for (idx, x, y, blocker) in blockers:
                    with self.subTest(x=x, y=y):
                        self.assertEqual(blocker.x, x)
                        self.assertEqual(blocker.y, y)
                        self.assertEqual(mapobj.roomxy[y][x], blocker)

    def test_nudge_subset_empty(self):
        """
        Tests attempting to nudge an empty subset of a map.  Nothing should
        happen.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'NW corner')
        r2 = mapobj.add_room_at(7, 7, 'SE corner')
        r3 = mapobj.add_room_at(1, 7, 'SW corner')
        r4 = mapobj.add_room_at(7, 1, 'NE corner')
        r5 = mapobj.add_room_at(4, 4, 'Middle')
        subset = set()

        for direction in [DIR_NW, DIR_N, DIR_NE, DIR_E,
                DIR_SE, DIR_S, DIR_SW, DIR_W]:
            with self.subTest(direction=direction):
                rv = mapobj.nudge(direction, subset)
                self.assertEqual(rv, False)
                self.assertEqual(r1.x, 1)
                self.assertEqual(r1.y, 1)
                self.assertEqual(r2.x, 7)
                self.assertEqual(r2.y, 7)
                self.assertEqual(r3.x, 1)
                self.assertEqual(r3.y, 7)
                self.assertEqual(r4.x, 7)
                self.assertEqual(r4.y, 1)
                self.assertEqual(r5.x, 4)
                self.assertEqual(r5.y, 4)
                self.assertEqual(mapobj.roomxy[1][1], r1)
                self.assertEqual(mapobj.roomxy[7][7], r2)
                self.assertEqual(mapobj.roomxy[7][1], r3)
                self.assertEqual(mapobj.roomxy[1][7], r4)
                self.assertEqual(mapobj.roomxy[4][4], r5)

    def test_resize_invalid_direction(self):
        """
        `resize` only works on cardinal directions
        """
        mapobj = Map('Map')
        for direction in [DIR_NW, DIR_NE, DIR_SE, DIR_SW]:
            with self.subTest(direction=direction):
                self.assertEqual(mapobj.resize(direction), False)
                self.assertEqual(mapobj.w, 9)
                self.assertEqual(mapobj.h, 9)

    def test_resize_e_success(self):
        """
        Resize to the east successfully
        """
        mapobj = Map('Map')
        rv = mapobj.resize(DIR_E)
        self.assertEqual(rv, True)
        self.assertEqual(mapobj.w, 10)
        self.assertEqual(mapobj.h, 9)
        for y in range(9):
            with self.subTest(y=y):
                self.assertEqual(len(mapobj.roomxy[y]), 10)

    def test_resize_w_success(self):
        """
        Resize to the west successfully
        """
        mapobj = Map('Map')
        rv = mapobj.resize(DIR_W)
        self.assertEqual(rv, True)
        self.assertEqual(mapobj.w, 8)
        self.assertEqual(mapobj.h, 9)
        for y in range(9):
            with self.subTest(y=y):
                self.assertEqual(len(mapobj.roomxy[y]), 8)

    def test_resize_s_success(self):
        """
        Resize to the south successfully
        """
        mapobj = Map('Map')
        rv = mapobj.resize(DIR_S)
        self.assertEqual(rv, True)
        self.assertEqual(mapobj.w, 9)
        self.assertEqual(mapobj.h, 10)
        self.assertEqual(len(mapobj.roomxy), 10)

    def test_resize_n_success(self):
        """
        Resize to the north successfully
        """
        mapobj = Map('Map')
        rv = mapobj.resize(DIR_N)
        self.assertEqual(rv, True)
        self.assertEqual(mapobj.w, 9)
        self.assertEqual(mapobj.h, 8)
        self.assertEqual(len(mapobj.roomxy), 8)

    def test_resize_e_fail_boundary(self):
        """
        Resize to the east and fail due to boundary constraints
        """
        mapobj = Map('Map')
        while mapobj.w < 255:
            mapobj.resize(DIR_E)
        rv = mapobj.resize(DIR_E)
        self.assertEqual(rv, False)
        self.assertEqual(mapobj.w, 255)
        self.assertEqual(mapobj.h, 9)
        for y in range(9):
            with self.subTest(y=y):
                self.assertEqual(len(mapobj.roomxy[y]), 255)

    def test_resize_w_fail_boundary(self):
        """
        Resize to the west and fail due to boundary constraints
        """
        mapobj = Map('Map')
        while mapobj.w > 1:
            mapobj.resize(DIR_W)
        rv = mapobj.resize(DIR_W)
        self.assertEqual(rv, False)
        self.assertEqual(mapobj.w, 1)
        self.assertEqual(mapobj.h, 9)
        for y in range(9):
            with self.subTest(y=y):
                self.assertEqual(len(mapobj.roomxy[y]), 1)

    def test_resize_s_fail_boundary(self):
        """
        Resize to the south and fail due to boundary constraints
        """
        mapobj = Map('Map')
        while mapobj.h < 255:
            mapobj.resize(DIR_S)
        rv = mapobj.resize(DIR_S)
        self.assertEqual(rv, False)
        self.assertEqual(mapobj.w, 9)
        self.assertEqual(mapobj.h, 255)
        self.assertEqual(len(mapobj.roomxy), 255)

    def test_resize_n_fail_boundary(self):
        """
        Resize to the north and fail due to boundary constraints
        """
        mapobj = Map('Map')
        while mapobj.h > 1:
            mapobj.resize(DIR_N)
        rv = mapobj.resize(DIR_N)
        self.assertEqual(rv, False)
        self.assertEqual(mapobj.w, 9)
        self.assertEqual(mapobj.h, 1)
        self.assertEqual(len(mapobj.roomxy), 1)

    def test_resize_w_fail_room(self):
        """
        Resize to the west but fail due to a room blocking the resize
        """
        mapobj = Map('Map')
        mapobj.add_room_at(8, 4, 'Room')
        rv = mapobj.resize(DIR_W)
        self.assertEqual(rv, False)
        self.assertEqual(mapobj.w, 9)
        self.assertEqual(mapobj.h, 9)
        for y in range(9):
            with self.subTest(y=y):
                self.assertEqual(len(mapobj.roomxy[y]), 9)

    def test_resize_n_fail_room(self):
        """
        Resize to the north but fail due to a room blocking the resize
        """
        mapobj = Map('Map')
        mapobj.add_room_at(4, 8, 'Room')
        rv = mapobj.resize(DIR_N)
        self.assertEqual(rv, False)
        self.assertEqual(mapobj.w, 9)
        self.assertEqual(mapobj.h, 9)
        self.assertEqual(len(mapobj.roomxy), 9)

    def test_remove_room_from_group_delete_group(self):
        """
        Tests removing a room from a group which also deletes the main group
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        mapobj.group_rooms(r1, r2)
        self.assertEqual(len(mapobj.groups), 1)
        self.assertEqual(r1.group, mapobj.groups[0])
        self.assertEqual(r2.group, mapobj.groups[0])

        rv = mapobj.remove_room_from_group(r1)
        self.assertEqual(rv, True)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertEqual(r1.group, None)
        self.assertEqual(r2.group, None)

    def test_remove_room_from_group_leave_group(self):
        """
        Tests removing a room from a group which leaves the group in place
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 3')
        mapobj.group_rooms(r1, r2)
        mapobj.group_rooms(r3, r2)
        self.assertEqual(len(mapobj.groups), 1)
        self.assertEqual(r1.group, mapobj.groups[0])
        self.assertEqual(r2.group, mapobj.groups[0])
        self.assertEqual(r3.group, mapobj.groups[0])

        rv = mapobj.remove_room_from_group(r1)
        self.assertEqual(rv, True)
        self.assertEqual(len(mapobj.groups), 1)
        self.assertEqual(r1.group, None)
        self.assertEqual(r2.group, mapobj.groups[0])
        self.assertEqual(r3.group, mapobj.groups[0])

    def test_remove_room_from_group_when_room_is_not_in_group(self):
        """
        Tests removing a group from a room, when the room isn't actually
        in a group.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        rv = mapobj.remove_room_from_group(r1)
        self.assertEqual(rv, False)
        self.assertEqual(len(mapobj.groups), 0)

    def test_group_rooms_new_group(self):
        """
        Test adding a room to a group which creates a new group
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        self.assertEqual(len(mapobj.groups), 0)
        self.assertEqual(r1.group, None)
        self.assertEqual(r2.group, None)

        rv = mapobj.group_rooms(r1, r2)
        self.assertEqual(rv, True)
        self.assertEqual(len(mapobj.groups), 1)
        g = mapobj.groups[0]
        self.assertEqual(len(g.rooms), 2)
        self.assertIn(r1, g.rooms)
        self.assertIn(r2, g.rooms)
        self.assertEqual(r1.group, g)
        self.assertEqual(r2.group, g)

    def test_group_rooms_already_in_same_group(self):
        """
        Test adding a room to a group which is already in that group
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        mapobj.group_rooms(r1, r2)
        self.assertEqual(len(mapobj.groups), 1)
        g = mapobj.groups[0]
        self.assertEqual(len(g.rooms), 2)
        self.assertIn(r1, g.rooms)
        self.assertIn(r2, g.rooms)
        self.assertEqual(r1.group, g)
        self.assertEqual(r2.group, g)

        rv = mapobj.group_rooms(r1, r2)
        self.assertEqual(rv, False)
        self.assertEqual(len(mapobj.groups), 1)
        self.assertEqual(len(g.rooms), 2)
        self.assertIn(r1, g.rooms)
        self.assertIn(r2, g.rooms)
        self.assertEqual(r1.group, g)
        self.assertEqual(r2.group, g)

    def test_group_rooms_already_in_different_group(self):
        """
        Test adding a room to a group which is already in another group
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 3')
        r4 = mapobj.add_room_at(4, 4, 'Room 4')
        mapobj.group_rooms(r1, r2)
        mapobj.group_rooms(r3, r4)
        self.assertEqual(len(mapobj.groups), 2)
        g1 = mapobj.groups[0]
        g2 = mapobj.groups[1]
        self.assertEqual(len(g1.rooms), 2)
        self.assertEqual(len(g2.rooms), 2)
        self.assertIn(r1, g1.rooms)
        self.assertIn(r2, g1.rooms)
        self.assertIn(r3, g2.rooms)
        self.assertIn(r4, g2.rooms)
        self.assertEqual(r1.group, g1)
        self.assertEqual(r2.group, g1)
        self.assertEqual(r3.group, g2)
        self.assertEqual(r4.group, g2)

        rv = mapobj.group_rooms(r1, r3)
        self.assertEqual(rv, False)
        self.assertEqual(len(mapobj.groups), 2)
        self.assertEqual(len(g1.rooms), 2)
        self.assertEqual(len(g2.rooms), 2)
        self.assertIn(r1, g1.rooms)
        self.assertIn(r2, g1.rooms)
        self.assertIn(r3, g2.rooms)
        self.assertIn(r4, g2.rooms)
        self.assertEqual(r1.group, g1)
        self.assertEqual(r2.group, g1)
        self.assertEqual(r3.group, g2)
        self.assertEqual(r4.group, g2)

    def test_group_rooms_existing_group_left(self):
        """
        Test adding a room to a group when the lefthand room is already
        in a group but the other side isn't
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 3')
        mapobj.group_rooms(r1, r2)
        self.assertEqual(len(mapobj.groups), 1)
        g = mapobj.groups[0]
        self.assertEqual(len(g.rooms), 2)
        self.assertIn(r1, g.rooms)
        self.assertIn(r2, g.rooms)
        self.assertEqual(r1.group, g)
        self.assertEqual(r2.group, g)
        self.assertEqual(r3.group, None)

        rv = mapobj.group_rooms(r1, r3)
        self.assertEqual(rv, True)
        self.assertEqual(len(mapobj.groups), 1)
        self.assertEqual(len(g.rooms), 3)
        self.assertIn(r1, g.rooms)
        self.assertIn(r2, g.rooms)
        self.assertIn(r3, g.rooms)
        self.assertEqual(r1.group, g)
        self.assertEqual(r2.group, g)
        self.assertEqual(r3.group, g)

    def test_group_rooms_existing_group_right(self):
        """
        Test adding a room to a group when the righthand room is already
        in a group but the other side isn't
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 3')
        mapobj.group_rooms(r2, r3)
        self.assertEqual(len(mapobj.groups), 1)
        g = mapobj.groups[0]
        self.assertEqual(len(g.rooms), 2)
        self.assertIn(r2, g.rooms)
        self.assertIn(r3, g.rooms)
        self.assertEqual(r1.group, None)
        self.assertEqual(r2.group, g)
        self.assertEqual(r3.group, g)

        rv = mapobj.group_rooms(r1, r2)
        self.assertEqual(rv, True)
        self.assertEqual(len(mapobj.groups), 1)
        self.assertEqual(len(g.rooms), 3)
        self.assertIn(r1, g.rooms)
        self.assertIn(r2, g.rooms)
        self.assertIn(r3, g.rooms)
        self.assertEqual(r1.group, g)
        self.assertEqual(r2.group, g)
        self.assertEqual(r3.group, g)

    def test_group_rooms_attempt_same_room(self):
        """
        Attempt adding the same room into its own group; should fail.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        rv = mapobj.group_rooms(r1, r1)
        self.assertEqual(rv, False)
        self.assertEqual(len(mapobj.groups), 0)

    def test_save(self):
        """
        Tests saving a file.  Will have three rooms, two connections, and one group.
        """
        mapobj = Map('Map')
        r1 = mapobj.add_room_at(1, 1, 'Room 1')
        r2 = mapobj.add_room_at(2, 2, 'Room 2')
        r3 = mapobj.add_room_at(3, 3, 'Room 3')
        mapobj.connect(r1, DIR_N, r2)
        mapobj.connect(r2, DIR_N, r3)
        mapobj.group_rooms(r2, r3)

        df = self.getSavefile()
        mapobj.save(df)
        df.seek(0)
        self.assertEqual(df.readstr(), 'Map')
        self.assertEqual(df.readuchar(), 9)
        self.assertEqual(df.readuchar(), 9)
        self.assertEqual(df.readshort(), 3)
        self.assertEqual(df.readshort(), 2)
        self.assertEqual(df.readshort(), 1)

        # Fudging quite a bit here because I don't want to bother
        # parsing out the actual room/conn/group structures, which
        # are all well-tested elsewhere.  Just counting up the room
        # each structure takes.  Strings take three bytes plus the
        # length of the string itself; our room names are all the
        # same length so I can skip doing those dynamically.
        for i in range(3):
            df.read(34)
        for i in range(2):
            df.read(18)
        df.read(7)

        self.assertEqual(df.eof(), True)

    def test_load_v1_blank_map(self):
        """
        Tests loading a very basic map without rooms, conections, or groups.
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(0)
        df.writeshort(0)
        df.writeshort(0)
        df.seek(0)

        mapobj = Map.load(df, 1)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 0)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertEqual(len(mapobj.groups), 0)

    def test_load_v1_two_rooms_and_group(self):
        """
        Tests loading a pretty basic map with two rooms and a single group
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(0)
        df.writeshort(1)

        # Room 1 (v1 format)
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)

        # Room 2 (v1 format)
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)

        # Group (<v6 format)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(2)

        df.seek(0)
        mapobj = Map.load(df, 1)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 0)
        self.assertEqual(len(mapobj.groups), 1)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        self.assertEqual(r1.idnum, 1)
        self.assertEqual(r1.name, 'Room 1')
        self.assertEqual(r2.idnum, 2)
        self.assertEqual(r2.name, 'Room 2')
        g = mapobj.groups[0]
        self.assertEqual(len(g.rooms), 2)
        self.assertIn(r1, g.rooms)
        self.assertIn(r2, g.rooms)
        self.assertEqual(r1.group, g)
        self.assertEqual(r2.group, g)

    def test_load_v1_two_rooms_and_connection(self):
        """
        Tests loading a pretty basic map with two rooms and a single connection
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (v1 format)
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)

        # Room 2 (v1 format)
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)

        # Connection (v1 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)

        df.seek(0)
        mapobj = Map.load(df, 1)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_N, c.ends1)
        self.assertIn(DIR_S, c.ends2)
        ce1 = c.ends1[DIR_N]
        ce2 = c.ends2[DIR_S]
        self.assertEqual(ce1.room, r1)
        self.assertEqual(ce1.direction, DIR_N)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce2.room, r2)
        self.assertEqual(ce2.direction, DIR_S)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_load_v3_two_rooms_and_connection(self):
        """
        Tests loading a pretty basic map with two rooms and a single connection,
        on map version 3
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v2+3 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(Connection.PASS_ONEWAY_A)

        df.seek(0)
        mapobj = Map.load(df, 3)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_N, c.ends1)
        self.assertIn(DIR_S, c.ends2)
        ce1 = c.ends1[DIR_N]
        ce2 = c.ends2[DIR_S]
        self.assertEqual(ce1.room, r1)
        self.assertEqual(ce1.direction, DIR_N)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce2.room, r2)
        self.assertEqual(ce2.direction, DIR_S)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_load_v4_two_rooms_and_connection(self):
        """
        Tests loading a pretty basic map with two rooms and a single connection,
        on map version 4
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v4 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)

        df.seek(0)
        mapobj = Map.load(df, 4)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_N, c.ends1)
        self.assertIn(DIR_S, c.ends2)
        ce1 = c.ends1[DIR_N]
        ce2 = c.ends2[DIR_S]
        self.assertEqual(ce1.room, r1)
        self.assertEqual(ce1.direction, DIR_N)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce2.room, r2)
        self.assertEqual(ce2.direction, DIR_S)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_load_v4_midpoint_a_mismatch(self):
        """
        Tests loading a map with two rooms and a single connection,
        on map version 4, where the connection is set to midpoint_a but
        should be fixed to midpoint_b due to changes introduced in v9.
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v4 format)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_A)

        df.seek(0)
        mapobj = Map.load(df, 4)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r2)
        self.assertEqual(c.dir1, DIR_S)
        self.assertEqual(c.r2, r1)
        self.assertEqual(c.dir2, DIR_N)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_S, c.ends1)
        self.assertIn(DIR_N, c.ends2)
        ce1 = c.ends1[DIR_S]
        ce2 = c.ends2[DIR_N]
        self.assertEqual(ce1.room, r2)
        self.assertEqual(ce1.direction, DIR_S)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce2.room, r1)
        self.assertEqual(ce2.direction, DIR_N)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_load_v4_midpoint_b_mismatch(self):
        """
        Tests loading a map with two rooms and a single connection,
        on map version 4, where the connection is set to midpoint_b but
        should be fixed to midpoint_a due to changes introduced in v9.
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v4 format)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)

        df.seek(0)
        mapobj = Map.load(df, 4)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r2)
        self.assertEqual(c.dir1, DIR_S)
        self.assertEqual(c.r2, r1)
        self.assertEqual(c.dir2, DIR_N)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_S, c.ends1)
        self.assertIn(DIR_N, c.ends2)
        ce1 = c.ends1[DIR_S]
        ce2 = c.ends2[DIR_N]
        self.assertEqual(ce1.room, r2)
        self.assertEqual(ce1.direction, DIR_S)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce2.room, r1)
        self.assertEqual(ce2.direction, DIR_N)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_load_v6_two_rooms_and_connection(self):
        """
        Tests loading a pretty basic map with two rooms and a single connection,
        on map version 6
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v5+6 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        df.seek(0)
        mapobj = Map.load(df, 6)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_N, c.ends1)
        self.assertIn(DIR_S, c.ends2)
        ce1 = c.ends1[DIR_N]
        ce2 = c.ends2[DIR_S]
        self.assertEqual(ce1.room, r1)
        self.assertEqual(ce1.direction, DIR_N)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_MAX)
        self.assertEqual(ce2.room, r2)
        self.assertEqual(ce2.direction, DIR_S)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_MAX)

    def test_load_v7_two_rooms_and_basic_symmetric_connection(self):
        """
        Tests loading a pretty basic map with two rooms and a single symmetric
        connection, on map version 7
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v7 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(1)
        # ends 1
        df.writeuchar(1)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        df.seek(0)
        mapobj = Map.load(df, 7)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_N, c.ends1)
        self.assertIn(DIR_S, c.ends2)
        ce1 = c.ends1[DIR_N]
        ce2 = c.ends2[DIR_S]
        self.assertEqual(ce1.room, r1)
        self.assertEqual(ce1.direction, DIR_N)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_MAX)
        self.assertEqual(ce2.room, r2)
        self.assertEqual(ce2.direction, DIR_S)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_MAX)

    def test_load_v7_two_rooms_and_basic_symmetric_connection_midpoint_mismatch(self):
        """
        Tests loading a pretty basic map with two rooms and a single symmetric
        connection, on map version 7, where we have a midpoint mismatch which
        needs fixing (we tested this earlier in the v4 tests too, but let's do
        it here as well.)
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v7 format)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(1)
        # ends 1
        df.writeuchar(1)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        df.seek(0)
        mapobj = Map.load(df, 7)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r2)
        self.assertEqual(c.dir1, DIR_S)
        self.assertEqual(c.r2, r1)
        self.assertEqual(c.dir2, DIR_N)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_S, c.ends1)
        self.assertIn(DIR_N, c.ends2)
        ce1 = c.ends1[DIR_S]
        ce2 = c.ends2[DIR_N]
        self.assertEqual(ce1.room, r2)
        self.assertEqual(ce1.direction, DIR_S)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_MAX)
        self.assertEqual(ce2.room, r1)
        self.assertEqual(ce2.direction, DIR_N)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_MAX)

    def test_load_v7_two_rooms_and_basic_nonsymmetric_connection(self):
        """
        Tests loading a pretty basic map with two rooms and a single nonsymmetric
        connection, on map version 7
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v7 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(0)
        # ends 1
        df.writeuchar(1)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_DOTTED)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_A)
        df.writeuchar(2)

        df.seek(0)
        mapobj = Map.load(df, 7)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(c.symmetric, False)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_N, c.ends1)
        self.assertIn(DIR_S, c.ends2)
        ce1 = c.ends1[DIR_N]
        ce2 = c.ends2[DIR_S]
        self.assertEqual(ce1.room, r1)
        self.assertEqual(ce1.direction, DIR_N)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_MAX)
        self.assertEqual(ce2.room, r2)
        self.assertEqual(ce2.direction, DIR_S)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_DOTTED)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce2.stub_length, 2)

    def test_load_v7_two_rooms_and_nonsymmetric_connection_with_extras(self):
        """
        Tests loading a pretty basic map with two rooms and a single nonsymmetric
        connection with a couple extra ends on each side, on map version 7
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v7 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(0)
        # ends 1
        df.writeuchar(2)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        df.writeuchar(DIR_NE)
        df.writeuchar(ConnectionEnd.CONN_REGULAR)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_A)
        df.writeuchar(ConnectionEnd.STUB_REGULAR)
        # ends 2
        df.writeuchar(2)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_DOTTED)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_A)
        df.writeuchar(2)
        df.writeuchar(DIR_SW)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_REGULAR)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        df.seek(0)
        mapobj = Map.load(df, 7)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_NE, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertIn(DIR_SW, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r1.conns[DIR_NE], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(r2.conns[DIR_SW], c)
        self.assertEqual(c.r1, r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, r2)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(c.symmetric, False)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 2)
        self.assertEqual(len(c.ends2), 2)
        self.assertIn(DIR_N, c.ends1)
        self.assertIn(DIR_NE, c.ends1)
        self.assertIn(DIR_S, c.ends2)
        self.assertIn(DIR_SW, c.ends2)
        ce1 = c.ends1[DIR_N]
        ce2 = c.ends1[DIR_NE]
        ce3 = c.ends2[DIR_S]
        ce4 = c.ends2[DIR_SW]
        self.assertEqual(ce1.room, r1)
        self.assertEqual(ce1.direction, DIR_N)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_MAX)
        self.assertEqual(ce2.room, r1)
        self.assertEqual(ce2.direction, DIR_NE)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce3.room, r2)
        self.assertEqual(ce3.direction, DIR_S)
        self.assertEqual(ce3.conn_type, ConnectionEnd.CONN_DOTTED)
        self.assertEqual(ce3.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce3.stub_length, 2)
        self.assertEqual(ce4.room, r2)
        self.assertEqual(ce4.direction, DIR_SW)
        self.assertEqual(ce4.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce4.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce4.stub_length, ConnectionEnd.STUB_MAX)

    def test_load_v7_error_with_loopback(self):
        """
        Tests loading an invalid map which has a loopback occupying the same space
        as a ConnectionEnd.  Map version 7.
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0x02)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v7 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(1)
        # ends 1
        df.writeuchar(2)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        df.writeuchar(DIR_NE)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        df.seek(0)
        with self.assertRaises(LoadException) as cm:
            Map.load(df, 7)
        self.assertIn('Found an existing ConnectionEnd where we shouldn\'t', cm.exception.text)

    def test_load_v7_error_with_connection(self):
        """
        Tests loading an invalid map which has another connection occupying the
        same space as a ConnectionEnd.  Map version 7.
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(2)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection 1 (v7 format)
        df.writeshort(1)
        df.writeuchar(DIR_NE)
        df.writeshort(2)
        df.writeuchar(DIR_SW)
        df.writeuchar(Connection.PASS_TWOWAY)
        df.writeuchar(0)
        # ends 1
        df.writeuchar(1)
        df.writeuchar(DIR_NE)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_SW)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        # Connection 2 (v7 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(0)
        # Conn 2, ends 1
        df.writeuchar(2)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        df.writeuchar(DIR_NE)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # Conn 2, ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        df.seek(0)
        with self.assertRaises(LoadException) as cm:
            Map.load(df, 7)
        self.assertIn('Found an existing ConnectionEnd where we shouldn\'t', cm.exception.text)

    def test_load_v7_two_rooms_and_two_connections(self):
        """
        Tests loading a pretty basic map with two rooms and two connections.
        Map version 7.
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(2)
        df.writeshort(0)

        # Room 1 (>=v3 format (at least through 7))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v3 format (at least through 7))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection 1 (v7 format)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(1)
        # ends 1
        df.writeuchar(1)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        # Connection 2 (v7 format)
        df.writeshort(1)
        df.writeuchar(DIR_NW)
        df.writeshort(2)
        df.writeuchar(DIR_SE)
        df.writeuchar(Connection.PASS_TWOWAY)
        df.writeuchar(1)
        # ends 1
        df.writeuchar(1)
        df.writeuchar(DIR_NW)
        df.writeuchar(ConnectionEnd.CONN_REGULAR)
        df.writeuchar(ConnectionEnd.RENDER_REGULAR)
        df.writeuchar(ConnectionEnd.STUB_REGULAR)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_SE)
        df.writeuchar(ConnectionEnd.CONN_REGULAR)
        df.writeuchar(ConnectionEnd.RENDER_REGULAR)
        df.writeuchar(ConnectionEnd.STUB_REGULAR)

        df.seek(0)
        mapobj = Map.load(df, 7)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 2)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c1 = mapobj.conns[0]
        c2 = mapobj.conns[1]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_NW, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertIn(DIR_SE, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c1)
        self.assertEqual(r2.conns[DIR_S], c1)
        self.assertEqual(r1.conns[DIR_NW], c2)
        self.assertEqual(r2.conns[DIR_SE], c2)
        self.assertEqual(c1.r1, r1)
        self.assertEqual(c1.dir1, DIR_N)
        self.assertEqual(c1.r2, r2)
        self.assertEqual(c1.dir2, DIR_S)
        self.assertEqual(c1.symmetric, True)
        self.assertEqual(c1.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c1.ends1), 1)
        self.assertEqual(len(c1.ends2), 1)
        self.assertIn(DIR_N, c1.ends1)
        self.assertIn(DIR_S, c1.ends2)
        ce1 = c1.ends1[DIR_N]
        ce2 = c1.ends2[DIR_S]
        self.assertEqual(ce1.room, r1)
        self.assertEqual(ce1.direction, DIR_N)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_MAX)
        self.assertEqual(ce2.room, r2)
        self.assertEqual(ce2.direction, DIR_S)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_MAX)

        self.assertEqual(c2.r1, r1)
        self.assertEqual(c2.dir1, DIR_NW)
        self.assertEqual(c2.r2, r2)
        self.assertEqual(c2.dir2, DIR_SE)
        self.assertEqual(c2.symmetric, True)
        self.assertEqual(c2.passage, Connection.PASS_TWOWAY)
        self.assertEqual(len(c2.ends1), 1)
        self.assertEqual(len(c2.ends2), 1)
        self.assertIn(DIR_NW, c2.ends1)
        self.assertIn(DIR_SE, c2.ends2)
        ce3 = c2.ends1[DIR_NW]
        ce4 = c2.ends2[DIR_SE]
        self.assertEqual(ce3.room, r1)
        self.assertEqual(ce3.direction, DIR_NW)
        self.assertEqual(ce3.conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(ce3.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce3.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce4.room, r2)
        self.assertEqual(ce4.direction, DIR_SE)
        self.assertEqual(ce4.conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(ce4.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce4.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_load_v9_midpoint_a(self):
        """
        Tests loading a pretty basic map with two rooms and a single symmetric
        connection, on map version 9, with the connection on midpoint_a.  Should
        remain the same.
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v8 format (at least through 9))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writeuchar(Room.COLOR_BW)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v8 format (at least through 9))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writeuchar(Room.COLOR_BW)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v7 format)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(1)
        # ends 1
        df.writeuchar(1)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_A)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_A)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        df.seek(0)
        mapobj = Map.load(df, 9)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r2)
        self.assertEqual(c.dir1, DIR_S)
        self.assertEqual(c.r2, r1)
        self.assertEqual(c.dir2, DIR_N)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_S, c.ends1)
        self.assertIn(DIR_N, c.ends2)
        ce1 = c.ends1[DIR_S]
        ce2 = c.ends2[DIR_N]
        self.assertEqual(ce1.room, r2)
        self.assertEqual(ce1.direction, DIR_S)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_MAX)
        self.assertEqual(ce2.room, r1)
        self.assertEqual(ce2.direction, DIR_N)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_MAX)

    def test_load_v9_midpoint_b(self):
        """
        Tests loading a pretty basic map with two rooms and a single symmetric
        connection, on map version 9, with the connection on midpoint_b.  Should
        remain the same.
        """
        df = self.getSavefile()
        df.writestr('Map')
        df.writeuchar(4)
        df.writeuchar(4)
        df.writeshort(2)
        df.writeshort(1)
        df.writeshort(0)

        # Room 1 (>=v8 format (at least through 9))
        df.writeshort(1)
        df.writeuchar(1)
        df.writeuchar(1)
        df.writestr('Room 1')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writeuchar(Room.COLOR_BW)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Room 2 (>=v8 format (at least through 9))
        df.writeshort(2)
        df.writeuchar(2)
        df.writeuchar(2)
        df.writestr('Room 2')
        df.writeuchar(Room.TYPE_NORMAL)
        df.writeuchar(Room.COLOR_BW)
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writestr('')
        df.writeuchar(0)
        df.writeuchar(0)

        # Connection (v7 format)
        df.writeshort(2)
        df.writeuchar(DIR_S)
        df.writeshort(1)
        df.writeuchar(DIR_N)
        df.writeuchar(Connection.PASS_ONEWAY_A)
        df.writeuchar(1)
        # ends 1
        df.writeuchar(1)
        df.writeuchar(DIR_S)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)
        # ends 2
        df.writeuchar(1)
        df.writeuchar(DIR_N)
        df.writeuchar(ConnectionEnd.CONN_LADDER)
        df.writeuchar(ConnectionEnd.RENDER_MIDPOINT_B)
        df.writeuchar(ConnectionEnd.STUB_MAX)

        df.seek(0)
        mapobj = Map.load(df, 9)
        self.assertEqual(df.eof(), True)
        self.assertEqual(mapobj.name, 'Map')
        self.assertEqual(mapobj.w, 4)
        self.assertEqual(mapobj.h, 4)
        self.assertEqual(len(mapobj.rooms), 2)
        self.assertEqual(len(mapobj.conns), 1)
        self.assertEqual(len(mapobj.groups), 0)
        self.assertIn(1, mapobj.rooms)
        self.assertIn(2, mapobj.rooms)
        r1 = mapobj.rooms[1]
        r2 = mapobj.rooms[2]
        c = mapobj.conns[0]
        self.assertIn(DIR_N, r1.conns)
        self.assertIn(DIR_S, r2.conns)
        self.assertEqual(r1.conns[DIR_N], c)
        self.assertEqual(r2.conns[DIR_S], c)
        self.assertEqual(c.r1, r2)
        self.assertEqual(c.dir1, DIR_S)
        self.assertEqual(c.r2, r1)
        self.assertEqual(c.dir2, DIR_N)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(len(c.ends1), 1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_S, c.ends1)
        self.assertIn(DIR_N, c.ends2)
        ce1 = c.ends1[DIR_S]
        ce2 = c.ends2[DIR_N]
        self.assertEqual(ce1.room, r2)
        self.assertEqual(ce1.direction, DIR_S)
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_MAX)
        self.assertEqual(ce2.room, r1)
        self.assertEqual(ce2.direction, DIR_N)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce2.stub_length, ConnectionEnd.STUB_MAX)
