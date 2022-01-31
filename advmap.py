#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:
#
# Adventure Game Mapper
# Copyright (C) 2010-2022 CJ Kucera
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

import sys
import argparse
from advmap.gui import Application

# Argument Definitions
parser = argparse.ArgumentParser(description='Adventure Game Mapper')
parser.add_argument('-r', '--readonly',
        action='store_true',
        help='Start the editor in readonly mode')
parser.add_argument('filename',
        type=str,
        nargs='?',
        metavar='filename',
        help='Filename to load (will start with a new map, otherwise)')

# Parse arguments
args = parser.parse_args()

# Run the GUI
gui = Application(args.filename, args.readonly)
sys.exit(gui.exec_())
