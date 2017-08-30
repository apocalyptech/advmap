#!/usr/bin/env python2
# vim: set expandtab tabstop=4 shiftwidth=4:
#
# Adventure Game Mapper
# Copyright (C) 2010 CJ Kucera
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

from advmap.file import *

#
# So.
#
# "Game" is the main object, which is a collection of Maps.
# A Map is a collection of Rooms and Connections.
#
# Each room keeps a dict of conns into itself, and the Map object
# also keeps a list of all conns in the map.  This means we've got
# to do data upkeep on two separate structures, which is subpar, but
# it's got the advantage that we can easily work on conns on a per-
# room basis (which is nice while editing) and on a whole-map basis
# (which is nice while saving/loading).
#

__all__ = [ 'Room', 'Connection', 'ConnectionEnd', 'Map', 'Game', 'Group',
        'DIR_N', 'DIR_NE', 'DIR_E', 'DIR_SE', 'DIR_S', 'DIR_SW', 'DIR_W', 'DIR_NW',
        'DIR_LIST', 'DIR_OPP', 'TXT_2_DIR', 'DIR_2_TXT' ]

DIR_N = 0
DIR_NE = 1
DIR_E = 2
DIR_SE = 3
DIR_S = 4
DIR_SW = 5
DIR_W = 6
DIR_NW = 7

DIR_LIST = [DIR_N, DIR_NE, DIR_E, DIR_SE, DIR_S, DIR_SW, DIR_W, DIR_NW]

DIR_OPP = []
DIR_OPP.append(DIR_S)
DIR_OPP.append(DIR_SW)
DIR_OPP.append(DIR_W)
DIR_OPP.append(DIR_NW)
DIR_OPP.append(DIR_N)
DIR_OPP.append(DIR_NE)
DIR_OPP.append(DIR_E)
DIR_OPP.append(DIR_SE)

TXT_2_DIR = {
        'n': DIR_N,
        'ne': DIR_NE,
        'e': DIR_E,
        'se': DIR_SE,
        's': DIR_S,
        'sw': DIR_SW,
        'w': DIR_W,
        'nw': DIR_NW
    }

DIR_2_TXT = {
        DIR_N: 'N',
        DIR_NE: 'NE',
        DIR_E: 'E',
        DIR_SE: 'SE',
        DIR_S: 'S',
        DIR_SW: 'SW',
        DIR_W: 'W',
        DIR_NW: 'NW'
    }

SAVEFILE_VER = 8

class Group(object):
    """
    A group of rooms, used for drawing screens in graphical
    adventure games which have multiple "levels" with their own
    connections, which nevertheless all take up one screen.
    (Could also be used for other purposes as well, of course)
    """

    # Style constants
    STYLE_MAX = 9
    (STYLE_NORMAL,
        STYLE_RED,
        STYLE_GREEN,
        STYLE_BLUE,
        STYLE_YELLOW,
        STYLE_PURPLE,
        STYLE_CYAN,
        STYLE_FAINT,
        STYLE_DARK,
        ) = range(STYLE_MAX)

    def __init__(self, room1, room2):
        if room1 == room2:
            raise Exception('Cannot create a group with only one room')
        self.rooms = []
        self.add_room(room1)
        self.add_room(room2)
        self.style = self.STYLE_NORMAL

    def get_rooms(self):
        """
        Returns a list of all rooms in this group
        """
        return self.rooms

    def has_room(self, room):
        """
        Returns True/False depending on if the given room is
        in this group.
        """
        return (room in self.rooms)

    def add_room(self, room):
        """
        Adds a room to the group.
        """
        if (room not in self.rooms):
            self.rooms.append(room)
            room.group = self

    def del_room(self, room):
        """
        Removes a room from the group.  Will return True if
        this group should be deleted afterwards or not.
        """
        try:
            self.rooms.remove(room)
            room.group = None
        except ValueError:
            pass
        return (len(self.rooms) < 2)

    def increment_style(self):
        """
        Increments our style
        """
        self.style = (self.style + 1) % self.STYLE_MAX

    def save(self, df):
        """
        Saves ourself to the given filehandle
        """
        if (len(self.get_rooms()) < 2):
            raise Exception('Warning: a group cannot consist of only one room')
        df.writeshort(len(self.get_rooms()))
        df.writeuchar(self.style)
        for room in self.get_rooms():
            df.writeshort(room.idnum)

    @staticmethod
    def load(df, mapobj, version):
        """
        Loads ourself, given a map object (to do room lookups) and a filehandle
        """
        num_rooms = df.readshort()
        if (num_rooms < 2):
            raise LoadException('Group stated it had only %d rooms' % (num_rooms))
        if version >= 6:
            style = df.readuchar()
        else:
            style = Group.STYLE_NORMAL
        rooms = []
        for i in range(num_rooms):
            identifier = df.readshort()
            room = mapobj.get_room(identifier)
            if (room is None):
                raise LoadException('Room %d does not exist while loading group' % (identifier))
            rooms.append(room)
        group = Group(rooms[0], rooms[1])
        group.style = style
        for room in rooms[2:]:
            group.add_room(room)
        return group

