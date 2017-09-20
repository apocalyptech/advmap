#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from advmap.data import ConnectionEnd, Room
from advmap.data import DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW, DIR_W, DIR_NW
from advmap.file import Savefile

class ConnectionEndTests(unittest.TestCase):
    """
    Tests for our ConnectionEnd objects.  Pretty basic.
    """

    def getSavefile(self):
        """
        Returns a Savefile object we can use to test load/save
        operations.
        """
        return Savefile('', in_memory=True)

    def test_initialization(self):
        """
        Basic object initialization
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N)
        self.assertEqual(ce.room, r)
        self.assertEqual(ce.direction, DIR_N)
        self.assertEqual(ce.conn_type, ConnectionEnd.CONN_REGULAR)
        self.assertEqual(ce.render_type, ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce.stub_length, ConnectionEnd.STUB_REGULAR)

    def test_initialization_with_options(self):
        """
        Basic object initialization with optional args
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_S,
                conn_type=ConnectionEnd.CONN_LADDER,
                render_type=ConnectionEnd.RENDER_MIDPOINT_A,
                stub_length=2,
                )
        self.assertEqual(ce.room, r)
        self.assertEqual(ce.direction, DIR_S)
        self.assertEqual(ce.conn_type, ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce.stub_length, 2)

    def test_initialization_with_stub_length_too_low(self):
        """
        Basic object initialization with a stub length set too low
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, stub_length=0)
        self.assertEqual(ce.stub_length, 1)

    def test_initialization_with_stub_length_too_high(self):
        """
        Basic object initialization with a stub length set too high
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, stub_length=4)
        self.assertEqual(ce.stub_length, 3)

    def test_set_regular(self):
        """
        Make sure we can set to regular
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, conn_type=ConnectionEnd.CONN_LADDER)
        self.assertNotEqual(ce.conn_type, ConnectionEnd.CONN_REGULAR)
        ce.set_regular()
        self.assertEqual(ce.conn_type, ConnectionEnd.CONN_REGULAR)

    def test_set_ladder(self):
        """
        Make sure we can set to ladder
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N)
        self.assertNotEqual(ce.conn_type, ConnectionEnd.CONN_LADDER)
        ce.set_ladder()
        self.assertEqual(ce.conn_type, ConnectionEnd.CONN_LADDER)

    def test_set_dotted(self):
        """
        Make sure we can set to dotted
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N)
        self.assertNotEqual(ce.conn_type, ConnectionEnd.CONN_DOTTED)
        ce.set_dotted()
        self.assertEqual(ce.conn_type, ConnectionEnd.CONN_DOTTED)

    def test_is_regular_success(self):
        """
        Test of whether `is_regular` returns `True`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, conn_type=ConnectionEnd.CONN_REGULAR)
        self.assertEqual(ce.is_regular(), True)

    def test_is_regular_fail(self):
        """
        Test of whether `is_regular` returns `False`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, conn_type=ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce.is_regular(), False)

    def test_is_ladder_success(self):
        """
        Test of whether `is_ladder` returns `True`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, conn_type=ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce.is_ladder(), True)

    def test_is_ladder_fail(self):
        """
        Test of whether `is_ladder` returns `False`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, conn_type=ConnectionEnd.CONN_REGULAR)
        self.assertEqual(ce.is_ladder(), False)

    def test_is_dotted_success(self):
        """
        Test of whether `is_dotted` returns `True`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, conn_type=ConnectionEnd.CONN_DOTTED)
        self.assertEqual(ce.is_dotted(), True)

    def test_is_dotted_fail(self):
        """
        Test of whether `is_dotted` returns `False`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, conn_type=ConnectionEnd.CONN_LADDER)
        self.assertEqual(ce.is_dotted(), False)

    def test_set_render_regular(self):
        """
        Make sure we can set to render_regular
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, render_type=ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertNotEqual(ce.render_type, ConnectionEnd.RENDER_REGULAR)
        ce.set_render_regular()
        self.assertEqual(ce.render_type, ConnectionEnd.RENDER_REGULAR)

    def test_set_render_midpoint_a(self):
        """
        Make sure we can set to render_midpoint_a
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N)
        self.assertNotEqual(ce.render_type, ConnectionEnd.RENDER_MIDPOINT_A)
        ce.set_render_midpoint_a()
        self.assertEqual(ce.render_type, ConnectionEnd.RENDER_MIDPOINT_A)

    def test_set_render_midpoint_b(self):
        """
        Make sure we can set to render_midpoint_b
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N)
        self.assertNotEqual(ce.render_type, ConnectionEnd.RENDER_MIDPOINT_B)
        ce.set_render_midpoint_b()
        self.assertEqual(ce.render_type, ConnectionEnd.RENDER_MIDPOINT_B)

    def test_is_render_regular_success(self):
        """
        Test of whether `is_render_regular` returns `True`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, render_type=ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce.is_render_regular(), True)

    def test_is_render_regular_fail(self):
        """
        Test of whether `is_render_regular` returns `False`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, render_type=ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce.is_render_regular(), False)

    def test_is_render_midpoint_a_success(self):
        """
        Test of whether `is_render_midpoint_a` returns `True`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, render_type=ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce.is_render_midpoint_a(), True)

    def test_is_render_midpoint_a_fail(self):
        """
        Test of whether `is_render_midpoint_a` returns `False`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, render_type=ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(ce.is_render_midpoint_a(), False)

    def test_is_render_midpoint_b_success(self):
        """
        Test of whether `is_render_midpoint_b` returns `True`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, render_type=ConnectionEnd.RENDER_MIDPOINT_B)
        self.assertEqual(ce.is_render_midpoint_b(), True)

    def test_is_render_midpoint_b_fail(self):
        """
        Test of whether `is_render_midpoint_b` returns `False`
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, render_type=ConnectionEnd.RENDER_MIDPOINT_A)
        self.assertEqual(ce.is_render_midpoint_b(), False)

    def test_set_stub_length(self):
        """
        Tests our set_stub_length method
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N)
        self.assertEqual(ce.stub_length, 1)
        ce.set_stub_length(2)
        self.assertEqual(ce.stub_length, 2)

    def test_set_stub_length_too_low(self):
        """
        Tests when our set_stub_length is set too low
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N, stub_length=2)
        self.assertEqual(ce.stub_length, 2)
        ce.set_stub_length(0)
        self.assertEqual(ce.stub_length, 1)

    def test_set_stub_length_too_high(self):
        """
        Tests when our set_stub_length is set too high
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N)
        self.assertEqual(ce.stub_length, 1)
        ce.set_stub_length(4)
        self.assertEqual(ce.stub_length, 3)

    def test_increment_stub_length(self):
        """
        Tests incrementing our stub length
        """
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_N)
        for (before, after) in [
                (1, 2),
                (2, 3),
                (3, 1),
                ]:
            with self.subTest(before=before):
                self.assertEqual(ce.stub_length, before)
                ce.increment_stub_length()
                self.assertEqual(ce.stub_length, after)

    def test_save(self):
        """
        Test to make sure our save method works
        """
        df = self.getSavefile()
        r = Room(1, 1, 1)
        ce = ConnectionEnd(r, DIR_S,
                conn_type=ConnectionEnd.CONN_DOTTED,
                render_type=ConnectionEnd.RENDER_REGULAR,
                stub_length=2,
                )
        ce.save(df)
        df.seek(0)
        self.assertEqual(df.readuchar(), DIR_S)
        self.assertEqual(df.readuchar(), ConnectionEnd.CONN_DOTTED)
        self.assertEqual(df.readuchar(), ConnectionEnd.RENDER_REGULAR)
        self.assertEqual(df.readuchar(), 2)
        self.assertEqual(df.eof(), True)
