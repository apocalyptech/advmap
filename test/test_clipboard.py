#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest

from advmap.data import Clipboard, Map, Room, Connection, Group
from advmap.data import DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW, DIR_W, DIR_NW

class ClipboardTests(unittest.TestCase):
    """
    Tests for our Clipboard objects.  Pretty basic.
    """

    def setUp(self):
        """
        Some vars we may as well set up for each test
        """
        self.m1 = Map('Map 1')
        self.r1 = self.m1.add_room_at(5, 5, 'Room 1')
        self.r2 = self.m1.add_room_at(6, 5, 'Room 2')
        self.r3 = self.m1.add_room_at(6, 6, 'Room 3')
        self.r4 = self.m1.add_room_at(5, 6, 'Room 4')
        self.c1 = self.m1.connect(self.r1, DIR_E, self.r2)
        self.c1.set_dotted(self.r1, DIR_E)
        self.c2 = self.m1.connect(self.r2, DIR_S, self.r3)
        self.c2.set_ladder(self.r2, DIR_S)
        self.m1.group_rooms(self.r2, self.r3)
        self.r2.group.increment_style()
        self.initial_group_style = self.r2.group.style

        self.m2 = Map('Map 2')
        self.m2.set_map_size(2, 2)
        self.blocker_room = self.m2.add_room_at(0, 0, 'Initial Room')

        self.clip = Clipboard()

    def test_initialization(self):
        """
        Testing basic initialization
        """
        self.assertEqual(self.clip.has_data, False)
        self.assertEqual(self.clip.room_count(), 0)

    def test_room_count_has_data_one_room(self):
        """
        Test to make sure that the clipboard reports having data when it should
        """
        self.clip.copy(self.m1, set([self.r1]))
        self.assertEqual(self.clip.has_data, True)
        self.assertEqual(self.clip.room_count(), 1)

    def test_room_count_has_data_two_rooms(self):
        """
        Test to make sure that the clipboard reports having data when it should
        """
        self.clip.copy(self.m1, set([self.r1, self.r2]))
        self.assertEqual(self.clip.has_data, True)
        self.assertEqual(self.clip.room_count(), 2)

    def test_copy_single_room(self):
        """
        Tests copying a single room
        """
        self.clip.copy(self.m1, set([self.r1]))
        self.assertEqual(len(self.clip.rooms), 1)
        self.assertEqual(len(self.clip.conns), 0)
        self.assertEqual(len(self.clip.groups), 0)
        room = next(iter(self.clip.rooms))
        self.assertNotEqual(room, self.r1)
        self.assertEqual(room.name, 'Room 1')
        self.assertEqual(self.clip.height, 1)
        self.assertEqual(self.clip.width, 1)

    def test_copy_no_rooms(self):
        """
        Tests copying an empty set
        """
        self.clip.copy(self.m1, set())
        self.assertEqual(self.clip.has_data, False)
        self.assertEqual(self.clip.room_count(), 0)

    def test_copy_two_rooms_wide(self):
        """
        Tests copying two rooms, side by side
        """
        self.clip.copy(self.m1, set([self.r1, self.r2]))
        self.assertEqual(len(self.clip.rooms), 2)
        self.assertEqual(len(self.clip.conns), 1)
        self.assertEqual(len(self.clip.groups), 0)
        self.assertNotIn(self.r1, self.clip.rooms)
        self.assertNotIn(self.r2, self.clip.rooms)
        titles = [r.name for r in self.clip.rooms]
        self.assertIn('Room 1', titles)
        self.assertIn('Room 2', titles)
        self.assertEqual(self.clip.height, 1)
        self.assertEqual(self.clip.width, 2)

    def test_copy_two_rooms_tall(self):
        """
        Tests copying two rooms, on top of each other
        """
        self.clip.copy(self.m1, set([self.r3, self.r2]))
        self.assertEqual(len(self.clip.rooms), 2)
        self.assertEqual(len(self.clip.conns), 1)
        self.assertEqual(len(self.clip.groups), 1)
        self.assertNotIn(self.r3, self.clip.rooms)
        self.assertNotIn(self.r2, self.clip.rooms)
        titles = [r.name for r in self.clip.rooms]
        self.assertIn('Room 3', titles)
        self.assertIn('Room 2', titles)
        self.assertEqual(self.clip.height, 2)
        self.assertEqual(self.clip.width, 1)

    def test_copy_room_var_changes_single_room(self):
        """
        Test to make sure we're modifying our copied rooms properly,
        for a single room.
        """
        self.clip.copy(self.m1, set([self.r1]))
        self.assertEqual(self.r1.x, 5)
        self.assertEqual(self.r1.y, 5)
        room = next(iter(self.clip.rooms))
        self.assertEqual(room.x, 0)
        self.assertEqual(room.y, 0)

    def test_copy_room_var_changes_two_rooms_nw_se(self):
        """
        Test to make sure we're modifying our copied rooms properly,
        for two rooms arranged NW and SE.
        """
        self.clip.copy(self.m1, set([self.r1, self.r3]))
        self.assertEqual(self.r1.x, 5)
        self.assertEqual(self.r1.y, 5)
        self.assertEqual(self.r3.x, 6)
        self.assertEqual(self.r3.y, 6)
        self.assertEqual(self.clip.width, 2)
        self.assertEqual(self.clip.height, 2)
        for room in self.clip.rooms:
            with self.subTest(room=room):
                if room.name == 'Room 1':
                    self.assertNotEqual(room, self.r1)
                    self.assertEqual(room.x, 0)
                    self.assertEqual(room.y, 0)
                else:
                    self.assertNotEqual(room, self.r3)
                    self.assertEqual(room.x, 1)
                    self.assertEqual(room.y, 1)

    def test_copy_room_var_changes_two_rooms_ne_sw(self):
        """
        Test to make sure we're modifying our copied rooms properly,
        for two rooms arranged NE and SW.
        """
        self.clip.copy(self.m1, set([self.r2, self.r4]))
        self.assertEqual(self.r2.x, 6)
        self.assertEqual(self.r2.y, 5)
        self.assertEqual(self.r4.x, 5)
        self.assertEqual(self.r4.y, 6)
        self.assertEqual(self.clip.width, 2)
        self.assertEqual(self.clip.height, 2)
        for room in self.clip.rooms:
            with self.subTest(room=room):
                if room.name == 'Room 2':
                    self.assertNotEqual(room, self.r2)
                    self.assertEqual(room.x, 1)
                    self.assertEqual(room.y, 0)
                else:
                    self.assertNotEqual(room, self.r4)
                    self.assertEqual(room.x, 0)
                    self.assertEqual(room.y, 1)

    def test_copy_no_connection(self):
        """
        Tests copying when there's no connection between the two rooms
        """
        self.clip.copy(self.m1, set([self.r1, self.r4]))
        self.assertEqual(len(self.clip.conns), 0)

    def test_copy_single_connection(self):
        """
        Tests copying when there's a single connection between the two rooms
        """
        self.clip.copy(self.m1, set([self.r1, self.r2]))
        self.assertEqual(len(self.clip.conns), 1)
        conn = self.clip.conns[0]
        self.assertNotEqual(conn, self.c1)
        self.assertIn(DIR_E, self.r1.conns)
        self.assertEqual(self.r1.conns[DIR_E], self.c1)
        self.assertIn(DIR_W, self.r2.conns)
        self.assertEqual(self.r2.conns[DIR_W], self.c1)

    def test_copy_two_connections(self):
        """
        Tests copying when there's a two connections between three rooms
        """
        self.clip.copy(self.m1, set([self.r1, self.r2, self.r3]))
        self.assertEqual(len(self.clip.conns), 2)

    def test_copy_no_groups(self):
        """
        Tests copying when there are no groups
        """
        self.clip.copy(self.m1, set([self.r1, self.r2]))
        self.assertEqual(len(self.clip.groups), 0)

    def test_copy_single_group(self):
        """
        Tests copying when there's one group
        """
        self.clip.copy(self.m1, set([self.r3, self.r2]))
        self.assertEqual(len(self.clip.groups), 1)
        self.assertEqual(self.clip.groups[0][0].style, self.initial_group_style)
        self.assertEqual(len(self.clip.groups[0][1]), 2)

    def test_will_fit_empty(self):
        """
        Tests will_fit when we don't have data.
        """
        self.assertEqual(self.clip.will_fit(self.m1, 0, 0), False)

    def test_will_fit_success_single(self):
        """
        Tests will_fit when we have a selection which will fit, with a single room
        """
        self.clip.copy(self.m1, set([self.r1]))
        self.assertEqual(self.clip.will_fit(self.m1, 0, 0), True)

    def test_will_fit_success_multiple(self):
        """
        Tests will_fit when we have a selection which will fit, with multiple rooms
        """
        self.clip.copy(self.m1, set([self.r1, self.r2, self.r3, self.r4]))
        self.assertEqual(self.clip.will_fit(self.m1, 0, 0), True)

    def test_will_fit_success_multiple_oblong(self):
        """
        Tests will_fit when we have a selection which will fit, with multiple rooms
        in an oblong shape which happens to fit amongst rooms already there.
        """
        self.m1.add_room_at(0, 0, 'Room 5')
        self.m1.add_room_at(1, 1, 'Room 6')
        self.clip.copy(self.m1, set([self.r2, self.r4]))
        self.assertEqual(self.clip.will_fit(self.m1, 0, 0), True)

    def test_will_fit_fail_multiple_blocked(self):
        """
        Tests will_fit when we have a selection which won't fit, with multiple rooms
        """
        self.m1.add_room_at(1, 1, 'Room 5')
        self.clip.copy(self.m1, set([self.r1, self.r2, self.r3, self.r4]))
        self.assertEqual(self.clip.will_fit(self.m1, 0, 0), False)

    def test_will_fit_fail_invalid_coords(self):
        """
        Tests will_fit when we have a selection which won't fit, with multiple rooms
        """
        self.clip.copy(self.m1, set([self.r1, self.r2, self.r3, self.r4]))
        self.assertEqual(self.clip.will_fit(self.m1, 90, 90), False)

    def test_paste_no_data(self):
        """
        Tests pasting when there's nothing to paste
        """
        self.assertEqual(self.clip.paste(self.m1), False)

    def test_paste_success_no_specified_coords_no_search(self):
        """
        Tests a successful paste when we didn't specify any coordinates, and
        searching isn't actually required
        """
        self.clip.copy(self.m1, set([self.r1]))
        self.assertEqual(self.m1.get_room_at(0, 0), None)
        next_id = self.m1.cur_id + 1
        self.assertEqual(self.clip.paste(self.m1), True)
        room = self.m1.get_room_at(0, 0)
        self.assertNotEqual(room, None)
        self.assertEqual(room.name, 'Room 1')
        self.assertNotEqual(room, self.r1)
        self.assertNotEqual(room.idnum, self.r1.idnum)
        self.assertEqual(room.idnum, next_id)
        self.assertEqual(room.x, 0)
        self.assertEqual(room.y, 0)

    def test_paste_success_no_specified_coords_searching(self):
        """
        Tests a successful paste when we didn't specify any coordinates, and
        searching is required
        """
        self.clip.copy(self.m1, set([self.r1]))
        self.assertEqual(self.m2.get_room_at(1, 0), None)
        next_id = self.m2.cur_id + 1
        self.assertEqual(self.clip.paste(self.m2), True)
        room = self.m2.get_room_at(1, 0)
        self.assertNotEqual(room, None)
        self.assertEqual(room.name, 'Room 1')
        self.assertNotEqual(room, self.r1)
        self.assertEqual(room.idnum, next_id)
        self.assertEqual(room.x, 1)
        self.assertEqual(room.y, 0)

    def test_paste_success_no_specified_coords_searching_next_row(self):
        """
        Tests a successful paste when we didn't specify any coordinates, and
        searching is required and moves to the next row.
        """
        self.clip.copy(self.m1, set([self.r1, self.r2]))
        self.assertEqual(self.m2.get_room_at(1, 0), None)
        self.assertEqual(self.m2.get_room_at(1, 1), None)
        self.assertEqual(self.clip.paste(self.m2), True)
        for (x, y, orig_room, title) in [
                (0, 1, self.r1, 'Room 1'),
                (1, 1, self.r2, 'Room 2'),
                ]:
            with self.subTest(x=x, y=y):
                room = self.m2.get_room_at(x, y)
                self.assertNotEqual(room, None)
                self.assertEqual(room.name, title)
                self.assertNotEqual(room, orig_room)
                self.assertEqual(room.x, x)
                self.assertEqual(room.y, y)

    def test_paste_success_no_specified_coords_fit_around_rooms(self):
        """
        Tests a successful paste when we didn't specify any coordinates, and
        the pattern of pasting happens to fix perfectly around other rooms.
        """
        self.m2.add_room_at(1, 1, 'Another Room')
        self.clip.copy(self.m1, set([self.r2, self.r4]))
        self.assertEqual(self.m2.get_room_at(1, 0), None)
        self.assertEqual(self.m2.get_room_at(0, 1), None)
        self.assertEqual(self.clip.paste(self.m2), True)
        for (x, y, orig_room, title) in [
                (1, 0, self.r1, 'Room 2'),
                (0, 1, self.r2, 'Room 4'),
                ]:
            with self.subTest(x=x, y=y):
                room = self.m2.get_room_at(x, y)
                self.assertNotEqual(room, None)
                self.assertEqual(room.name, title)
                self.assertNotEqual(room, orig_room)
                self.assertEqual(room.x, x)
                self.assertEqual(room.y, y)

    def test_paste_fail_no_specified_coords(self):
        """
        Tests a failure to paste, when there's not enough room and we don't
        specify coordinates.
        """
        self.clip.copy(self.m1, set([self.r1, self.r2, self.r3, self.r4]))
        self.assertEqual(self.clip.paste(self.m2), False)
        for (x, y) in [(1, 0), (0, 1), (1, 1)]:
            with self.subTest(x=x, y=y):
                self.assertEqual(self.m2.get_room_at(x, y), None)

    def test_paste_success_specified_coords(self):
        """
        Tests a successful paste when we specified coordinates
        """
        self.clip.copy(self.m1, set([self.r1]))
        self.assertEqual(self.m1.get_room_at(0, 0), None)
        self.assertEqual(self.clip.paste(self.m1, 0, 0), True)
        room = self.m1.get_room_at(0, 0)
        self.assertNotEqual(room, None)
        self.assertEqual(room.name, 'Room 1')
        self.assertNotEqual(room, self.r1)
        self.assertEqual(room.x, 0)
        self.assertEqual(room.y, 0)

    def test_paste_failure_specified_coords(self):
        """
        Tests a failed paste when we specified coordinates
        """
        self.clip.copy(self.m1, set([self.r1]))
        self.assertEqual(self.m2.get_room_at(0, 0), self.blocker_room)
        self.assertEqual(self.clip.paste(self.m2, 0, 0), False)
        self.assertEqual(self.m2.get_room_at(0, 0), self.blocker_room)

    def test_paste_failure_specified_coords_pattern(self):
        """
        Tests a failed paste when we specified coordinates, when it's
        just a single room in our selection which is blocking it.
        """
        self.m2.add_room_at(0, 1, 'Another Room')
        self.clip.copy(self.m1, set([self.r2, self.r4]))
        self.assertEqual(self.clip.paste(self.m2, 0, 0), False)
        self.assertEqual(self.m2.get_room_at(1, 0), None)

    def test_paste_single_connection(self):
        """
        Tests pasting a single connection.
        """
        self.clip.copy(self.m1, set([self.r1, self.r2]))
        self.clip.paste(self.m2)
        r1 = self.m2.get_room_at(0, 1)
        r2 = self.m2.get_room_at(1, 1)
        self.assertEqual(len(self.m2.conns), 1)
        conn = self.m2.conns[0]
        self.assertNotEqual(conn, self.c1)
        self.assertIn(DIR_E, r1.conns)
        self.assertEqual(r1.conns[DIR_E], conn)
        self.assertIn(DIR_W, r2.conns)
        self.assertEqual(r2.conns[DIR_W], conn)
        self.assertEqual(conn.r1, r1)
        self.assertEqual(conn.r2, r2)
        self.assertEqual(conn.ends1[DIR_E].is_dotted(), True)

    def test_paste_two_connections(self):
        """
        Tests pasting two connections
        """
        self.m1.connect(self.r3, DIR_W, self.r4)
        self.clip.copy(self.m1, set([self.r2, self.r3, self.r4]))
        self.clip.paste(self.m2)
        self.assertNotEqual(self.m2.get_room_at(1, 0), None)
        self.assertNotEqual(self.m2.get_room_at(0, 1), None)
        self.assertNotEqual(self.m2.get_room_at(1, 1), None)
        self.assertEqual(len(self.m2.conns), 2)

    def test_paste_single_group(self):
        """
        Tests pasting a single group
        """
        self.clip.copy(self.m1, set([self.r2, self.r3]))
        self.clip.paste(self.m2)
        self.assertEqual(len(self.m2.groups), 1)
        group = self.m2.groups[0]
        self.assertNotEqual(self.m1.groups[0], group)
        self.assertEqual(group.style, self.initial_group_style)
        self.assertEqual(len(group.rooms), 2)
        self.assertIn(self.m2.get_room_at(1, 0), group.rooms)
        self.assertIn(self.m2.get_room_at(1, 1), group.rooms)
        self.assertEqual(self.m2.get_room_at(1, 0).group, group)
        self.assertEqual(self.m2.get_room_at(1, 1).group, group)

    def test_paste_single_group_with_three_rooms(self):
        """
        Tests pasting a single group which has three rooms.
        """
        self.m1.group_rooms(self.r3, self.r4)
        self.clip.copy(self.m1, set([self.r2, self.r3, self.r4]))
        self.clip.paste(self.m2)
        self.assertEqual(len(self.m2.groups), 1)
        group = self.m2.groups[0]
        self.assertNotEqual(self.m1.groups[0], group)
        self.assertEqual(group.style, self.initial_group_style)
        self.assertEqual(len(group.rooms), 3)
        self.assertIn(self.m2.get_room_at(1, 0), group.rooms)
        self.assertIn(self.m2.get_room_at(1, 1), group.rooms)
        self.assertIn(self.m2.get_room_at(0, 1), group.rooms)
        self.assertEqual(self.m2.get_room_at(1, 0).group, group)
        self.assertEqual(self.m2.get_room_at(1, 1).group, group)
        self.assertEqual(self.m2.get_room_at(0, 1).group, group)

    def test_paste_two_groups(self):
        """
        Tests pasting two groups
        """
        self.m1.group_rooms(self.r1, self.r4)
        self.clip.copy(self.m1, set([self.r1, self.r2, self.r3, self.r4]))
        # This next call will clear the map
        self.m2.set_map_size(2, 2)
        self.clip.paste(self.m2)
        self.assertEqual(len(self.m2.groups), 2)
        r1 = self.m2.get_room_at(0, 0)
        r2 = self.m2.get_room_at(1, 0)
        r3 = self.m2.get_room_at(1, 1)
        r4 = self.m2.get_room_at(0, 1)
        self.assertNotEqual(r1, None)
        self.assertNotEqual(r2, None)
        self.assertNotEqual(r3, None)
        self.assertNotEqual(r4, None)
        self.assertNotEqual(r1.group, None)
        self.assertNotEqual(r2.group, None)
        self.assertNotEqual(r3.group, None)
        self.assertNotEqual(r4.group, None)
        self.assertEqual(r1.group, r4.group)
        self.assertEqual(r2.group, r3.group)
        self.assertEqual(r2.group.style, self.initial_group_style)
        self.assertNotEqual(r1.group.style, self.initial_group_style)

    def test_paste_no_groups_but_room_has_one(self):
        """
        Tests pasting no groups, though one of the rooms being pasted does have
        a group.
        """
        self.clip.copy(self.m1, set([self.r1, self.r2]))
        self.clip.paste(self.m2)
        self.assertEqual(len(self.m2.groups), 0)
        self.assertNotEqual(self.m2.get_room_at(0, 1), None)
        self.assertNotEqual(self.m2.get_room_at(1, 1), None)
