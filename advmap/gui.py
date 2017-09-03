#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:
#
# Adventure Game Mapper
# Copyright (C) 2010-2017 CJ Kucera
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

import os.path
import math
from PyQt5 import QtWidgets, QtGui, QtCore

from advmap.data import *

def overlay_color(source, overlay):
    """
    Merges two QColors.  The Alpha value of the new QColor will be the
    Alpha from `source`.  The Alpha value of `overlay` will determine how
    much of the color to multiply in.
    """
    ratio_overlay = overlay.alphaF()
    return QtGui.QColor(
            source.red()*(1-ratio_overlay)+overlay.red()*ratio_overlay,
            source.green()*(1-ratio_overlay)+overlay.green()*ratio_overlay,
            source.blue()*(1-ratio_overlay)+overlay.blue()*ratio_overlay,
            source.alpha(),
        )

class Constants(object):
    """
    Basically just a container for a bunch of static vars used by a number
    of classes
    """

    # Geometry of our rooms, etc
    room_size = 110
    room_size_half = room_size/2
    room_space_half = 30
    room_space_half = room_space_half/2

    # Initialize a bunch of Colors that we'll use
    c_background = QtGui.QColor(255, 255, 255, 255)
    c_borders = QtGui.QColor(0, 0, 0, 255)
    c_label = QtGui.QColor(178, 178, 178, 255)
    c_highlight = QtGui.QColor(127, 255, 127, 51)
    c_highlight_nudge = QtGui.QColor(178, 178, 178, 51)
    c_highlight_del = QtGui.QColor(255, 127, 127, 51)
    c_highlight_new = QtGui.QColor(127, 127, 255, 51)
    c_grid = QtGui.QColor(229, 229, 229, 255)

    c_group_map = {
            Group.STYLE_NORMAL: QtGui.QColor(216, 216, 216, 255),
            Group.STYLE_RED: QtGui.QColor(242, 216, 216, 255),
            Group.STYLE_GREEN: QtGui.QColor(216, 242, 216, 255),
            Group.STYLE_BLUE: QtGui.QColor(216, 216, 242, 255),
            Group.STYLE_YELLOW: QtGui.QColor(242, 242, 216, 255),
            Group.STYLE_PURPLE: QtGui.QColor(242, 216, 242, 255),
            Group.STYLE_CYAN: QtGui.QColor(216, 242, 242, 255),
            Group.STYLE_FAINT: QtGui.QColor(242, 242, 242, 255),
            Group.STYLE_DARK: QtGui.QColor(165, 165, 165, 255),
        }
    c_group_default = c_group_map[Group.STYLE_NORMAL]

    # Entries here are tuples with the following:
    #   1) Foreground color for borderse
    #   2) Background color for fill
    #   3) Foreground color for text
    c_default_text = QtGui.QColor(0, 0, 0, 255)
    c_default_text_faint = QtGui.QColor(102, 102, 102, 255)
    c_default_text_dark = QtGui.QColor(229, 229, 229, 255)
    c_type_map = {
            Room.TYPE_NORMAL: {
                    Room.COLOR_BW: (c_borders, QtGui.QColor(249, 249, 249, 255), c_default_text),
                    Room.COLOR_RED: (QtGui.QColor(127, 0, 0, 255), QtGui.QColor(255, 249, 249, 255), c_default_text),
                    Room.COLOR_GREEN: (QtGui.QColor(0, 127, 0, 255), QtGui.QColor(249, 255, 249, 255), c_default_text),
                    Room.COLOR_BLUE: (QtGui.QColor(0, 0, 127, 255), QtGui.QColor(249, 249, 255, 255), c_default_text),
                    Room.COLOR_YELLOW: (QtGui.QColor(127, 127, 0, 255), QtGui.QColor(255, 255, 249, 255), c_default_text),
                    Room.COLOR_PURPLE: (QtGui.QColor(127, 0, 127, 255), QtGui.QColor(255, 249, 255, 255), c_default_text),
                    Room.COLOR_CYAN: (QtGui.QColor(0, 127, 127, 255), QtGui.QColor(249, 255, 255, 255), c_default_text),
                    Room.COLOR_ORANGE: (QtGui.QColor(178, 89, 0, 255), QtGui.QColor(249, 252, 255, 255), c_default_text),
                },
            Room.TYPE_LABEL: {
                    Room.COLOR_BW: (c_borders, QtGui.QColor(249, 249, 249, 255), c_default_text),
                    Room.COLOR_RED: (QtGui.QColor(127, 0, 0, 255), QtGui.QColor(255, 249, 249, 255), c_default_text),
                    Room.COLOR_GREEN: (QtGui.QColor(0, 127, 0, 255), QtGui.QColor(249, 255, 249, 255), c_default_text),
                    Room.COLOR_BLUE: (QtGui.QColor(0, 0, 127, 255), QtGui.QColor(249, 249, 255, 255), c_default_text),
                    Room.COLOR_YELLOW: (QtGui.QColor(127, 127, 0, 255), QtGui.QColor(255, 255, 249, 255), c_default_text),
                    Room.COLOR_PURPLE: (QtGui.QColor(127, 0, 127, 255), QtGui.QColor(255, 249, 255, 255), c_default_text),
                    Room.COLOR_CYAN: (QtGui.QColor(0, 127, 127, 255), QtGui.QColor(249, 255, 255, 255), c_default_text),
                    Room.COLOR_ORANGE: (QtGui.QColor(178, 89, 0, 255), QtGui.QColor(249, 255, 255, 255), c_default_text),
                },
            Room.TYPE_FAINT: {
                    Room.COLOR_BW: (QtGui.QColor(153, 153, 153, 255), QtGui.QColor(255, 255, 255, 255), c_default_text_faint),
                    Room.COLOR_RED: (QtGui.QColor(204, 153, 153, 255), QtGui.QColor(255, 255, 255, 255), c_default_text_faint),
                    Room.COLOR_GREEN: (QtGui.QColor(153, 204, 153, 255), QtGui.QColor(255, 255, 255, 255), c_default_text_faint),
                    Room.COLOR_BLUE: (QtGui.QColor(153, 153, 204, 255), QtGui.QColor(255, 255, 255, 255), c_default_text_faint),
                    Room.COLOR_YELLOW: (QtGui.QColor(204, 204, 153, 255), QtGui.QColor(255, 255, 255, 255), c_default_text_faint),
                    Room.COLOR_PURPLE: (QtGui.QColor(204, 153, 204, 255), QtGui.QColor(255, 255, 255, 255), c_default_text_faint),
                    Room.COLOR_CYAN: (QtGui.QColor(153, 204, 204, 255), QtGui.QColor(255, 255, 255, 255), c_default_text_faint),
                    Room.COLOR_ORANGE: (QtGui.QColor(204, 178, 153, 255), QtGui.QColor(255, 255, 255, 255), c_default_text_faint),
                },
            Room.TYPE_DARK: {
                    Room.COLOR_BW: (QtGui.QColor(0, 0, 0, 255), QtGui.QColor(89, 89, 89, 255), c_default_text_dark),
                    Room.COLOR_RED: (QtGui.QColor(127, 0, 0, 255), QtGui.QColor(89, 51, 51, 255), c_default_text_dark),
                    Room.COLOR_GREEN: (QtGui.QColor(0, 127, 0, 255), QtGui.QColor(51, 89, 51, 255), c_default_text_dark),
                    Room.COLOR_BLUE: (QtGui.QColor(0, 0, 127, 255), QtGui.QColor(51, 51, 89, 255), c_default_text_dark),
                    Room.COLOR_YELLOW: (QtGui.QColor(127, 127, 0, 255), QtGui.QColor(89, 89, 51, 255), c_default_text_dark),
                    Room.COLOR_PURPLE: (QtGui.QColor(127, 0, 127, 255), QtGui.QColor(89, 51, 89, 255), c_default_text_dark),
                    Room.COLOR_CYAN: (QtGui.QColor(0, 127, 127, 255), QtGui.QColor(51, 89, 89, 255), c_default_text_dark),
                    Room.COLOR_ORANGE: (QtGui.QColor(127, 63, 0, 255), QtGui.QColor(89, 68, 51, 255), c_default_text_dark),
                },
            Room.TYPE_CONNHELPER: {
                    # Background for connhelper is only used if the room is selected.  Text color
                    # is never used.
                    Room.COLOR_BW: (QtGui.QColor(153, 153, 153, 255), QtGui.QColor(249, 249, 249, 255), None),
                    Room.COLOR_RED: (QtGui.QColor(204, 153, 153, 255), QtGui.QColor(255, 249, 249, 255), None),
                    Room.COLOR_GREEN: (QtGui.QColor(153, 204, 153, 255), QtGui.QColor(249, 255, 249, 255), None),
                    Room.COLOR_BLUE: (QtGui.QColor(153, 153, 204, 255), QtGui.QColor(249, 249, 255, 255), None),
                    Room.COLOR_YELLOW: (QtGui.QColor(204, 204, 153, 255), QtGui.QColor(255, 255, 249, 255), None),
                    Room.COLOR_PURPLE: (QtGui.QColor(204, 153, 204, 255), QtGui.QColor(255, 249, 255, 255), None),
                    Room.COLOR_CYAN: (QtGui.QColor(153, 204, 204, 255), QtGui.QColor(249, 255, 255, 255), None),
                    Room.COLOR_ORANGE: (QtGui.QColor(204, 178, 153, 255), QtGui.QColor(249, 252, 255, 255), None),
                },
        }