class Room(object):
    """
    A single room
    """

    # Type constants
    TYPE_MAX = 5
    (TYPE_NORMAL,
        TYPE_LABEL,
        TYPE_FAINT,
        TYPE_DARK,
        TYPE_CONNHELPER,
        ) = range(TYPE_MAX)

    # English equivalents
    TYPE_TXT = {
            TYPE_NORMAL: 'Normal Room',
            TYPE_LABEL: 'Label',
            TYPE_FAINT: 'Faint',
            TYPE_DARK: 'Dark',
            TYPE_CONNHELPER: 'Connection Helper',
        }

    # Color constants
    COLOR_MAX = 8
    (COLOR_BW,
        COLOR_GREEN,
        COLOR_BLUE,
        COLOR_RED,
        COLOR_YELLOW,
        COLOR_PURPLE,
        COLOR_CYAN,
        COLOR_ORANGE,
        ) = range(COLOR_MAX)

    # Color equivalents
    COLOR_TXT = {
            COLOR_BW: 'Black+White',
            COLOR_GREEN: 'Green',
            COLOR_BLUE: 'Blue',
            COLOR_RED: 'Red',
            COLOR_YELLOW: 'Yellow',
            COLOR_PURPLE: 'Purple',
            COLOR_CYAN: 'Cyan',
            COLOR_ORANGE: 'Orange',
        }

    def __init__(self, idnum, x, y):
        self.idnum = idnum
        self.x = x
        self.y = y
        self.name = ''
        self.notes = ''
        self.conns = {}
        self.loopbacks = {}
        self.up = ''
        self.down = ''
        self.door_in = ''
        self.door_out = ''
        self.type = self.TYPE_NORMAL
        self.color = self.COLOR_BW
        self.offset_x = False
        self.offset_y = False
        self.group = None

    def duplicate(self):
        """
        Returns a copy of ourself.  Note that this doesn't
        copy connections or groups; that has to be handled by
        the Map object
        """
        newroom = Room(self.idnum, self.x, self.y)
        newroom.name = self.name
        newroom.notes = self.notes
        newroom.up = self.up
        newroom.down = self.down
        newroom.door_in = self.door_in
        newroom.door_out = self.door_out
        newroom.type = self.type
        newroom.color = self.color
        newroom.offset_x = self.offset_x
        newroom.offset_y = self.offset_y
        for direction, value in self.loopbacks.items():
            newroom.loopbacks[direction] = value
        return newroom

    def unexplored(self):
        """
        Special-case magic string here.  Yay!
        """
        return (self.name == '(unexplored)')

    def set_loopback(self, direction):
        """
        Sets a loopback at the given direction
        """
        if direction not in self.conns:
            self.loopbacks[direction] = True

    def connect(self, direction, other_room, direction2=None):
        """
        Connects ourself to another room.  Will default to the opposite
        direction on the other room, if no other direction is specified.
        Will return the new Connection object which was created, or
        `None` if there was already a connection or loopback in the
        way.
        """
        if direction2 is None:
            direction2 = DIR_OPP[direction]
        if direction in self.conns or direction in self.loopbacks:
            return None
        if direction2 in other_room.conns or direction2 in other_room.loopbacks:
            return None
        return Connection(self, direction, other_room, direction2)

    def detach(self, direction):
        """
        Detaches ourself from a direction.  Will
        additionally detach the opposite end, if this is the
        last End to be detached.  Returns `True` if the connection
        should be completely torn down by whatever's calling the
        method, or `False` if it should be kept alive.
        """
        # First do a couple sanity checks
        if direction not in self.conns and direction not in self.loopbacks:
            raise Exception('No connections or loopbacks to detach')

        # Set a default return val
        retval = False

        # Process
        if direction in self.conns:
            # Now see if we have more than one connection on this end.
            # If so, just trim the ends dict.
            conn_var = self.conns[direction]
            (primary_dir, ends_dict) = conn_var.get_primary_ends_dict(self)
            if len(ends_dict) == 1:
                conn = self.conns[direction]
                (other, other_dirs) = conn.get_opposite(self)
                del self.conns[direction]
                for other_dir in other_dirs:
                    del other.conns[other_dir]
                retval = True
            else:
                del ends_dict[direction]
                del self.conns[direction]
                # Set a new primary, if we just deleted the primary
                if direction == primary_dir:
                    if self.idnum == conn_var.r1.idnum:
                        conn_var.dir1 = next(iter(ends_dict.keys()))
                    else:
                        conn_var.dir2 = next(iter(ends_dict.keys()))

        # Get rid of any loopbacks which we might have
        if direction in self.loopbacks:
            del self.loopbacks[direction]

        # And return
        return retval

    def get_loopback(self, direction):
        """
        Returns True if there's a loopback at the given direction,
        False otherwise.
        """
        return (direction in self.loopbacks)

    def get_conn(self, direction):
        """
        Returns the Connection object at our given direction, if
        we can.  Returns None otherwise.
        """
        if direction in self.conns:
            return self.conns[direction]
        else:
            return None

    def in_group_with(self, room):
        """
        Returns True/False depending on if we're in a group with the
        specified room
        """
        if self.group:
            return self.group.has_room(room)
        else:
            return False

    def increment_type(self):
        """
        Increments our type
        """
        self.type = (self.type + 1) % self.TYPE_MAX

    def increment_color(self):
        """
        Increments our color
        """
        self.color = (self.color + 1) % self.COLOR_MAX

    def save(self, df):
        """
        Writes ourself to the given filehandle
        """
        flagbits = 0
        if (self.offset_x):
            flagbits = flagbits | 0x2
        if (self.offset_y):
            flagbits = flagbits | 0x1
        df.writeshort(self.idnum)
        df.writeuchar(self.x)
        df.writeuchar(self.y)
        df.writestr(self.name)
        df.writeuchar(self.type)
        df.writeuchar(self.color)
        df.writestr(self.up)
        df.writestr(self.down)
        df.writestr(self.door_in)
        df.writestr(self.door_out)
        df.writestr(self.notes)
        df.writeuchar(flagbits)
        loopbackbits = 0
        for direction in DIR_LIST:
            if direction in self.loopbacks:
                compvar = 1 << direction
                loopbackbits |= compvar
        df.writeuchar(loopbackbits)

    @staticmethod
    def load(df, version):
        """
        Loads a room from the given filehandle
        """
        idnum = df.readshort()
        x = df.readuchar()
        y = df.readuchar()
        room = Room(idnum, x, y)
        room.name = df.readstr()
        if version >= 8:
            room.type = df.readuchar()
            room.color = df.readuchar()
        else:
            # v8 split off type+color for much better room flexibility.
            # This means we've got to do a mapping for previous revs, though!
            previous_type = df.readuchar()
            mapping = {
                    0: (0, 0),  # Normal
                    1: (0, 1),  # Green
                    2: (1, 0),  # Label
                    3: (0, 2),  # Blue
                    4: (0, 3),  # Red
                    5: (2, 0),  # Faint
                    6: (0, 4),  # Yellow
                    7: (0, 5),  # Purple
                    8: (0, 6),  # Cyan
                    9: (3, 0),  # Dark
                }
            if previous_type in mapping:
                room.type = mapping[previous_type][0]
                room.color = mapping[previous_type][1]
            else:
                # Shouldn't really ever be able to get here
                room.type = Room.TYPE_NORMAL
                room.color = Room.COLOR_BW
        room.up = df.readstr()
        room.down = df.readstr()
        room.door_in = df.readstr()
        room.door_out = df.readstr()
        room.notes = df.readstr()
        flagbits = df.readuchar()
        if ((flagbits & 0x01) == 0x01):
            room.offset_y = True
        if ((flagbits & 0x02) == 0x02):
            room.offset_x = True
        if version >= 3:
            loopbackbits = df.readuchar()
            for direction in DIR_LIST:
                compvar = 1 << direction
                if ((loopbackbits & compvar) == compvar):
                    room.loopbacks[direction] = True
        return room

