#!/usr/bin/python
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

__all__ = [ 'Room', 'Connection', 'Map', 'Game', 
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

SAVEFILE_VER = 4

class Group(object):
    """
    A group of rooms, used for drawing screens in graphical
    adventure games which have multiple "levels" with their own
    connections, which nevertheless all take up one screen.
    (Could also be used for other purposes as well, of course)
    """
    def __init__(self, room1, room2):
        self.rooms = []
        self.add_room(room1)
        self.add_room(room2)

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

    def save(self, df):
        """
        Saves ourself to the given filehandle
        """
        if (len(self.get_rooms()) < 2):
            raise Exception('Warning: a group cannot consist of only one room')
        df.writeshort(len(self.get_rooms()))
        for room in self.get_rooms():
            df.writeshort(room.id)

    @staticmethod
    def load(df, map, version):
        """
        Loads ourself, given a map object (to do room lookups) and a filehandle
        """
        num_rooms = df.readshort()
        if (num_rooms < 2):
            raise LoadException('Group stated it had only %d rooms' % (num_rooms))
        rooms = []
        for i in range(num_rooms):
            id = df.readshort()
            room = map.get_room(id)
            if (room is None):
                raise LoadException('Room %d does not exist while loading group' % (id))
            rooms.append(room)
        group = Group(rooms[0], rooms[1])
        for room in rooms[2:]:
            group.add_room(room)
        return group

class Room(object):
    """
    A single room
    """

    # Type constants
    TYPE_NORMAL = 0
    TYPE_HI_GREEN = 1
    TYPE_LABEL = 2
    TYPE_HI_BLUE = 3
    TYPE_HI_RED = 4
    TYPE_FAINT = 5
    TYPE_HI_YELLOW = 6
    TYPE_HI_PURPLE = 7
    TYPE_HI_CYAN = 8
    TYPE_DARK = 9

    # English equivalents
    TYPE_TXT = {
            TYPE_NORMAL: 'Normal Room',
            TYPE_HI_GREEN: 'Green Highlight',
            TYPE_LABEL: 'Label',
            TYPE_HI_BLUE: 'Blue Highlight',
            TYPE_HI_RED: 'Red Highlight',
            TYPE_FAINT: 'Unimportant',
            TYPE_HI_YELLOW: 'Yellow Highlight',
            TYPE_HI_PURPLE: 'Purple Highlight',
            TYPE_HI_CYAN: 'Cyan Highlight',
            TYPE_DARK: 'Dark'
        }

    def __init__(self, id, x, y):
        self.id = id
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
        self.offset_x = False
        self.offset_y = False
        self.group = None

    def duplicate(self):
        """
        Returns a copy of ourself.  Note that this doesn't
        copy connections or groups; that has to be handled by
        the Map object
        """
        newroom = Room(self.id, self.x, self.y)
        newroom.name = self.name
        newroom.notes = self.notes
        newroom.up = self.up
        newroom.down = self.down
        newroom.door_in = self.door_in
        newroom.door_out = self.door_out
        newroom.type = self.type
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

    def set_loopback(self, dir):
        """
        Sets a loopback at the given direction
        """
        if dir in self.conns:
            self.detach(dir)
        self.loopbacks[dir] = True

    def attach_conn(self, conn):
        """
        Attaches the given connection to our room, without
        modifying the connection at all.  Useful when the GUI
        is modifying connection parameters and we don't want
        to build up a totally new Connection object.
        """
        if conn.r1 == self:
            if conn.dir1 in self.conns or conn.dir1 in self.loopbacks:
                self.detach(conn.dir1)
            self.conns[conn.dir1] = conn
        elif conn.r2 == self:
            if conn.dir2 in self.conns or conn.dir2 in self.loopbacks:
                self.detach(conn.dir2)
            self.conns[conn.dir2] = conn
        else:
            raise Exception('Given connection does not involve this room')

    def connect(self, dir, room, dir2=None):
        """
        Connects ourself to another room.  Note
        that we expect another Room object here, and
        that any new connection will disconnect any
        existing connection.  Will return the new Connection
        object which was created
        """
        if dir2 is None:
            dir2 = DIR_OPP[dir]
        if dir in self.conns or dir in self.loopbacks:
            self.detach(dir)
        if dir2 in room.conns:
            room.detach(dir2)
        conn = Connection(self, dir, room, dir2)
        self.conns[dir] = conn
        room.conns[dir2] = conn
        return conn

    def detach(self, dir):
        """
        Detaches ourself from a direction.  Will
        additionally detach the opposite end.
        """
        if dir not in self.conns and dir not in self.loopbacks:
            raise Exception('No connections or loopbacks to detach')
        if dir in self.conns:
            conn = self.conns[dir]
            (other, other_dir) = conn.get_opposite(self)
            del self.conns[dir]
            del other.conns[other_dir]
        if dir in self.loopbacks:
            del self.loopbacks[dir]

    def detach_single(self, dir):
        """
        Detaches ourselves from the given direction.  Will not
        touch the opposite end.
        """
        if dir in self.conns:
            del self.conns[dir]
        if dir in self.loopbacks:
            del self.loopbacks[dir]

    def get_loopback(self, dir):
        """
        Returns True if there's a loopback at the given direction,
        False otherwise.
        """
        return (dir in self.loopbacks)

    def get_conn(self, dir):
        """
        Returns the Connection object at our given direction, if
        we can.  Returns None otherwise.
        """
        if dir in self.conns:
            return self.conns[dir]
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

    def save(self, df):
        """
        Writes ourself to the given filehandle
        """
        flagbits = 0
        if (self.offset_x):
            flagbits = flagbits | 0x2
        if (self.offset_y):
            flagbits = flagbits | 0x1
        df.writeshort(self.id)
        df.writeuchar(self.x)
        df.writeuchar(self.y)
        df.writestr(self.name)
        df.writeuchar(self.type)
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
        id = df.readshort()
        x = df.readuchar()
        y = df.readuchar()
        room = Room(id, x, y)
        room.name = df.readstr()
        room.type = df.readuchar()
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

class Connection(object):
    """
    A connection between two rooms.  Mostly just a data container,
    the actual connection logic will be handled by the Room objects.
    Note that while we have a save() method here, like the other objects,
    loading is actually done inside the Map object, since it makes more
    sense in there.
    """

    CONN_REGULAR = 0
    CONN_LADDER = 1
    CONN_DOTTED = 2

    PASS_TWOWAY = 0
    PASS_ONEWAY_A = 1
    PASS_ONEWAY_B = 2

    RENDER_REGULAR = 0
    RENDER_MIDPOINT_A = 1
    RENDER_MIDPOINT_B = 2

    def __init__(self, r1, dir1, r2, dir2, type=0, passage=0, render=0):
        self.r1 = r1
        self.dir1 = dir1
        self.r2 = r2
        self.dir2 = dir2
        self.type = type
        self.passage = passage
        self.render = render

    def set_regular(self):
        self.type = self.CONN_REGULAR

    def set_ladder(self):
        self.type = self.CONN_LADDER

    def set_dotted(self):
        self.type = self.CONN_DOTTED

    def is_regular(self):
        return (self.type == self.CONN_REGULAR)

    def is_ladder(self):
        return (self.type == self.CONN_LADDER)

    def is_dotted(self):
        return (self.type == self.CONN_DOTTED)

    def set_twoway(self):
        self.passage = self.PASS_TWOWAY

    def set_oneway_a(self):
        self.passage = self.PASS_ONEWAY_A

    def set_oneway_b(self):
        self.passage = self.PASS_ONEWAY_B

    def is_twoway(self):
        return (self.passage == self.PASS_TWOWAY)

    def is_oneway_a(self):
        return (self.passage == self.PASS_ONEWAY_A)

    def is_oneway_b(self):
        return (self.passage == self.PASS_ONEWAY_B)

    def is_oneway(self):
        return (self.is_oneway_a() or self.is_oneway_b())

    def set_render_regular(self):
        self.render = self.RENDER_REGULAR

    def set_render_midpoint_a(self):
        self.render = self.RENDER_MIDPOINT_A

    def set_render_midpoint_b(self):
        self.render = self.RENDER_MIDPOINT_B

    def is_render_regular(self):
        return (self.render == self.RENDER_REGULAR)

    def is_render_midpoint_a(self):
        return (self.render == self.RENDER_MIDPOINT_A)

    def is_render_midpoint_b(self):
        return (self.render == self.RENDER_MIDPOINT_B)

    def __repr__(self):
        if (self.is_oneway_a()):
            conntext = '<-'
        elif (self.is_oneway_b()):
            conntext = '->'
        else:
            conntext = '<->'
        return '<Connection - %s (%s) %s %s (%s)>' % (self.r1.name, DIR_2_TXT[self.dir1], conntext, self.r2.name, DIR_2_TXT[self.dir2])

    def get_opposite(self, room):
        """
        Given a room, return a tuple of (room, dir) corresponding
        to the "other" end of the room.
        """
        # TODO: Again note that this doesn't support self-looping conns
        if (room.id == self.r1.id):
            return (self.r2, self.dir2)
        else:
            return (self.r1, self.dir1)

    def save(self, df):
        """
        Saves ourself to a filehandle
        """
        df.writeshort(self.r1.id)
        df.writeuchar(self.dir1)
        df.writeshort(self.r2.id)
        df.writeuchar(self.dir2)
        df.writeuchar(self.type)
        df.writeuchar(self.passage)
        df.writeuchar(self.render)

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
            newconn = newmap.connect_id(conn.r1.id, conn.dir1, conn.r2.id, conn.dir2)
            newconn.type = conn.type
        for group in self.groups:
            r1 = newmap.get_room(group.rooms[0].id)
            r2 = newmap.get_room(group.rooms[1].id)
            newmap.add_room_to_group(r1, r2)
            for room in group.rooms[2:]:
                newmap.add_room_to_group(newmap.get_room(room.id), r1)
        return newmap

    def roomlist(self):
        """
        Returns a list of our rooms
        """
        return self.rooms.values()

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
        if (room.id in self.rooms):
            raise Exception('Room ID %d already exists' % (room.id))
        self.rooms[room.id] = room
        self.roomxy[room.y][room.x] = room

    def add_room_at(self, x, y, name):
        """
        Adds a new room at (x, y), with no connections.
        Make sure to keep this in sync with inject_room_obj
        """
        # TODO: this limit is actually because of the way the GUI handles the mousemaps
        if (len(self.rooms) == 256):
            raise Exception('Can only have 256 rooms on a map currently; sorry...')
        if self.roomxy[y][x]:
            raise Exception('A room already exists at (%d, %d)' % (x+1, y+1))
        id = self.grab_id()
        if id in self.rooms:
            raise Exception('A room already exists with ID %d' % (id))
        self.rooms[id] = Room(id, x, y)
        self.rooms[id].name = name
        self.roomxy[y][x] = self.rooms[id]
        return self.rooms[id]

    def get_room(self, id):
        """
        Gets the specified room
        """
        if (id in self.rooms):
            return self.rooms[id]
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
        connection.
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
        if dir1 in room1.conns:
            self.detach(room1, dir1)
        if dir2 in room2.conns:
            self.detach(room2, dir2)
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

    def _detach_conn(self, conn):
        """
        Processes the detach of the given Connection object
        """
        # TODO: if we ever support conns which loop back
        # to the same room, we'll have to watch for that.
        self.conns.remove(conn)
        conn.r1.detach(conn.dir1)

    def detach(self, room, dir):
        """
        Detaches two rooms
        """
        # TODO: interaction with _detach_conn is bizarre now that
        # we're doing this loopback thing.
        conn = room.get_conn(dir)
        if conn:
            self._detach_conn(conn)
        if room.get_loopback(dir):
            room.detach(dir)

    def detach_id(self, id, dir):
        """
        Detaches two rooms, based on the ID
        """
        room = self.get_room(id)
        if (not room):
            raise Exception('Must specify a valid room')
        return self.detach(room, dir)

    def del_room(self, room):
        """
        Deletes a room, and removes all former connections to
        that room, and also removes the room from its group,
        if necessary.
        """
        id = room.id
        x = room.x
        y = room.y
        if room.group:
            self.remove_room_from_group(room)
        for (dir, conn) in room.conns.items():
            self._detach_conn(conn)
        del self.rooms[id]
        self.roomxy[y][x] = None

    def dir_coord(self, room, dir, allow_invalid=False):
        """
        Returns (x, y) coordinates of the space to the "dir" of the
        given room.

        If allow_invalid is true, this will return coordinates even outside
        the actual map range (less than zero, or greater than the maximums.

        Will return None if allow_invalid is False (the default).
        """
        x = room.x
        y = room.y
        if (dir in [DIR_NW, DIR_W, DIR_SW]):
            if (x == 0 and not allow_invalid):
                return None
            x -= 1
        if (dir in [DIR_NE, DIR_E, DIR_SE]):
            if (x == self.w-1 and not allow_invalid):
                return None
            x += 1
        if (dir in [DIR_NW, DIR_N, DIR_NE]):
            if (y == 0 and not allow_invalid):
                return None
            y -= 1
        if (dir in [DIR_SW, DIR_S, DIR_SE]):
            if (y == self.h-1 and not allow_invalid):
                return None
            y += 1
        return (x, y)

    def move_room(self, room, dir):
        """
        Attempts to move a room one space in the specified direction.
        Will return True/False depending on success.
        """
        new_coords = self.dir_coord(room, dir)
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

    def nudge(self, dir):
        """
        Attempts to "nudge" a map in the given direction.  Will return
        True/False depending on success
        """
        for room in self.roomlist():
            if room and not self.dir_coord(room, dir):
                return False
        if (dir in [DIR_W, DIR_NW, DIR_N, DIR_NE]):
            for y in range(len(self.roomxy)):
                for x in range(len(self.roomxy[y])):
                    if self.roomxy[y][x]:
                        self.move_room(self.roomxy[y][x], dir)
        else:
            for y in range(len(self.roomxy)-1, -1, -1):
                for x in range(len(self.roomxy[y])-1, -1, -1):
                    if self.roomxy[y][x]:
                        self.move_room(self.roomxy[y][x], dir)
        return True

    def resize(self, dir):
        """
        Resizes the map, if possible
        """
        if (dir == DIR_E):
            # Limitations in W/H are due to storing these
            # as chars in the savefile.  And also because
            # seriously, what are you doing with a map that big?
            if (self.w == 255):
                return False
            self.w += 1
            for row in self.roomxy:
                row.append(None)
            return True
        elif (dir == DIR_S):
            if (self.h == 255):
                return False
            self.h += 1
            self.roomxy.append([])
            for x in range(self.w):
                self.roomxy[-1].append(None)
            return True
        elif (dir == DIR_W):
            if (self.w == 1):
                return False
            for row in self.roomxy:
                if row[-1]:
                    return False
            self.w -= 1
            for row in self.roomxy:
                row.pop()
            return True
        elif (dir == DIR_N):
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
        Removes the given room from its group
        """
        group = room.group
        to_delete = group.del_room(room)
        if (to_delete):
            for other_room in group.get_rooms():
                group.del_room(other_room)
            self.groups.remove(group)

    def add_room_to_group(self, room_subj, room_to):
        """
        Adds the specified room (room_subj) to a group containing the
        specified other room (room_to).  If room_to does not currently
        belong to a group, a new group is created.  If room_subj is
        already part of a group, it will leave that group first (which
        may result in that group being removed).

        Returns True if we changed anything, or False if room_subj and
        room_to already belonged to the same group
        """
        if (not room_subj.in_group_with(room_to)):
            if (room_subj.group):
                self.remove_room_from_group(room_subj)
            if (room_to.group):
                room_to.group.add_room(room_subj)
            else:
                self.groups.append(Group(room_subj, room_to))
            return True
        else:
            return False

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
            if room:
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
        map = Map(df.readstr())
        map.set_map_size(df.readuchar(), df.readuchar())
        num_rooms = df.readshort()
        num_conns = df.readshort()
        num_groups = df.readshort()

        # Load rooms
        for i in range(num_rooms):
            map.inject_room_obj(Room.load(df, version))

        # Now load connections
        for i in range(num_conns):
            conn = map.connect_id(df.readshort(), df.readuchar(), df.readshort(), df.readuchar())
            conn.type = df.readuchar()
            if version >= 2:
                conn.passage = df.readuchar()
            if version >= 4:
                conn.render = df.readuchar()

        # Now load groups
        for i in range(num_groups):
            map.groups.append(Group.load(df, map, version))

        # ... and return our object.
        return map

class Game(object):
    """
    Data for a single game - Games are actually collections
    of Maps, which are themselves collections of rooms
    """

    def __init__(self, name):
        self.name = name
        self.maps = []

    def add_map_obj(self, map):
        self.maps.append(map)
        return len(self.maps)-1

    def add_map(self, name):
        map = Map(name)
        return (self.add_map_obj(map), map)

    def replace_maps(self, maps):
        """
        Used to replace our current map list.  Mostly here to
        support the GUI reordering.
        """
        self.maps = maps

    def save(self, filename):
        """
        Saves the game maps to a file
        """
        df = Savefile(filename)
        df.open_w()
        df.write('ADVMAP')
        df.writeshort(SAVEFILE_VER)
        df.writestr(self.name)
        df.writeshort(len(self.maps))
        for map in self.maps:
            map.save(df)
        df.close()

    @staticmethod
    def load(filename):
        """
        Loads a game from a savefile
        """
        df = Savefile(filename)
        df.open_r()
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
        df.close()
        return game
