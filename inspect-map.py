#!/usr/bin/env python2
# vim: set expandtab tabstop=4 shiftwidth=4:

# Duplicated code, etc, just wanted something quick to read
# a map on the console

import sys
from advmap.file import *

print('It looks like this might have been broken for awhile.')
print('Will have to investigate at some point, or alternatively')
print('just remove it from the repo.')
sys.exit(1)

DIR_N = 0
DIR_NE = 1
DIR_E = 2
DIR_SE = 3
DIR_S = 4
DIR_SW = 5
DIR_W = 6
DIR_NW = 7

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

if (len(sys.argv) < 2):
    print('Need a filename')
    sys.exit()

df = Savefile(sys.argv[1])
df.open_r()
read_str = df.read(6)
if (read_str != b'ADVMAP'):
    print('Not a map file')
    sys.exit()

ver = df.readshort()
name = df.readstr()
mapcount = df.readshort()

print('File Version %d' % ver)
print('Game: %s' % name)
print('Map Count: %d' % mapcount)
print('')

for i in range(mapcount):
    mapname = df.readstr()
    w = df.readuchar()
    h = df.readuchar()
    roomcount = df.readshort()
    print('Map %d: %s (%d x %d)' % (i+1, mapname, w, h))
    print('Room Count: %d' % roomcount)
    print('')

    for j in range(roomcount):
        id = df.readshort()
        x = df.readuchar()
        y = df.readuchar()
        roomname = df.readstr()
        type = df.readuchar()
        up = df.readstr()
        down = df.readstr()
        notes = df.readstr()
        print('  Room ID %d: %s at (%d, %d)' % (id, roomname, x, y))

        conns = df.readuchar()
        for dir in range(8):
            haveconn = (conns >> (7-dir)) & 0x1
            if (haveconn == 1):
                print('     Connection to %s: %d' % (DIR_2_TXT[dir], df.readshort()))
        print('')

df.close()