class ConnectionEnd(object):
    """
    An object describing one end of a connection.  This is, essentially, a
    glorified dict which is meant to hold onto four bits of information:
        1) The direction of the room that we're attached to
        2) The type of connection (regular, ladder, dotted)
        3) The "stub length" - how far out from the room before we start
           drawing towards the full connection's midpoint
        4) The method of rendering the path to the connection's midpoint
           (straight line, or single right-angle bend, in one of two 
           orientations)
    """

    CONN_REGULAR = 0
    CONN_LADDER = 1
    CONN_DOTTED = 2

    RENDER_REGULAR = 0
    RENDER_MIDPOINT_A = 1
    RENDER_MIDPOINT_B = 2

    STUB_REGULAR = 1
    STUB_MAX = 3

    def __init__(self, room, direction, conn_type=0, render_type=0, stub_length=1):
        self.room = room
        self.direction = direction
        self.conn_type = conn_type
        self.render_type = render_type
        self.stub_length = stub_length
        if self.stub_length < self.STUB_REGULAR:
            self.stub_length = self.STUB_REGULAR
        elif self.stub_length > self.STUB_MAX:
            self.stub_length = self.STUB_MAX

    def set_regular(self):
        self.conn_type = self.CONN_REGULAR

    def set_ladder(self):
        self.conn_type = self.CONN_LADDER

    def set_dotted(self):
        self.conn_type = self.CONN_DOTTED

    def is_regular(self):
        return (self.conn_type == self.CONN_REGULAR)

    def is_ladder(self):
        return (self.conn_type == self.CONN_LADDER)

    def is_dotted(self):
        return (self.conn_type == self.CONN_DOTTED)

    def set_render_regular(self):
        self.render_type = self.RENDER_REGULAR

    def set_render_midpoint_a(self):
        self.render_type = self.RENDER_MIDPOINT_A

    def set_render_midpoint_b(self):
        self.render_type = self.RENDER_MIDPOINT_B

    def is_render_regular(self):
        return (self.render_type == self.RENDER_REGULAR)

    def is_render_midpoint_a(self):
        return (self.render_type == self.RENDER_MIDPOINT_A)

    def is_render_midpoint_b(self):
        return (self.render_type == self.RENDER_MIDPOINT_B)

    def set_stub_length(self, stub_length=1):
        if stub_length < self.STUB_REGULAR:
            stub_length = self.STUB_REGULAR
        elif stub_length > self.STUB_MAX:
            stub_length = self.STUB_MAX
        self.stub_length = stub_length

    def increment_stub_length(self):
        """
        stub_length doesn't go to zero, which is why we're not just using
        the % operator here.
        """
        self.stub_length += 1
        if self.stub_length > self.STUB_MAX:
            self.stub_length = self.STUB_REGULAR

    def save(self, df):
        """
        Saves ourself to a filehandle
        """
        df.writeuchar(self.direction)
        df.writeuchar(self.conn_type)
        df.writeuchar(self.render_type)
        df.writeuchar(self.stub_length)

