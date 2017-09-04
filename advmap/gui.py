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
    room_space = 30
    room_space_half = room_space/2

    # Z-values we'll use in the scene - layers, effectively.  This makes
    # sure that our hovers are prioritized the way we want them to, and also
    # makes connection+room rendering show up in a consistent way.
    (z_value_background,
        z_value_group,
        z_value_connection,
        z_value_room,
        z_value_room_hover,
        z_value_connection_hover,
        z_value_edge_hover,
        ) = range(7)

    # Initialize a bunch of Colors that we'll use
    c_background = QtGui.QColor(255, 255, 255, 255)
    c_borders = QtGui.QColor(0, 0, 0, 255)
    c_label = QtGui.QColor(178, 178, 178, 255)
    c_highlight = QtGui.QColor(127, 255, 127, 51)
    c_highlight_nudge = QtGui.QColor(178, 178, 178, 51)
    c_highlight_del = QtGui.QColor(255, 127, 127, 51)
    c_highlight_new = QtGui.QColor(127, 127, 255, 51)
    c_grid = QtGui.QColor(229, 229, 229, 255)
    c_transparent = QtGui.QColor(0, 0, 0, 0)

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

class GUIRoomHover(QtWidgets.QGraphicsRectItem):

    def __init__(self, parent, gui_room):
        super().__init__()
        self.gui_room = gui_room
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsFocusable)
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.setRect(0, 0, Constants.room_size, Constants.room_size)
        self.setPos(gui_room.gfx_x, gui_room.gfx_y)
        self.setZValue(Constants.z_value_room_hover)

    def hoverEnterEvent(self, event):
        """
        We've entered hovering
        """
        self.setBrush(QtGui.QBrush(Constants.c_highlight))
        self.setPen(QtGui.QPen(Constants.c_highlight))
        self.setFocus()

    def hoverLeaveEvent(self, event):
        """
        We've entered hovering
        """
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.clearFocus()

    def keyPressEvent(self, event):
        """
        Keyboard input
        """
        print('{}: Received {}'.format(self.gui_room.room.name, event.text()))

class GUIRoom(QtWidgets.QGraphicsRectItem):

    def __init__(self, parent, room):
        super().__init__()
        self.room = room
        self.set_position()
        self.setZValue(Constants.z_value_room)

        self.color_border = Constants.c_type_map[self.room.type][self.room.color][0]
        self.color_bg = Constants.c_type_map[self.room.type][self.room.color][1]
        self.color_text = Constants.c_type_map[self.room.type][self.room.color][2]

        # Show our notes, or at least set up a pretend note var so that we know
        # what height to constrain our title
        notes_font = QtGui.QFont()
        notes_font.setItalic(True)
        notes_metrics = QtGui.QFontMetrics(notes_font)
        if self.room.notes is None or self.room.notes == '':
            metrics_rect = notes_metrics.boundingRect('(notes)')
            self.notes = None
        else:
            if len(self.room.notes) > 15:
                note_str = '%s...' % (self.room.notes[:12])
            else:
                note_str = self.room.notes
            metrics_rect = notes_metrics.boundingRect(note_str)
            self.notes = QtWidgets.QGraphicsTextItem(note_str)
            self.notes.setFont(notes_font)
            self.notes.setTextWidth(Constants.room_size)
            doc = self.notes.document()
            options = doc.defaultTextOption()
            options.setAlignment(QtCore.Qt.AlignHCenter)
            options.setWrapMode(options.NoWrap)
            doc.setDefaultTextOption(options)
            notes_rect = self.notes.boundingRect()
            # TODO: For centering, there's two ways to do it.
            #   Way 1: setTextWidth+setAlignment+using a number below.  But for long notes, using -1 looks better than 0
            #   Way 2: do the commented out calc instead.  But for long notes, using +1 looks better than without.
            # ... why?
            self.notes.setPos(
                #Constants.room_size_half - (notes_rect.width()/2) + 1,
                -1,
                Constants.room_size_half - notes_rect.height() + ((notes_rect.height()-metrics_rect.height())/2)
                )
            self.notes.setParentItem(self)

        # How tall our title is allowed to be is dependent, currently, on how tall
        # Notes are (whether they're shown or not)
        title_max_height = Constants.room_size_half - Constants.room_space_half - metrics_rect.height()

        # Show our title
        self.title = QtWidgets.QGraphicsTextItem(self.room.name, self)
        self.title.setTextWidth(Constants.room_size-Constants.room_space_half)
        doc = self.title.document()
        options = doc.defaultTextOption()
        options.setAlignment(QtCore.Qt.AlignHCenter)
        doc.setDefaultTextOption(options)
        font = QtGui.QFont()
        font.setWeight(font.Bold)
        self.title.setFont(font)
        #print(self.title.boundingRect().height())
        self.title.setPos(Constants.room_space_half/2, Constants.room_space_half/8)

        # Set our coloration
        self.setBrush(QtGui.QBrush(self.color_bg))
        self.setPen(QtGui.QPen(self.color_border))
        if self.color_text:
            self.title.setDefaultTextColor(self.color_text)
            if self.notes:
                self.notes.setDefaultTextColor(self.color_text)
        
        # Also add a Hover object for ourselves
        self.hover_obj = GUIRoomHover(parent, self)


    def set_position(self):
        """
        Sets our position within the scene, based on our room coords
        """
        self.gfx_x = Constants.room_space_half + (Constants.room_size+Constants.room_space)*self.room.x
        self.gfx_y = Constants.room_space_half + (Constants.room_size+Constants.room_space)*self.room.y
        if self.room.offset_x:
            self.gfx_x += Constants.room_size_half + Constants.room_space_half
        if self.room.offset_y:
            self.gfx_y += Constants.room_size_half + Constants.room_space_half
        self.setRect(0, 0, Constants.room_size, Constants.room_size)
        self.setPos(self.gfx_x, self.gfx_y)

class MapScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent):

        super().__init__(parent)

        self.mapobj = None
        self.set_dimensions(1, 1)

    def set_dimensions(self, w, h):
        """
        Sets our dimensions in terms of rooms
        """
        total_w = (Constants.room_space + Constants.room_size)*w
        total_h = (Constants.room_space + Constants.room_size)*h
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
            self.addItem(guiroom.hover_obj)

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
