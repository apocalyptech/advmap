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

# TODO:
#   * right now only two-way connections are possible, and
#     connections from one way will always connect to the opposite way
#     ... er, that makes sense to me.
#
#   * The internal storage is a bit dumb, should really fix that.  Having
#     an ID and (x, y) pair which are basically redundant but need to be
#     kept up-to-date with each other is pretty ridiculous.
#  

__all__ = [ 'Room', 'Map', 'Game', 
        'DIR_N', 'DIR_NE', 'DIR_E', 'DIR_SE', 'DIR_S', 'DIR_SW', 'DIR_W', 'DIR_NW',
        'DIR_OPP', 'TXT_2_DIR', 'DIR_2_TXT' ]

DIR_N = 0
DIR_NE = 1
DIR_E = 2
DIR_SE = 3
DIR_S = 4
DIR_SW = 5
DIR_W = 6
DIR_NW = 7

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

SAVEFILE_VER = 1

class Room(object):
    """
    A single room
    """

    # Type constants
    TYPE_NORMAL = 0
    TYPE_ENTRANCE = 1
    TYPE_LABEL = 2

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.name = ''
        self.notes = ''
        self.conns = []
        self.up = ''
        self.down = ''
        self.type = self.TYPE_NORMAL
        self.offset_x = False
        self.offset_y = False
        for dir in DIR_OPP:
            self.conns.append(None)

    def unexplored(self):
        """
        Special-case magic string here.  Yay!
        """
        return (self.name == '(unexplored)')

    def connect(self, dir, room):
        """
        Connects ourself to another room.  Note
        that we expect another Room object here, and
        that any new connection will overwrite any old
        connection
        """
        self.conns[dir] = room

    def detach(self, dir):
        """
        Detaches ourself from a direction.
        """
        self.conns[dir] = None

    def save(self, df):
        """
        Writes ourself to the given filehandle
        """
        connbits = 0
        for dir in range(len(DIR_OPP)):
            connbits = connbits << 1
            if (self.conns[dir]):
                connbits = connbits | 0x1
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
        df.writestr(self.notes)
        df.writeuchar(flagbits)
        df.writeuchar(connbits)
        for dir in range(len(DIR_OPP)):
            if (self.conns[dir]):
                df.writeshort(self.conns[dir].id)

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
        room.notes = df.readstr()
        flagbits = df.readuchar()
        connbits = df.readuchar()
        conns = []
        for dir in range(len(DIR_OPP)):
            haveconn = (connbits >> (7-dir)) & 0x1
            if (haveconn == 1):
                conns.append(df.readshort())
            else:
                conns.append(None)
        if ((flagbits & 0x01) == 0x01):
            room.offset_y = True
        if ((flagbits & 0x02) == 0x02):
            room.offset_x = True
        return (room, conns)

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

    def connect(self, dir, room1, room2):
        """
        Connects two rooms, given the room objects and
        the direction.  Note that it's room1's "dir" which
        will be hooked up to room2's "!dir", so to speak
        """
        room1.connect(dir, room2)
        room2.connect(DIR_OPP[dir], room1)

    def connect_id(self, dir, id1, id2):
        """
        Connects two rooms, given the room IDs
        """
        room1 = self.get_room(id1)
        room2 = self.get_room(id2)
        if (not room1 or not room2):
            raise Exception('Must specify two valid rooms')
        self.connect(dir, room1, room2)

    def detach(self, dir, id1):
        """
        Detaches two rooms
        """
        room1 = self.get_room(id1)
        if (not room1):
            raise Exception('Must specify a valid room')
        room2 = room1.conns[dir]
        if (not room2):
            return
        room1.detach(dir)
        room2.detach(DIR_OPP[dir])

    def del_room(self, room):
        """
        Deletes a room, and removes all former connections to
        that room
        """
        id = room.id
        x = room.x
        y = room.y
        for (dir, conn) in enumerate(room.conns):
            if conn:
                conn.detach(DIR_OPP[dir])
        del self.rooms[id]
        self.roomxy[y][x] = None

    def dir_coord(self, room, dir):
        """
        Returns (x, y) coordinates of the space to the "dir" of the
        given room.  Will return None if that's impossible.
        """
        x = room.x
        y = room.y
        if (dir in [DIR_NW, DIR_W, DIR_SW]):
            if (x == 0):
                return None
            x -= 1
        if (dir in [DIR_NE, DIR_E, DIR_SE]):
            if (x == self.w-1):
                return None
            x += 1
        if (dir in [DIR_NW, DIR_N, DIR_NE]):
            if (y == 0):
                return None
            y -= 1
        if (dir in [DIR_SW, DIR_S, DIR_SE]):
            if (y == self.h-1):
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
            self.w += 1
            for row in self.roomxy:
                row.append(None)
            return True
        elif (dir == DIR_S):
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

    def save(self, df):
        """
        Saves the map to the given filehandle
        """
        df.writestr(self.name)
        df.writeuchar(self.w)
        df.writeuchar(self.h)
        df.writeshort(len(self.rooms))
        for room in self.roomlist():
            if room:
                room.save(df)

    @staticmethod
    def load(df, version):
        """
        Loads a map from the given filehandle
        """
        map = Map(df.readstr())
        map.set_map_size(df.readuchar(), df.readuchar())
        num_rooms = df.readshort()
        connmap = {}
        for i in range(num_rooms):
            (room, conns) = Room.load(df, version)
            connmap[room.id] = conns
            map.inject_room_obj(room)
        # Now connect the rooms that need connecting
        for (roomid, conns) in connmap.items():
            for (dir, conn) in enumerate(conns):
                if conn is not None:
                    map.rooms[roomid].connect(dir, map.rooms[conn])
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