class Connection(object):
    """
    A connection between two rooms.  Mostly just a data container,
    the actual connection logic will be handled by the Room objects.
    Note that while we have a save() method here, like the other objects,
    loading is actually done inside the Map object, since it makes more
    sense in there.
    """

    PASS_TWOWAY = 0
    PASS_ONEWAY_A = 1
    PASS_ONEWAY_B = 2

    def __init__(self, r1, dir1, r2, dir2,
            passage=0,
            conn_type=ConnectionEnd.CONN_REGULAR,
            render_type=ConnectionEnd.RENDER_REGULAR,
            stub_length=ConnectionEnd.STUB_REGULAR):
        """
        Initialization of Connections.  New in savegame format v7 is supporting multiple
        directions on both sides of the connection, and the ability to tweak the
        connection parameters independently on each side.  `dir1` and `dir2` specify the
        "primary" connection between the two rooms - this one will be used to compute
        the midpoints of the connection (where all the various components will converge)
        and will render a bit more efficiently if possible (ie: if both ends of the
        connection are set to REGULAR_MIDPOINT and the same connection type, it'll render
        the line in one go rather than dividing it into parts).

        All the actual details of how to render the connections have moved into the
        ConnectionEnd object, which is stored in `ends1` and `ends2`.  This is a dict with
        the direction as keys.

        The one thing which isn't yet stored in ConnectionEnd is the oneway/twoway
        information, which feels like it should still sit up at the higher level.
        """
        self.r1 = r1
        self.dir1 = dir1
        self.ends1 = {dir1: ConnectionEnd(r1, dir1,
            conn_type=conn_type,
            render_type=render_type,
            stub_length=stub_length,
            )}
        self.r2 = r2
        self.dir2 = dir2
        self.ends2 = {dir2: ConnectionEnd(r2, dir2,
            conn_type=conn_type,
            render_type=render_type,
            stub_length=stub_length,
            )}
        self.passage = passage
        self.symmetric = True

        # Update a couple of Room vars here, while we're at it.
        self.r1.conns[self.dir1] = self
        self.r2.conns[self.dir2] = self

    def set_symmetric(self, symmetric=True, room=None, direction=None):
        """
        Sets our `symmetric` boolean which specifies whether the ConnectionEnd
        objects are allowed to drift from each other.  When specifying `False`,
        the only internal change is to update our `symmetric` boolean.  When
        specifying `True` (the default), all ConnectionEnd attributes will be
        updated to match the attributes of one of the Ends in the connection.
        If `room` and `direction` are not specified, this will always be the
        primary ConnectionEnd on r1's side.  If just `room` is specified, it'll
        be the primary ConnectionEnd on that room's side.  if both `room` and
        `direction` are specified, we'll chose that particular End.
        """
        if symmetric:

            # Don't do any work if we're already set True
            if not self.symmetric:

                self.symmetric = True

                # Choose a source End
                main_ce = None
                if room and direction:
                    main_ce = self.get_end(room, direction)
                if not main_ce and room:
                    if room == self.r1:
                        main_ce = self.ends1[self.dir1]
                    elif room == self.r2:
                        main_ce = self.ends2[self.dir2]
                if not main_ce:
                    main_ce = self.ends1[self.dir1]

                # Apply changes based on that End
                for end in self.get_all_ends():
                    if end != main_ce:
                        end.conn_type = main_ce.conn_type
                        end.stub_length = main_ce.stub_length
        else:
            self.symmetric = False

    def toggle_symmetric(self, room=None, direction=None):
        """
        Toggles symmetry of our connection.  Optionally pass in room and direction
        to specify which End should be considered the source for all Connection
        attributes, if it's going from nonsymmetric to symmetric.  This function
        useful for calling from the GUI, as opposed to `set_symmetric`
        """
        self.set_symmetric(not self.symmetric, room, direction)

    def get_primary_ends_dict(self, room):
        """
        Given a room, return a tuple containing:
            1) The "primary" direction of that side of the room
            2) the ends dict which matches the room
        """
        if room.idnum == self.r1.idnum:
            return (self.dir1, self.ends1)
        elif room.idnum == self.r2.idnum:
            return (self.dir2, self.ends2)
        else:
            raise Exception('Room %d is not part of connection %s' % (room.idnum, self))

    def get_all_ends(self):
        """
        Returns a list of all ConnectionEnds in this Connection
        """
        return list(self.ends1.values()) + list(self.ends2.values())

    def get_all_extra_ends(self):
        """
        Returns a list of all non-primary ends in this Connection
        """
        retlist = []
        for end in self.get_all_ends():
            if ((end.room == self.r1 and end.direction == self.dir1) or
                    (end.room == self.r2 and end.direction == self.dir2)):
                continue
            retlist.append(end)
        return retlist

    def get_end(self, room, direction):
        """
        Given a room and a direction, return the ConnectionEnd matching it.
        """
        if room.idnum == self.r1.idnum and direction in self.ends1:
            return self.ends1[direction]
        elif room.idnum == self.r2.idnum and direction in self.ends2:
            return self.ends2[direction]
        else:
            return None

    def get_end_list(self, room, direction):
        """
        Returns a list of ConnectionEnds to process, given both our internal
        `symmetric` boolean, and the specified room and direction.  If `symmetric`
        is `True`, this will be a list of all available ConnectionEnd objects inside
        this Connection.  Otherwise, it will be a list containing only the single
        End specified by the arguments.
        """
        if self.symmetric:
            return self.get_all_ends()
        else:
            end = self.get_end(room, direction)
            if end is None:
                return []
            else:
                return [end]

    def connect_extra(self, room, direction):
        """
        Adds an extra connection end to ourselves, with the specified parameters.  This will
        refuse to do anything if there's an existing connection or loopback in that direction
        on the room.  Will inherit its ConnectionEnd parameters from the primary connection
        endpoint of the room it's operating on.

        Returns the newly-created ConnectionEnd object, if one was created.  `None` otherwise.
        """
        if room == self.r1:
            endsvar = self.ends1
            attribute_end = self.ends1[self.dir1]
        elif room == self.r2:
            endsvar = self.ends2
            attribute_end = self.ends2[self.dir2]
        else:
            raise Exception('Specified room %s is not part of Connection %s' % (room.idnum, self))
        
        if (direction not in room.loopbacks and direction not in room.conns and
                direction not in endsvar):
            room.conns[direction] = self
            endsvar[direction] = ConnectionEnd(room, direction,
                conn_type=attribute_end.conn_type,
                render_type=attribute_end.render_type,
                stub_length=attribute_end.stub_length)
            return endsvar[direction]
        
        return None

    def move_end(self, room_from, direction_from, room_to, direction_to):
        """
        Moves the specified end from one point on the existing room, to another
        point (potentially on a completely different room).  If there's more
        than one end connected to `room_from`, this will do nothing, rather
        than trying to guess what to do with the non-moved ends.  Will also
        refuse to do anything if there is already a connection or loopback at
        the destination.  Another no-op possibility is trying to create a
        connection which goes from a room back into itself.

        Returns `True` if the end was moved, or `False` otherwise.
        """

        # First up: make sure that we've actually been told to change something
        if room_from == room_to and direction_from == direction_to:
            return False

        # Make sure we've got a valid End to move
        from_end = self.get_end(room_from, direction_from)
        if not from_end:
            raise Exception('Given from_room does not involve this connection')

        # Make sure the destination is open
        if room_to.get_loopback(direction_to) or room_to.get_conn(direction_to):
            return False

        # Figure out what side of the connection we're operating on
        if room_from == self.r1:
            ends = self.ends1
            unchanged_room = self.r2
            primary_dir = self.dir1
        else:
            ends = self.ends2
            unchanged_room = self.r1
            primary_dir = self.dir2

        # Check to see if we've been told to link back to the other side
        if room_to == unchanged_room:
            return False

        # If we're changing rooms, check to see if there's more than one
        # End on the side we're dealing with.  Return False if so, because
        # we don't want to have to guess what to do with the extra ends.
        # If we're sticking within the same room, though, that's okay.
        update_primary_dir = True
        if room_to == room_from:
            if primary_dir != direction_from:
                update_primary_dir = False
        else:
            if len(ends) > 1:
                return False

        # So - if we got here, we're good to go!
        del room_from.conns[direction_from]
        if update_primary_dir:
            if unchanged_room == self.r1:
                self.r2 = room_to
                self.dir2 = direction_to
            else:
                self.r1 = room_to
                self.dir1 = direction_to
        room_to.conns[direction_to] = self
        if direction_from != direction_to:
            ends[direction_to] = ends[direction_from]
            del ends[direction_from]
        ends[direction_to].room = room_to
        ends[direction_to].direction = direction_to

        # Aand if we got here, return True
        return True

    def is_primary(self, room, direction):
        """
        Returns `True` if the given room/direction is one of the primary
        Ends for this connection
        """
        return ((room == self.r1 and direction == self.dir1) or
                (room == self.r2 and direction == self.dir2))

    def set_primary(self, room, direction):
        """
        Sets the given ConnectionEnd to be the primary for the connection, if
        it isn't already.  Will update the `render_type` of the far end if need
        be, since those should remain locked together.
        """
        end = self.get_end(room, direction)
        if end:
            if room == self.r1:
                self.dir1 = direction
                self.ends2[self.dir2].render_type = self.ends1[self.dir1].render_type
            else:
                self.dir2 = direction
                self.ends1[self.dir1].render_type = self.ends2[self.dir2].render_type

    def set_regular(self, room, direction):
        for end in self.get_end_list(room, direction):
            end.set_regular()

    def set_ladder(self, room, direction):
        for end in self.get_end_list(room, direction):
            end.set_ladder()

    def set_dotted(self, room, direction):
        for end in self.get_end_list(room, direction):
            end.set_dotted()

    def cycle_conn_type(self, room, direction):
        """
        Cycle through our available conn_types
        """
        end = self.get_end(room, direction)
        if end:
            if end.is_regular():
                self.set_ladder(room, direction)
            elif end.is_ladder():
                self.set_dotted(room, direction)
            else:
                self.set_regular(room, direction)

    def get_render_type_change_endlist(self, room, direction):
        """
        Unlike other attributes stored in ConnectionEnd, render_type
        does NOT follow our symmetry attribute, since it doesn't
        really make sense for this attribute.  The primary Ends will
        always remain synced, though.
        """
        if ((room == self.r1 and direction == self.dir1) or
                (room == self.r2 and direction == self.dir2)):
            return [self.ends1[self.dir1], self.ends2[self.dir2]]
        else:
            end = self.get_end(room, direction)
            if end:
                return [end]
            else:
                return []

    def set_render_regular(self, room, direction):
        for end in self.get_render_type_change_endlist(room, direction):
            end.set_render_regular()

    def set_render_midpoint_a(self, room, direction):
        for end in self.get_render_type_change_endlist(room, direction):
            end.set_render_midpoint_a()

    def set_render_midpoint_b(self, room, direction):
        for end in self.get_render_type_change_endlist(room, direction):
            end.set_render_midpoint_b()

    def cycle_render_type(self, room, direction):
        """
        Cycles through all available render types
        """
        end = self.get_end(room, direction)
        if end:
            if end.is_render_regular():
                self.set_render_midpoint_a(room, direction)
            elif end.is_render_midpoint_a():
                self.set_render_midpoint_b(room, direction)
            else:
                self.set_render_regular(room, direction)

    def set_stub_length(self, room, direction, stub_length=ConnectionEnd.STUB_REGULAR):
        for end in self.get_end_list(room, direction):
            end.set_stub_length(stub_length)

    def increment_stub_length(self, room, direction):
        for end in self.get_end_list(room, direction):
            end.increment_stub_length()

    def set_twoway(self):
        self.passage = self.PASS_TWOWAY

    def set_oneway_a(self):
        self.passage = self.PASS_ONEWAY_A

    def set_oneway_b(self):
        self.passage = self.PASS_ONEWAY_B

    def cycle_passage(self):
        """
        Cycles through all available `passage` values
        """
        if self.is_twoway():
            self.set_oneway_a()
        elif self.is_oneway_a():
            self.set_oneway_b()
        else:
            self.set_twoway()

    def is_twoway(self):
        return (self.passage == self.PASS_TWOWAY)

    def is_oneway_a(self):
        return (self.passage == self.PASS_ONEWAY_A)

    def is_oneway_b(self):
        return (self.passage == self.PASS_ONEWAY_B)

    def is_oneway(self):
        return (self.is_oneway_a() or self.is_oneway_b())

    def __repr__(self):
        if (self.is_oneway_a()):
            conntext = '<-'
        elif (self.is_oneway_b()):
            conntext = '->'
        else:
            conntext = '<->'
        return '<Connection - %s (%s) %s %s (%s)>' % (
                self.r1.name,
                ', '.join([DIR_2_TXT[d] for d in self.ends1.keys()]),
                conntext,
                self.r2.name,
                ', '.join([DIR_2_TXT[d] for d in self.ends2.keys()]),
                )

    def get_opposite(self, room):
        """
        Given a room, return a tuple of (room, dirs) corresponding
        to the "other" end of the room.  `dirs` is a list
        """
        if (room.idnum == self.r1.idnum):
            return (self.r2, list(self.ends2.keys()))
        elif (room.idnum == self.r2.idnum):
            return (self.r1, list(self.ends1.keys()))
        else:
            raise Exception('Room %d not valid for this connection' % (room.idnum))

    def save(self, df):
        """
        Saves ourself to a filehandle
        """

        flagbits = 0
        if (self.symmetric):
            flagbits = flagbits | 0x1

        df.writeshort(self.r1.idnum)
        df.writeuchar(self.dir1)
        df.writeshort(self.r2.idnum)
        df.writeuchar(self.dir2)
        df.writeuchar(self.passage)
        df.writeuchar(flagbits)

        # We're going to go ahead and sort the ends that we write
        # out, so that there's no chance of functionally-identical
        # maps containing different data.  Would like to be able to
        # diff map files without having to take internal ordering
        # into account.

        df.writeuchar(len(self.ends1))
        for direction in sorted(self.ends1.keys()):
            self.ends1[direction].save(df)

        df.writeuchar(len(self.ends2))
        for direction in sorted(self.ends2.keys()):
            self.ends2[direction].save(df)

