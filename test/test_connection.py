#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from advmap.data import ConnectionEnd, Connection, Room
from advmap.data import DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW, DIR_W, DIR_NW
from advmap.file import Savefile

class ConnectionTests(unittest.TestCase):
    """
    Tests for our Connection objects
    """

    def getSavefile(self):
        """
        Returns a Savefile object we can use to test load/save
        operations.
        """
        return Savefile('', in_memory=True)

    def setUp(self):
        """
        Some vars we may as well set up for each test
        """
        self.r1 = Room(1, 1, 1)
        self.r1.name = 'Room 1'
        self.r2 = Room(2, 2, 2)
        self.r2.name = 'Room 2'
        self.c = Connection(self.r1, DIR_N, self.r2, DIR_S)

    def test_initialization_defaults(self):
        """
        Tests initialization with the default values
        """
        self.assertEqual(self.c.r1, self.r1)
        self.assertEqual(self.c.dir1, DIR_N)
        self.assertEqual(self.c.r2, self.r2)
        self.assertEqual(self.c.dir2, DIR_S)
        self.assertEqual(self.c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(self.c.symmetric, True)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_S, self.c.ends2)
        ce1 = self.c.ends1[DIR_N]
        ce2 = self.c.ends2[DIR_S]
        # Alas, no unittest.subTest in Py2
        for end in [ce1, ce2]:
            self.assertEqual(end.conn_type, ConnectionEnd.CONN_REGULAR)
            self.assertEqual(end.render_type, ConnectionEnd.RENDER_REGULAR)
            self.assertEqual(end.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_initialization_specify(self):
        """
        Tests initialization with specifying non-default values
        """
        c = Connection(self.r1, DIR_N, self.r2, DIR_S,
                passage=Connection.PASS_ONEWAY_A,
                conn_type=ConnectionEnd.CONN_LADDER,
                render_type=ConnectionEnd.RENDER_MIDPOINT_A,
                stub_length=3,
                )
        self.assertEqual(c.r1, self.r1)
        self.assertEqual(c.dir1, DIR_N)
        self.assertEqual(c.r2, self.r2)
        self.assertEqual(c.dir2, DIR_S)
        self.assertEqual(c.passage, Connection.PASS_ONEWAY_A)
        self.assertEqual(c.symmetric, True)
        self.assertEqual(len(c.ends1), 1)
        self.assertIn(DIR_N, c.ends1)
        self.assertEqual(len(c.ends2), 1)
        self.assertIn(DIR_S, c.ends2)
        ce1 = c.ends1[DIR_N]
        ce2 = c.ends2[DIR_S]
        # Alas, no unittest.subTest in Py2
        for end in [ce1, ce2]:
            self.assertEqual(end.conn_type, ConnectionEnd.CONN_LADDER)
            self.assertEqual(end.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
            self.assertEqual(end.stub_length, 3)

    def test_set_symmetric_to_false(self):
        """
        Test setting symmetric to false
        """
        self.assertEqual(self.c.symmetric, True)
        self.c.set_symmetric(False)
        self.assertEqual(self.c.symmetric, False)

    def test_set_symmetric_to_true_no_changes(self):
        """
        Test setting symmetric to True when no changes are required
        """
        self.c.set_symmetric(False)

        self.assertEqual(self.c.symmetric, False)
        self.assertEqual(self.c.r1, self.r1)
        self.assertEqual(self.c.dir1, DIR_N)
        self.assertEqual(self.c.r2, self.r2)
        self.assertEqual(self.c.dir2, DIR_S)
        self.assertEqual(self.c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_S, self.c.ends2)
        ce1 = self.c.ends1[DIR_N]
        ce2 = self.c.ends2[DIR_S]
        # Alas, no unittest.subTest in Py2
        for end in [ce1, ce2]:
            self.assertEqual(end.conn_type, ConnectionEnd.CONN_REGULAR)
            self.assertEqual(end.render_type, ConnectionEnd.RENDER_REGULAR)
            self.assertEqual(end.stub_length, ConnectionEnd.STUB_REGULAR)

        self.c.set_symmetric()

        self.assertEqual(self.c.symmetric, True)
        self.assertEqual(self.c.r1, self.r1)
        self.assertEqual(self.c.dir1, DIR_N)
        self.assertEqual(self.c.r2, self.r2)
        self.assertEqual(self.c.dir2, DIR_S)
        self.assertEqual(self.c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_S, self.c.ends2)
        ce1 = self.c.ends1[DIR_N]
        ce2 = self.c.ends2[DIR_S]
        # Alas, no unittest.subTest in Py2
        for end in [ce1, ce2]:
            self.assertEqual(end.conn_type, ConnectionEnd.CONN_REGULAR)
            self.assertEqual(end.render_type, ConnectionEnd.RENDER_REGULAR)
            self.assertEqual(end.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_set_symmetric_to_true_change_other_side(self):
        """
        Test setting symmetric to True when changes are made to the other side
        """
        self.c.set_symmetric(False)
        self.c.ends2[DIR_S].conn_type = ConnectionEnd.CONN_LADDER
        self.c.ends2[DIR_S].render_type = ConnectionEnd.RENDER_MIDPOINT_A
        self.c.ends2[DIR_S].stub_length = 2

        self.assertEqual(self.c.symmetric, False)
        self.assertEqual(self.c.r1, self.r1)
        self.assertEqual(self.c.dir1, DIR_N)
        self.assertEqual(self.c.r2, self.r2)
        self.assertEqual(self.c.dir2, DIR_S)
        self.assertEqual(self.c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_S, self.c.ends2)
        ce1 = self.c.ends1[DIR_N]
        ce2 = self.c.ends2[DIR_S]
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce2.stub_length, 2)

        self.c.set_symmetric()

        self.assertEqual(self.c.symmetric, True)
        self.assertEqual(self.c.r1, self.r1)
        self.assertEqual(self.c.dir1, DIR_N)
        self.assertEqual(self.c.r2, self.r2)
        self.assertEqual(self.c.dir2, DIR_S)
        self.assertEqual(self.c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_S, self.c.ends2)
        ce1 = self.c.ends1[DIR_N]
        ce2 = self.c.ends2[DIR_S]
        # Alas, no unittest.subTest in Py2
        for end in [ce1, ce2]:
            self.assertEqual(end.conn_type, ConnectionEnd.CONN_REGULAR)
            self.assertEqual(end.render_type, ConnectionEnd.RENDER_REGULAR)
            self.assertEqual(end.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_set_symmetric_to_true_change_multiple_ends(self):
        """
        Test setting symmetric to True when changes are made to multiple ends
        """
        self.c.set_symmetric(False)
        self.c.ends2[DIR_S].conn_type = ConnectionEnd.CONN_LADDER
        self.c.ends2[DIR_S].render_type = ConnectionEnd.RENDER_MIDPOINT_A
        self.c.ends2[DIR_S].stub_length = 2
        new_ce = self.c.connect_extra(self.r1, DIR_NE)
        new_ce.conn_type = ConnectionEnd.CONN_DOTTED
        new_ce.render_type = ConnectionEnd.RENDER_MIDPOINT_B
        new_ce.stub_length = 3

        self.assertEqual(self.c.symmetric, False)
        self.assertEqual(self.c.r1, self.r1)
        self.assertEqual(self.c.dir1, DIR_N)
        self.assertEqual(self.c.r2, self.r2)
        self.assertEqual(self.c.dir2, DIR_S)
        self.assertEqual(self.c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(len(self.c.ends1), 2)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_NE, self.c.ends1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_S, self.c.ends2)
        ce1 = self.c.ends1[DIR_N]
        ce2 = self.c.ends2[DIR_S]
        ce3 = self.c.ends1[DIR_NE]
        self.assertEqual(ce1.conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(ce1.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce1.stub_length, ConnectionEnd.STUB_REGULAR)
        self.assertEqual(ce2.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce2.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce2.stub_length, 2)
        self.assertEqual(ce3.conn_type, ConnectionEnd.CONN_DOTTED)
        self.assertEqual(ce3.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce3.stub_length, 3)

        self.c.set_symmetric()

        self.assertEqual(self.c.symmetric, True)
        self.assertEqual(self.c.r1, self.r1)
        self.assertEqual(self.c.dir1, DIR_N)
        self.assertEqual(self.c.r2, self.r2)
        self.assertEqual(self.c.dir2, DIR_S)
        self.assertEqual(self.c.passage, Connection.PASS_TWOWAY)
        self.assertEqual(len(self.c.ends1), 2)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_NE, self.c.ends1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_S, self.c.ends2)
        ce1 = self.c.ends1[DIR_N]
        ce2 = self.c.ends2[DIR_S]
        ce3 = self.c.ends1[DIR_NE]
        # Alas, no unittest.subTest in Py2
        for end in [ce1, ce2, ce3]:
            self.assertEqual(end.conn_type, ConnectionEnd.CONN_REGULAR)
            self.assertEqual(end.render_type, ConnectionEnd.RENDER_REGULAR)
            self.assertEqual(end.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_get_primary_ends_dict_r1(self):
        """
        Test `get_primary_ends_dict` when it should match `r1`
        """
        (direction, ends) = self.c.get_primary_ends_dict(self.r1)
        self.assertEqual(direction, DIR_N)
        self.assertEqual(ends, self.c.ends1)

    def test_get_primary_ends_dict_r2(self):
        """
        Test `get_primary_ends_dict` when it should match `r2`
        """
        (direction, ends) = self.c.get_primary_ends_dict(self.r2)
        self.assertEqual(direction, DIR_S)
        self.assertEqual(ends, self.c.ends2)

    def test_get_primary_ends_dict_not_found(self):
        """
        Test `get_primary_ends_dict` when an invalid Room is passed in
        """
        r3 = Room(3, 3, 3)
        with self.assertRaises(Exception) as cm:
            self.c.get_primary_ends_dict(r3)
        self.assertIn('Room 3 is not part of connection', str(cm.exception))

    def test_get_all_ends_basic(self):
        """
        Tests getting all ends, with just the two default Ends in the connection
        """
        endlist = self.c.get_all_ends()
        self.assertEqual(len(endlist), 2)
        self.assertIn(self.c.ends1[DIR_N], endlist)
        self.assertIn(self.c.ends2[DIR_S], endlist)

    def test_get_all_ends_extra_ends(self):
        """
        Tests getting all ends, with a few extra ends in the connection.
        """
        ce3 = self.c.connect_extra(self.r1, DIR_NE)
        ce4 = self.c.connect_extra(self.r2, DIR_SW)
        endlist = self.c.get_all_ends()
        self.assertEqual(len(endlist), 4)
        self.assertIn(self.c.ends1[DIR_N], endlist)
        self.assertIn(self.c.ends2[DIR_S], endlist)
        self.assertIn(ce3, endlist)
        self.assertIn(ce4, endlist)

    def test_get_end_list_symmetric_basic(self):
        """
        Tests getting our end list when we are set to symmetric, with just the two
        default Ends in the connection
        """
        endlist = self.c.get_end_list(self.r1, DIR_N)
        self.assertEqual(len(endlist), 2)
        self.assertIn(self.c.ends1[DIR_N], endlist)
        self.assertIn(self.c.ends2[DIR_S], endlist)

    def test_get_end_list_symmetric_extra_ends(self):
        """
        Tests getting our end list when we are set to symmetric, with a few extra
        ends in the connection.
        """
        ce3 = self.c.connect_extra(self.r1, DIR_NE)
        ce4 = self.c.connect_extra(self.r2, DIR_SW)
        endlist = self.c.get_end_list(self.r1, DIR_N)
        self.assertEqual(len(endlist), 4)
        self.assertIn(self.c.ends1[DIR_N], endlist)
        self.assertIn(self.c.ends2[DIR_S], endlist)
        self.assertIn(ce3, endlist)
        self.assertIn(ce4, endlist)

    def test_get_end_list_nonsymmetric_r1(self):
        """
        Tests getting our end list when we are set to be nonsymmetric, matching on
        the r1 connection.
        """
        self.c.set_symmetric(False)
        endlist = self.c.get_end_list(self.r1, DIR_N)
        self.assertEqual(len(endlist), 1)
        self.assertIn(self.c.ends1[DIR_N], endlist)

    def test_get_end_list_nonsymmetric_r2(self):
        """
        Tests getting our end list when we are set to be nonsymmetric, matching on
        the r2 connection.
        """
        self.c.set_symmetric(False)
        endlist = self.c.get_end_list(self.r2, DIR_S)
        self.assertEqual(len(endlist), 1)
        self.assertIn(self.c.ends2[DIR_S], endlist)

    def test_get_end_list_symmetric_not_found(self):
        """
        Tests getting our end list while symmetric and the direction is not found.
        Should still return the entire list
        """
        endlist = self.c.get_end_list(self.r1, DIR_W)
        self.assertEqual(len(endlist), 2)
        self.assertIn(self.c.ends1[DIR_N], endlist)
        self.assertIn(self.c.ends2[DIR_S], endlist)

    def test_get_end_list_nonsymmetric_not_found(self):
        """
        Tests getting our end list while symmetric and the direction is not found.
        """
        self.c.set_symmetric(False)
        endlist = self.c.get_end_list(self.r1, DIR_W)
        self.assertEqual(len(endlist), 0)

    def test_connect_extra_basic_r1(self):
        """
        Tests connecting an extra end when it attaches to r1
        """
        new_ce = self.c.connect_extra(self.r1, DIR_NE)
        self.assertEqual(len(self.c.ends1), 2)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_NE, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)
        self.assertEqual(self.c.ends1[DIR_NE], new_ce)
        self.assertEqual(self.r1.conns[DIR_NE], self.c)

    def test_connect_extra_basic_r2(self):
        """
        Tests connecting an extra end when it attaches to r2
        """
        new_ce = self.c.connect_extra(self.r2, DIR_SW)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertEqual(len(self.c.ends2), 2)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)
        self.assertIn(DIR_SW, self.c.ends2)
        self.assertEqual(self.c.ends2[DIR_SW], new_ce)
        self.assertEqual(self.r2.conns[DIR_SW], self.c)

    def test_connect_extra_invalid_room(self):
        """
        Test connecting an extra end when an invalid room is passed in
        """
        r3 = Room(3, 3, 3)
        with self.assertRaises(Exception) as cm:
            self.c.connect_extra(r3, DIR_NE)
        self.assertIn('Specified room 3 is not part of Connection', str(cm.exception))

    def test_connect_extra_r1_defaults_from_primary(self):
        """
        Tests connecting an extra end when it attaches to r1, and defaulting
        to the attributes of the primary r1 direction
        """
        self.c.ends1[DIR_N].conn_type = ConnectionEnd.CONN_LADDER
        self.c.ends1[DIR_N].render_type = ConnectionEnd.RENDER_MIDPOINT_A
        self.c.ends1[DIR_N].stub_length = 2
        new_ce = self.c.connect_extra(self.r1, DIR_NE)
        self.assertEqual(len(self.c.ends1), 2)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_NE, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)
        self.assertEqual(self.c.ends1[DIR_NE], new_ce)
        self.assertEqual(new_ce.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(new_ce.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(new_ce.stub_length, 2)

    def test_connect_extra_r2_defaults_from_primary(self):
        """
        Tests connecting an extra end when it attaches to r2, and defaulting
        to the attributes of the primary r2 direction
        """
        self.c.ends2[DIR_S].conn_type = ConnectionEnd.CONN_LADDER
        self.c.ends2[DIR_S].render_type = ConnectionEnd.RENDER_MIDPOINT_A
        self.c.ends2[DIR_S].stub_length = 2
        new_ce = self.c.connect_extra(self.r2, DIR_SW)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertEqual(len(self.c.ends2), 2)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)
        self.assertIn(DIR_SW, self.c.ends2)
        self.assertEqual(self.c.ends2[DIR_SW], new_ce)
        self.assertEqual(new_ce.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(new_ce.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(new_ce.stub_length, 2)

    def test_connect_extra_blocked_by_loopback_r1(self):
        """
        Tests attempting an extra connection on a direction in r1 which has
        a loopback defined already
        """
        self.r1.set_loopback(DIR_NE)
        new_ce = self.c.connect_extra(self.r1, DIR_NE)
        self.assertEqual(new_ce, None)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)

    def test_connect_extra_blocked_by_loopback_r2(self):
        """
        Tests attempting an extra connection on a direction in r2 which has
        a loopback defined already
        """
        self.r2.set_loopback(DIR_SW)
        new_ce = self.c.connect_extra(self.r2, DIR_SW)
        self.assertEqual(new_ce, None)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)

    def test_connect_extra_blocked_by_connection_r1(self):
        """
        Tests attempting an extra connection on a direction in r1 which has
        a connection defined already.
        """
        r3 = Room(3, 3, 3)
        new_c = self.r1.connect(DIR_NE, r3)
        new_ce = self.c.connect_extra(self.r1, DIR_NE)
        self.assertEqual(new_ce, None)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)
        self.assertEqual(len(new_c.ends1), 1)
        self.assertEqual(len(new_c.ends2), 1)
        self.assertIn(DIR_NE, new_c.ends1)
        self.assertIn(DIR_SW, new_c.ends2)

    def test_connect_extra_blocked_by_connection_r2(self):
        """
        Tests attempting an extra connection on a direction in r2 which has
        a connection defined already.
        """
        r3 = Room(3, 3, 3)
        new_c = self.r2.connect(DIR_SW, r3)
        new_ce = self.c.connect_extra(self.r2, DIR_SW)
        self.assertEqual(new_ce, None)
        self.assertEqual(len(self.c.ends1), 1)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)
        self.assertEqual(len(new_c.ends1), 1)
        self.assertEqual(len(new_c.ends2), 1)
        self.assertIn(DIR_SW, new_c.ends1)
        self.assertIn(DIR_NE, new_c.ends2)

    def test_connect_extra_blocked_by_existing_endsvar(self):
        """
        Tests attempting an extra connection on a direction when the connection's
        own ends var already contains the specified direction.  This particular
        clause of the `if` statement really should never be reached - something
        would have to be digging around in the internal structures like we're
        doing here to set up the test, but whatever, we'll test for it anyway.
        """
        self.c.ends1[DIR_NE] = True
        new_ce = self.c.connect_extra(self.r1, DIR_NE)
        self.assertEqual(new_ce, None)
        self.assertEqual(len(self.c.ends1), 2)
        self.assertEqual(len(self.c.ends2), 1)
        self.assertIn(DIR_N, self.c.ends1)
        self.assertIn(DIR_NE, self.c.ends1)
        self.assertIn(DIR_S, self.c.ends2)
        self.assertEqual(self.c.ends1[DIR_NE], True)

    def test_set_regular_symmetric(self):
        """
        Test set_regular when we are symmetric
        """
        self.c.ends1[DIR_N].conn_type = ConnectionEnd.CONN_LADDER
        self.c.ends2[DIR_S].conn_type = ConnectionEnd.CONN_LADDER
        self.c.set_regular(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(self.c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_REGULAR)

    def test_set_regular_nonsymmetric(self):
        """
        Test set_regular when we are nonsymmetric
        """
        self.c.ends1[DIR_N].conn_type = ConnectionEnd.CONN_LADDER
        self.c.ends2[DIR_S].conn_type = ConnectionEnd.CONN_LADDER
        self.c.set_symmetric(False)
        self.c.set_regular(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(self.c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_LADDER)

    def test_set_ladder_symmetric(self):
        """
        Test set_ladder when we are symmetric
        """
        self.c.set_ladder(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(self.c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_LADDER)

    def test_set_ladder_nonsymmetric(self):
        """
        Test set_ladder when we are nonsymmetric
        """
        self.c.set_symmetric(False)
        self.c.set_ladder(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(self.c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_REGULAR)

    def test_set_dotted_symmetric(self):
        """
        Test set_dotted when we are symmetric
        """
        self.c.set_dotted(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_DOTTED)
        self.assertEqual(self.c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_DOTTED)

    def test_set_dotted_nonsymmetric(self):
        """
        Test set_dotted when we are nonsymmetric
        """
        self.c.set_symmetric(False)
        self.c.set_dotted(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].conn_type, ConnectionEnd.CONN_DOTTED)
        self.assertEqual(self.c.ends2[DIR_S].conn_type, ConnectionEnd.CONN_REGULAR)

    def test_set_render_regular_symmetric(self):
        """
        Test set_render_regular when we are symmetric
        """
        self.c.ends1[DIR_N].render_type = ConnectionEnd.RENDER_MIDPOINT_A
        self.c.ends2[DIR_S].render_type = ConnectionEnd.RENDER_MIDPOINT_A
        self.c.set_render_regular(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(self.c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_REGULAR)

    def test_set_render_regular_nonsymmetric(self):
        """
        Test set_render_regular when we are nonsymmetric
        """
        self.c.ends1[DIR_N].render_type = ConnectionEnd.RENDER_MIDPOINT_A
        self.c.ends2[DIR_S].render_type = ConnectionEnd.RENDER_MIDPOINT_A
        self.c.set_symmetric(False)
        self.c.set_render_regular(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(self.c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_MIDPOINT_A)

    def test_set_render_midpoint_a_symmetric(self):
        """
        Test set_render_midpoint_a when we are symmetric
        """
        self.c.set_render_midpoint_a(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(self.c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_MIDPOINT_A)

    def test_set_render_midpoint_a_nonsymmetric(self):
        """
        Test set_render_midpoint_a when we are nonsymmetric
        """
        self.c.set_symmetric(False)
        self.c.set_render_midpoint_a(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(self.c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_REGULAR)

    def test_set_render_midpoint_b_symmetric(self):
        """
        Test set_render_midpoint_b when we are symmetric
        """
        self.c.set_render_midpoint_b(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(self.c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_MIDPOINT_B)

    def test_set_render_midpoint_b_nonsymmetric(self):
        """
        Test set_render_midpoint_b when we are nonsymmetric
        """
        self.c.set_symmetric(False)
        self.c.set_render_midpoint_b(self.r1, DIR_N)
        self.assertEqual(self.c.ends1[DIR_N].render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(self.c.ends2[DIR_S].render_type, ConnectionEnd.RENDER_REGULAR)

    def test_set_stub_length_symmetric(self):
        """
        Test set_stub_length when we are symmetric
        """
        self.c.set_stub_length(self.r1, DIR_N, 2)
        self.assertEqual(self.c.ends1[DIR_N].stub_length, 2)
        self.assertEqual(self.c.ends2[DIR_S].stub_length, 2)

    def test_set_stub_length_nonsymmetric(self):
        """
        Test set_stub_length when we are nonsymmetric
        """
        self.c.set_symmetric(False)
        self.c.set_stub_length(self.r1, DIR_N, 2)
        self.assertEqual(self.c.ends1[DIR_N].stub_length, 2)
        self.assertEqual(self.c.ends2[DIR_S].stub_length, 1)

    def test_set_twoway(self):
        """
        Test setting two-way connection
        """
        self.c.passage = Connection.PASS_ONEWAY_A
        self.c.set_twoway()
        self.assertEqual(self.c.passage, Connection.PASS_TWOWAY)

    def test_set_oneway_a(self):
        """
        Test setting one-way A connection
        """
        self.c.set_oneway_a()
        self.assertEqual(self.c.passage, Connection.PASS_ONEWAY_A)

    def test_set_oneway_b(self):
        """
        Test setting one-way B connection
        """
        self.c.set_oneway_b()
        self.assertEqual(self.c.passage, Connection.PASS_ONEWAY_B)

    def test_is_twoway_true(self):
        """
        Test `is_twoway` for truth
        """
        self.assertEqual(self.c.is_twoway(), True)

    def test_is_twoway_false(self):
        """
        Test `is_twoway` for falsehood
        """
        self.c.set_oneway_a()
        self.assertEqual(self.c.is_twoway(), False)

    def test_is_oneway_a_true(self):
        """
        Test `is_oneway_a` for truth
        """
        self.c.set_oneway_a()
        self.assertEqual(self.c.is_oneway_a(), True)

    def test_is_oneway_a_false(self):
        """
        Test `is_oneway_a` for falsehood
        """
        self.assertEqual(self.c.is_oneway_a(), False)

    def test_is_oneway_true_for_a(self):
        """
        Test `is_oneway` for truth when the connection is oneway_a
        """
        self.c.set_oneway_a()
        self.assertEqual(self.c.is_oneway(), True)

    def test_is_oneway_true_for_b(self):
        """
        Test `is_oneway` for truth when the connection is oneway_b
        """
        self.c.set_oneway_b()
        self.assertEqual(self.c.is_oneway(), True)

    def test_is_oneway_false(self):
        """
        Test `is_oneway` for falsehood
        """
        self.assertEqual(self.c.is_oneway(), False)

    def test_is_oneway_b_true(self):
        """
        Test `is_oneway_b` for truth
        """
        self.c.set_oneway_b()
        self.assertEqual(self.c.is_oneway_b(), True)

    def test_is_oneway_b_false(self):
        """
        Test `is_oneway_b` for falsehood
        """
        self.assertEqual(self.c.is_oneway_b(), False)

    def test_repr_oneway_a(self):
        """
        Test our __repr__ for a oneway_a connection
        """
        self.c.set_oneway_a()
        self.assertEqual(repr(self.c), '<Connection - Room 1 (N) <- Room 2 (S)>')

    def test_repr_oneway_b(self):
        """
        Test our __repr__ for a oneway_b connection
        """
        self.c.set_oneway_b()
        self.assertEqual(repr(self.c), '<Connection - Room 1 (N) -> Room 2 (S)>')

    def test_repr_twoway(self):
        """
        Test our __repr__ for a twoway connection
        """
        self.assertEqual(repr(self.c), '<Connection - Room 1 (N) <-> Room 2 (S)>')

    def test_repr_multiple_directions(self):
        """
        Test our __repr__ for a twoway connection with multiple Ends on each room
        """
        self.c.connect_extra(self.r1, DIR_NE)
        self.c.connect_extra(self.r2, DIR_SW)
        self.assertEqual(repr(self.c), '<Connection - Room 1 (N, NE) <-> Room 2 (S, SW)>')

    def test_get_opposite_from_r1(self):
        """
        Tests `get_opposite` when we're querying from r1
        """
        (room, directions) = self.c.get_opposite(self.r1)
        self.assertEqual(room, self.r2)
        self.assertEqual(directions, [DIR_S])

    def test_get_opposite_from_r1_extra_ends(self):
        """
        Tests `get_opposite` when we're querying from r1 and r2
        has extra ends
        """
        self.c.connect_extra(self.r2, DIR_SW)
        (room, directions) = self.c.get_opposite(self.r1)
        self.assertEqual(room, self.r2)
        self.assertEqual(sorted(directions), sorted([DIR_S, DIR_SW]))

    def test_get_opposite_from_r2(self):
        """
        Tests `get_opposite` when we're querying from r2
        """
        (room, directions) = self.c.get_opposite(self.r2)
        self.assertEqual(room, self.r1)
        self.assertEqual(directions, [DIR_N])

    def test_get_opposite_invalid_room(self):
        """
        Tests `get_opposite` when the passed-in room is invalid
        """
        r3 = Room(3, 3, 3)
        with self.assertRaises(Exception) as cm:
            self.c.get_opposite(r3)
        self.assertIn('Room 3 not valid for this connection', str(cm.exception))

    def test_save_symmetric(self):
        """
        Test saving with our symmetric flag on
        """
        df = self.getSavefile()
        self.c.save(df)
        df.seek(0)
        self.assertEqual(df.readshort(), 1)
        self.assertEqual(df.readuchar(), DIR_N)
        self.assertEqual(df.readshort(), 2)
        self.assertEqual(df.readuchar(), DIR_S)
        self.assertEqual(df.readuchar(), Connection.PASS_TWOWAY)
        self.assertEqual(df.readuchar(), 1)
        self.assertEqual(df.readuchar(), 1)
        self.assertEqual(df.readuchar(), DIR_N)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.STUB_REGULAR)
        self.assertEqual(df.readuchar(), 1)
        self.assertEqual(df.readuchar(), DIR_S)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.STUB_REGULAR)
        self.assertEqual(df.eof(), True)

    def test_save_nonsymmetric(self):
        """
        Test saving with our symmetric flag off
        """
        self.c.set_symmetric(False)
        self.c.set_ladder(self.r2, DIR_S)
        self.c.set_render_midpoint_a(self.r2, DIR_S)
        self.c.set_stub_length(self.r2, DIR_S, 3)
        df = self.getSavefile()
        self.c.save(df)
        df.seek(0)
        self.assertEqual(df.readshort(), 1)
        self.assertEqual(df.readuchar(), DIR_N)
        self.assertEqual(df.readshort(), 2)
        self.assertEqual(df.readuchar(), DIR_S)
        self.assertEqual(df.readuchar(), Connection.PASS_TWOWAY)
        self.assertEqual(df.readuchar(), 0)
        self.assertEqual(df.readuchar(), 1)
        self.assertEqual(df.readuchar(), DIR_N)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.STUB_REGULAR)
        self.assertEqual(df.readuchar(), 1)
        self.assertEqual(df.readuchar(), DIR_S)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_LADDER)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(df.readuchar(), 3)
        self.assertEqual(df.eof(), True)

    def test_save_extra_ends(self):
        """
        Test saving with extra ends on both sides
        """
        # Note that we rely on the ends being saved in order.  This is
        # currently the case, and I intend to keep it that way, but should
        # that ever accidentally change, the pass/fail of this test may
        # not be predictable.
        self.c.connect_extra(self.r1, DIR_NE)
        self.c.connect_extra(self.r2, DIR_SW)
        df = self.getSavefile()
        self.c.save(df)
        df.seek(0)
        self.assertEqual(df.readshort(), 1)
        self.assertEqual(df.readuchar(), DIR_N)
        self.assertEqual(df.readshort(), 2)
        self.assertEqual(df.readuchar(), DIR_S)
        self.assertEqual(df.readuchar(), Connection.PASS_TWOWAY)
        self.assertEqual(df.readuchar(), 1)
        self.assertEqual(df.readuchar(), 2)
        self.assertEqual(df.readuchar(), DIR_N)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.STUB_REGULAR)
        self.assertEqual(df.readuchar(), DIR_NE)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.STUB_REGULAR)
        self.assertEqual(df.readuchar(), 2)
        self.assertEqual(df.readuchar(), DIR_S)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.STUB_REGULAR)
        self.assertEqual(df.readuchar(), DIR_SW)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(df.readuchar(), ConnectionEnd.STUB_REGULAR)
        self.assertEqual(df.eof(), True)