class GUI(QtWidgets.QMainWindow):
    """
    Main application window.
    """

    def __init__(self, initfile, readonly):
        super().__init__()
        self.initUI(initfile, readonly)

    def initUI(self, initfile, readonly):

        # Set up a stats bar
        self.statusbar = self.statusBar()


        # Load the specified game, or create a blank map
        self.curfile = None
        if initfile:
            try:
                self.load_from_file(initfile)
            except Exception as e:
                print(e)
        if not self.curfile:
            self.create_new_game()

        self.maparea = MapArea(self)
        self.scene = self.maparea.scene
        self.setCentralWidget(self.maparea)

        self.maparea.statusbar[str].connect(self.statusbar.showMessage)

        self.resize(1000, 700)
        self.setWindowTitle('Adventure Game Mapper')
        self.show()

        self.scene.set_map(self.mapobj)

    def set_status(self, status_str):
        """
        Sets our status
        """
        self.statusbar.showMessage(status_str)

    def load_from_file(self, filename):
        """
        Loads a game from a file.  Note that we always return
        true; if loading failed, the load() method should raise an
        exception, which should be caught by anything attempting
        the load.
        """
        game = Game.load(filename)
        self.game = game
        self.mapobj = self.game.maps[0]
        self.map_idx = 0
        self.curfile = filename
        self.set_status('Editing %s' % filename)
        return True

    def create_new_game(self):
        """
        Starts a new Game file from scratch.
        """
        self.curfile = None
        self.game = Game('New Game')
        self.mapobj = self.create_new_map('Starting Map')
        self.map_idx = self.game.add_map_obj(self.mapobj)
        self.set_status('Editing a new game')

    def create_new_map(self, name):
        """
        Creates our default new map, with a single room in the center
        """
        mapobj = Map(name)
        room = mapobj.add_room_at(4, 4, 'Starting Room')
        room.color = Room.COLOR_GREEN
        return mapobj