class Map(object):
    """
    One map, or a collection of rooms
    """

    # TODO: we're hardcoding 9x9 at the moment
    def __init__(self, name):
        self.name = name
        self.set_map_size(9, 9)

    def set_map_size(self, w, h):
        """
        Sets a new map size; note that this will completely wipe the map.
        """
        self.w = w
        self.h = h

        # Populate rooms
        self.cur_id = 0
        self.rooms = {}
        self.roomxy = []
        for y in range(self.h):
            self.roomxy.append([])
            for x in range(self.w):
                self.roomxy[-1].append(None)

        # ... and wipe our collection of conns
        self.conns = []

        # ... and our groups
        self.groups = []

    def duplicate(self, newname=None):
        """
        Returns a duplicate of ourself.
        """
        if newname:
            newmap = Map(newname)
        else:
            newmap = Map(self.name)
        newmap.set_map_size(self.w, self.h)
        for room in self.roomlist():
            newroom = room.duplicate()
            newmap.inject_room_obj(newroom)
        for conn in self.conns:
            newconn = newmap.connect_id(conn.r1.idnum, conn.dir1, conn.r2.idnum, conn.dir2)
            newconn.passage = conn.passage
            newconn.symmetric = conn.symmetric
            for (new_room, primary_dir, orig_ends, new_ends) in [(newconn.r1, newconn.dir1, conn.ends1, newconn.ends1),
                    (newconn.r2, newconn.dir2, conn.ends2, newconn.ends2)]:
                for orig_end in orig_ends.values():
                    ce = newconn.connect_extra(new_room, orig_end.direction)
                    if ce is None:
                        if orig_end.direction == primary_dir:
                            ce = new_ends[orig_end.direction]
                        else:
                            raise Exception('Unable to get ConnectionEnd for duplicated Map')
                    ce.conn_type = orig_end.conn_type
                    ce.render_type = orig_end.render_type
                    ce.stub_length = orig_end.stub_length
        for group in self.groups:
            r1 = newmap.get_room(group.rooms[0].idnum)
            r2 = newmap.get_room(group.rooms[1].idnum)
            newmap.group_rooms(r1, r2)
            for room in group.rooms[2:]:
                newmap.group_rooms(newmap.get_room(room.idnum), r1)
        return newmap

    def roomlist(self):
        """
        Returns a list of our rooms
        """
        return list(self.rooms.values())

    def grab_id(self):
        """
        Returns the next available ID
        """
        looped = False
        while (self.cur_id in self.rooms):
            self.cur_id += 1
            if (self.cur_id == 65536):
                self.cur_id = 0
                if looped:
                    raise Exception('No free room IDs!')
                looped = True
        return self.cur_id

    def inject_room_obj(self, room):
        """
        Injects a room object.  Make sure to keep this in
        sync with add_room_at.
        """
        if self.roomxy[room.y][room.x]:
            raise Exception('Attempt to overwrite existing room at (%d, %d)' % (room.x+1, room.y+1))
        if (room.idnum in self.rooms):
            raise Exception('Room ID %d already exists' % (room.idnum))
        self.rooms[room.idnum] = room
        self.roomxy[room.y][room.x] = room

    def add_room_at(self, x, y, name):
        """
        Adds a new room at (x, y), with no connections.
        Make sure to keep this in sync with inject_room_obj
        """
        # TODO: this limit is actually because of the way the GUI handles the mousemaps
        if (len(self.rooms) >= 256):
            raise Exception('Can only have 256 rooms on a map currently; sorry...')
        if self.roomxy[y][x]:
            raise Exception('A room already exists at (%d, %d)' % (x+1, y+1))
        idnum = self.grab_id()
        if idnum in self.rooms: # pragma: nocover
            # There's really no conceivable way we could ever get here
            raise Exception('A room already exists with ID %d' % (idnum))
        self.rooms[idnum] = Room(idnum, x, y)
        self.rooms[idnum].name = name
        self.roomxy[y][x] = self.rooms[idnum]
        return self.rooms[idnum]

    def get_room(self, idnum):
        """
        Gets the specified room
        """
        if (idnum in self.rooms):
            return self.rooms[idnum]
        else:
            return None

    def get_room_at(self, x, y):
        """
        Gets the specified room
        """
        return self.roomxy[y][x]

    def connect(self, room1, dir1, room2, dir2=None):
        """
        Connects two rooms, given the room objects and
        the direction.  If a second direction is not provided,
        the connection will be symmetrical.  Returns the new
        connection, or None if something got in the way
        """
        # TODO: Note that technically we're limited to 65535
        # conns because we store the number of conns as a
        # short in the file.  Given our current 256-room
        # limit, there's not much point checking for it, but
        # should we ever lift that, it's at least technically
        # possible that some determined maniac could run up
        # against the limit, so we should check for it if so.
        if dir2 is None:
            dir2 = DIR_OPP[dir1]
        if dir1 in room1.conns or dir1 in room1.loopbacks:
            return None
        if dir2 in room2.conns or dir2 in room2.loopbacks:
            return None
        self.conns.append(room1.connect(dir1, room2, dir2))
        return self.conns[-1]

    def connect_id(self, id1, dir1, id2, dir2=None):
        """
        Connects two rooms, given the room IDs.  Returns the new connection.
        """
        room1 = self.get_room(id1)
        room2 = self.get_room(id2)
        if (not room1 or not room2):
            raise Exception('Must specify two valid rooms')
        return self.connect(room1, dir1, room2, dir2)

    def detach(self, room, direction):
        """
        Detaches two rooms
        """
        conn = room.get_conn(direction)
        if conn or room.get_loopback(direction):
            delete_conn = room.detach(direction)
            if delete_conn and conn:
                self.conns.remove(conn)

    def detach_id(self, idnum, direction):
        """
        Detaches two rooms, based on the ID
        """
        room = self.get_room(idnum)
        if (not room):
            raise Exception('Must specify a valid room')
        return self.detach(room, direction)

    def del_room(self, room):
        """
        Deletes a room, and removes all former connections to
        that room, and also removes the room from its group,
        if necessary.
        """
        idnum = room.idnum
        x = room.x
        y = room.y
        if room.group:
            self.remove_room_from_group(room)
        for direction in list(room.conns.keys()):
            self.detach(room, direction)
        del self.rooms[idnum]
        self.roomxy[y][x] = None

    def dir_coord(self, room, direction, allow_invalid=False):
        """
        Returns (x, y) coordinates of the space to the `direction` of the
        given room.

        If allow_invalid is true, this will return coordinates even outside
        the actual map range (less than zero, or greater than the maximums.

        Will return None if allow_invalid is False (the default).
        """
        x = room.x
        y = room.y
        if (direction in [DIR_NW, DIR_W, DIR_SW]):
            if (x == 0 and not allow_invalid):
                return None
            x -= 1
        if (direction in [DIR_NE, DIR_E, DIR_SE]):
            if (x == self.w-1 and not allow_invalid):
                return None
            x += 1
        if (direction in [DIR_NW, DIR_N, DIR_NE]):
            if (y == 0 and not allow_invalid):
                return None
            y -= 1
        if (direction in [DIR_SW, DIR_S, DIR_SE]):
            if (y == self.h-1 and not allow_invalid):
                return None
            y += 1
        return (x, y)

    def move_room(self, room, direction):
        """
        Attempts to move a room one space in the specified direction.
        Will return True/False depending on success.
        """
        new_coords = self.dir_coord(room, direction)
        if not new_coords:
            return False
        new_room = self.get_room_at(*new_coords)
        if new_room:
            return False
        self.roomxy[room.y][room.x] = None
        room.x = new_coords[0]
        room.y = new_coords[1]
        self.roomxy[room.y][room.x] = room
        return True

    def nudge(self, direction, roomset=None):
        """
        Attempts to "nudge" a map in the given direction, optionally
        only acting on a set of passed-in rooms.  Will return
        True/False depending on success
        """

        # Operate on all rooms if we weren't told otherwise
        if roomset is None:
            roomset = set(self.roomlist())

        # Sanity check
        if len(roomset) == 0:
            return False

        # Loop through and make sure that we're capable of nudging
        # the specified rooms.  If the edge of the map or another
        # room not in our passed-in set is blocking, return False
        # right away.
        for room in roomset:
            adj_dir = self.dir_coord(room, direction)
            if not adj_dir:
                return False
            adj_room = self.get_room_at(*adj_dir)
            if adj_room and adj_room not in roomset:
                return False

        if (direction in [DIR_W, DIR_NW, DIR_N, DIR_NE]):
            for y in range(len(self.roomxy)):
                for x in range(len(self.roomxy[y])):
                    if self.roomxy[y][x] and self.roomxy[y][x] in roomset:
                        self.move_room(self.roomxy[y][x], direction)
        else:
            for y in range(len(self.roomxy)-1, -1, -1):
                for x in range(len(self.roomxy[y])-1, -1, -1):
                    if self.roomxy[y][x] and self.roomxy[y][x] in roomset:
                        self.move_room(self.roomxy[y][x], direction)
        return True

    def resize(self, direction):
        """
        Resizes the map, if possible
        """
        if (direction == DIR_E):
            # Limitations in W/H are due to storing these
            # as chars in the savefile.  And also because
            # seriously, what are you doing with a map that big?
            if (self.w == 255):
                return False
            self.w += 1
            for row in self.roomxy:
                row.append(None)
            return True
        elif (direction == DIR_S):
            if (self.h == 255):
                return False
            self.h += 1
            self.roomxy.append([])
            for x in range(self.w):
                self.roomxy[-1].append(None)
            return True
        elif (direction == DIR_W):
            if (self.w == 1):
                return False
            for row in self.roomxy:
                if row[-1]:
                    return False
            self.w -= 1
            for row in self.roomxy:
                row.pop()
            return True
        elif (direction == DIR_N):
            if (self.h == 1):
                return False
            for room in self.roomxy[-1]:
                if room:
                    return False
            self.h -= 1
            self.roomxy.pop()
            return True
        else:
            return False

    def remove_room_from_group(self, room):
        """
        Removes the given room from its group.  Returns True
        if something was changed, False otherwise.
        """
        group = room.group
        if group:
            to_delete = group.del_room(room)
            if (to_delete):
                for other_room in group.get_rooms():
                    group.del_room(other_room)
                self.groups.remove(group)
            return True
        else:
            return False

    def group_rooms(self, room1, room2):
        """
        Puts `room1` and `room2` into a group together, if possible.
        If neither are in a group currently, a new one is created.
        If one of the two is in a group but the other isn't, the
        non-grouped room will be added to the group.  If both are
        already in a group, nothing will be changed.

        Returns True if we changed anything, or False otherwise.
        (This is primarily for the benefit of the GUI, to know if
        anything needs to be redrawn)
        """
        if room1.group and room2.group:
            return False
        elif not room1.group and not room2.group:
            if room1 != room2:
                self.groups.append(Group(room1, room2))
                return True
            else:
                return False
        else:
            if room1.group:
                room1.group.add_room(room2)
            else:
                room2.group.add_room(room1)
            return True

    def save(self, df):
        """
        Saves the map to the given filehandle
        """
        df.writestr(self.name)
        df.writeuchar(self.w)
        df.writeuchar(self.h)
        df.writeshort(len(self.rooms))
        df.writeshort(len(self.conns))
        df.writeshort(len(self.groups))
        for room in self.roomlist():
            room.save(df)
        for conn in self.conns:
            conn.save(df)
        for group in self.groups:
            group.save(df)

    @staticmethod
    def load(df, version):
        """
        Loads a map from the given filehandle
        """
        advmap = Map(df.readstr())
        advmap.set_map_size(df.readuchar(), df.readuchar())
        num_rooms = df.readshort()
        num_conns = df.readshort()
        num_groups = df.readshort()

        # Load rooms
        for i in range(num_rooms):
            advmap.inject_room_obj(Room.load(df, version))

        # Now load connections
        for i in range(num_conns):
            conn = advmap.connect_id(df.readshort(), df.readuchar(), df.readshort(), df.readuchar())
            if version >= 7:
                conn.passage = df.readuchar()
                flagbits = df.readuchar()
                if ((flagbits & 0x01) == 0x01):
                    conn.symmetric = True
                else:
                    conn.symmetric = False
                for (room, primary_dir, ends) in [(conn.r1, conn.dir1, conn.ends1),
                        (conn.r2, conn.dir2, conn.ends2)]:
                    num_ends = df.readuchar()
                    for j in range(num_ends):
                        direction = df.readuchar()
                        conn_type = df.readuchar()
                        render_type = df.readuchar()
                        stub_length = df.readuchar()
                        ce = conn.connect_extra(room, direction)
                        if ce is None:
                            if direction == primary_dir:
                                ce = ends[direction]
                            else:
                                raise LoadException('Found an existing ConnectionEnd where we shouldn\'t')
                        ce.conn_type = conn_type
                        ce.render_type = render_type
                        ce.stub_length = stub_length
            else:
                ends = conn.get_all_ends()
                conn_type = df.readuchar()
                for end in ends:
                    end.conn_type = conn_type
                if version >= 2:
                    conn.passage = df.readuchar()
                if version >= 4:
                    render_type = df.readuchar()
                    for end in ends:
                        end.render_type = render_type
                if version >= 5:
                    stub_length = df.readuchar()
                    for end in ends:
                        end.stub_length = stub_length

        # Now load groups
        for i in range(num_groups):
            advmap.groups.append(Group.load(df, advmap, version))

        # ... and return our object.
        return advmap

class Game(object):
    """
    Data for a single game - Games are actually collections
    of Maps, which are themselves collections of rooms
    """

    def __init__(self, name):
        self.name = name
        self.maps = []

    def add_map_obj(self, mapobj):
        """
        Adds the specified Map object to our array, and return the index
        of the map.
        """
        self.maps.append(mapobj)
        return len(self.maps)-1

    def add_map(self, name):
        """
        Adds a new map with the given name.  Returns a tuple containing:
           1) The Index of the map
           2) The map object itself
        """
        mapobj = Map(name)
        return (self.add_map_obj(mapobj), mapobj)

    def replace_maps(self, maps):
        """
        Used to replace our current map list.  Mostly here to
        support the GUI reordering.
        """
        self.maps = maps

    def _save(self, df):
        """
        Save ourselves to a Savefile object
        """
        df.write('ADVMAP')
        df.writeshort(SAVEFILE_VER)
        df.writestr(self.name)
        df.writeshort(len(self.maps))
        for mapobj in self.maps:
            mapobj.save(df)

    def save(self, filename):
        """
        Saves the game maps to a filename.  This is the main
        routine that the GUI will end up calling - the heavy lifting
        is actually done in the internal `_save` routine.
        """
        df = Savefile(filename)
        df.open_w()
        self._save(df)
        df.close()

    @staticmethod
    def _load(df):
        """
        Loads ourselves from a Savefile object.  Returns the Game object.
        """
        openstr = df.read(6)
        if (openstr != 'ADVMAP'):
            raise LoadException('Invalid Map File specified')
        version = df.readshort()
        if (version > SAVEFILE_VER):
            raise LoadException('Map file is version %d, we can only open versions %d and lower' % (version, SAVEFILE_VER))
        name = df.readstr()
        game = Game(name)
        num_maps = df.readshort()
        for i in range(num_maps):
            game.add_map_obj(Map.load(df, version))
        return game

    @staticmethod
    def load(filename):
        """
        Loads a game from a filename.  Returns the Game object
        """
        df = Savefile(filename)
        df.open_r()
        game = Game._load(df)
        df.close()
        return game