class GUIRoom(QtWidgets.QGraphicsRectItem):

    def __init__(self, parent, room):
        super().__init__()
        self.room = room
        self.set_position()
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsFocusable)

        self.color_border = Constants.c_type_map[self.room.type][self.room.color][0]
        self.color_bg = Constants.c_type_map[self.room.type][self.room.color][1]
        self.color_text = Constants.c_type_map[self.room.type][self.room.color][2]

        self.title = QtWidgets.QGraphicsTextItem(self.room.name, self)
        self.title.setTextWidth(Constants.room_size-Constants.room_space_half)
        doc = self.title.document()
        options = doc.defaultTextOption()
        options.setAlignment(QtCore.Qt.AlignHCenter)
        doc.setDefaultTextOption(options)
        font = QtGui.QFont()
        font.setWeight(font.Bold)
        self.title.setFont(font)
        print(self.title.boundingRect().height())

        self.title.setPos(Constants.room_space_half/2, Constants.room_space_half/4)

        self.set_hover_vars(False)
    
    def set_hover_vars(self, hovered):
        """
        Sets vars which change depending on if we're hovered or not
        """
        if hovered:
            self.setBrush(QtGui.QBrush(overlay_color(self.color_bg, Constants.c_highlight)))
            self.setPen(QtGui.QPen(overlay_color(self.color_border, Constants.c_highlight)))
            if self.color_text:
                self.title.setDefaultTextColor(overlay_color(self.color_text, Constants.c_highlight))
        else:
            self.setBrush(QtGui.QBrush(self.color_bg))
            self.setPen(QtGui.QPen(self.color_border))
            if self.color_text:
                self.title.setDefaultTextColor(self.color_text)

    def set_position(self):
        """
        Sets our position within the scene, based on our room coords
        """
        gfx_x = Constants.room_space_half + (Constants.room_size+Constants.room_space_half)*self.room.x
        gfx_y = Constants.room_space_half + (Constants.room_size+Constants.room_space_half)*self.room.y
        if self.room.offset_x:
            gfx_x += Constants.room_size_half + Constants.room_space_half
        if self.room.offset_y:
            gfx_y += Constants.room_size_half + Constants.room_space_half
        self.setRect(0, 0, Constants.room_size, Constants.room_size)
        self.setPos(gfx_x, gfx_y)

    def hoverEnterEvent(self, event):
        """
        We've entered hovering
        """
        self.set_hover_vars(True)
        self.setFocus()

    def hoverLeaveEvent(self, event):
        """
        We've entered hovering
        """
        self.set_hover_vars(False)
        self.clearFocus()

    def keyPressEvent(self, event):
        """
        Keyboard input
        """
        print('{}: Received {}'.format(self.room.name, event.text()))

class MapScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent):

        super().__init__(parent)

        self.mapobj = None
        self.set_dimensions(1, 1)

    def set_dimensions(self, w, h):
        """
        Sets our dimensions in terms of rooms
        """
        total_w = (Constants.room_space_half + Constants.room_size)*w
        total_h = (Constants.room_space_half + Constants.room_size)*h
        self.setSceneRect(QtCore.QRectF(0, 0, total_w, total_h))

    def set_map(self, mapobj):
        """
        Sets the current map in use
        """
        self.mapobj = mapobj
        self.set_dimensions(self.mapobj.w, self.mapobj.h)
        for room in mapobj.rooms.values():
            guiroom = GUIRoom(self, room)
            self.addItem(guiroom)

class MapArea(QtWidgets.QGraphicsView):

    statusbar = QtCore.pyqtSignal(str)

    def __init__(self, parent):

        super().__init__(parent)
        self.scene = MapScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

class Application(QtWidgets.QApplication):
    """
    Our main application
    """

    def __init__(self, initfile=None, readonly=False):
        """
        Initialization
        """
        
        super().__init__([])
        self.app = GUI(initfile=initfile, readonly=readonly)
