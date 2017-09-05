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
    connhelper_corner_length = room_size_half*.2

    # Various room text spacing constants.  Some of these actually rely on
    # values we get from querying QFont and QFontMetrics data directly,
    # which will segfault the app if there's not a full Qt environment up
    # and running, so we can't do it here.  These will get populated when
    # our main GUI class is initializing.

    # Border around the room where we theoretically want to not have text
    # (also the space we'll try to keep between lines of text)
    room_text_padding = 6

    # Blank padding which our QGraphicsTextItem objects will report on each
    # side of the actual text dimensions contained within.  Will be a dict with
    # the key corresponding to the font size in use.
    title_font_sizes = [10, 9, 8, 7, 6]
    title_padding_x = {}
    title_padding_y = {}

    # Similar to the blank padding for title, but for notes.
    notes_font_sizes = [10, 9, 8, 7, 6]
    notes_padding_x = {}
    notes_padding_y = {}

    # Similar to the others, for our in/out/up/down labels.  A dict because the
    # size can vary.
    other_font_sizes = [8, 7, 6]
    other_padding_x = {}
    other_padding_y = {}

    # Y position where we'll always draw the notes field, if it exists
    notes_start_y = None

    # Parameters for fitting the room title
    title_max_width = room_size - (room_text_padding*2)
    title_max_height = None

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

        # Set up some constants which we can't do directly in Constants
        # because of Reasons.  First up: title font padding
        for font_size in Constants.title_font_sizes:
            f = GUIRoom.get_title_font(font_size)
            m = QtGui.QFontMetrics(f)
            m_rect = m.boundingRect('Title')
            t = QtWidgets.QGraphicsTextItem('Title')
            t.setFont(f)
            t_rect = t.boundingRect()
            Constants.title_padding_x[font_size] = (t_rect.width() - m_rect.width()) / 2
            Constants.title_padding_y[font_size] = (t_rect.height() - m_rect.height()) / 2
        # Next up: the exact same thing but for our "other" labels
        for font_size in Constants.other_font_sizes:
            f = GUIRoom.get_other_font(font_size)
            m = QtGui.QFontMetrics(f)
            m_rect = m.boundingRect('Other')
            t = QtWidgets.QGraphicsTextItem('Other')
            t.setFont(f)
            t_rect = t.boundingRect()
            Constants.other_padding_x[font_size] = (t_rect.width() - m_rect.width()) / 2
            Constants.other_padding_y[font_size] = (t_rect.height() - m_rect.height()) / 2
        # and finally (for this kind of calculation, anyway, for notes.
        for font_size in Constants.notes_font_sizes:
            f = GUIRoom.get_notes_font(font_size)
            m = QtGui.QFontMetrics(f)
            m_rect = m.boundingRect('Notes')
            t = QtWidgets.QGraphicsTextItem('Notes')
            t.setFont(f)
            t_rect = t.boundingRect()
            Constants.notes_padding_x[font_size] = (t_rect.width() - m_rect.width()) / 2
            Constants.notes_padding_y[font_size] = (t_rect.height() - m_rect.height()) / 2
        Constants.notes_start_y = Constants.room_size_half - m_rect.height() - Constants.notes_padding_y[Constants.notes_font_sizes[0]]
        Constants.title_max_height = Constants.room_size_half - (Constants.room_text_padding*1) - m_rect.height()

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

    def __init__(self, gui_room):
        super().__init__(gui_room)
        self.gui_room = gui_room
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsFocusable)
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.setRect(0, 0, Constants.room_size, Constants.room_size)
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

class GUIRoomTitleAsNotesTextItem(QtWidgets.QGraphicsTextItem):
    """
    A text field used for showing "full" room names, for Label type rooms
    """

    def __init__(self, parent):
        super().__init__(parent.room.name, parent)

        max_width = Constants.room_size - (Constants.room_text_padding*2)
        max_height = Constants.room_size - (Constants.room_text_padding*2)
        self.setDefaultTextColor(parent.color_text)
        self.setTextWidth(max_width)
        doc = self.document()
        options = doc.defaultTextOption()
        options.setAlignment(QtCore.Qt.AlignHCenter)
        options.setWrapMode(options.WordWrap)
        doc.setDefaultTextOption(options)

        for font_size in Constants.notes_font_sizes:
            self.setFont(GUIRoom.get_notes_font(font_size))
            rect = self.boundingRect()
            if (rect.width() > max_width or rect.height() > max_height):
                continue
            else:
                break

        # Update our position automatically.
        self.setPos(
                Constants.room_text_padding,
                Constants.room_size_half - (rect.height()/2),
            )

class GUIRoomNotesTextItem(QtWidgets.QGraphicsTextItem):
    """
    A text field used for showing room notes
    """

    def __init__(self, parent):
        if len(parent.room.notes) > 15:
            note_str = '%s...' % (parent.room.notes[:12])
        else:
            note_str = parent.room.notes
        super().__init__(note_str, parent)
        self.setFont(GUIRoom.get_notes_font(9))
        self.setDefaultTextColor(parent.color_text)
        doc = self.document()
        options = doc.defaultTextOption()
        options.setWrapMode(options.NoWrap)
        doc.setDefaultTextOption(options)

        # Update our position automatically.
        rect = self.boundingRect()
        self.setPos(
                Constants.room_size_half - (rect.width()/2) + 1,
                Constants.notes_start_y,
            )

class GUIRoomTitleTextItem(QtWidgets.QGraphicsTextItem):
    """
    A text field used for showing room title
    """

    def __init__(self, parent):

        super().__init__(parent.room.name, parent)

        # TODO: The default Qt line spacing is a bit too big for my tastes;
        # the Gtk formatting was noticeably more compact.  It looks like this
        # is actually super difficult to accomplish in Qt.  (Stylesheets don't
        # help, unfortunately; the line-height attribute isn't supported.)
        # My only real idea is that I think the Document can give you the text
        # on a per-line basis, and we could manually add multiple items for
        # each line, setting the distance ourselves.  I don't actually care
        # that much yet, though.
        self.setTextWidth(Constants.title_max_width)
        self.setDefaultTextColor(parent.color_text)
        doc = self.document()
        options = doc.defaultTextOption()
        options.setAlignment(QtCore.Qt.AlignHCenter)
        options.setWrapMode(options.WordWrap)
        doc.setDefaultTextOption(options)

        # Loop through font sizes, trying to find one which fits
        for font_size in Constants.title_font_sizes:
            self.setFont(GUIRoom.get_title_font(font_size))
            rect = self.boundingRect()
            if (rect.width() > (Constants.title_max_width + (Constants.title_padding_x[font_size]*2)) or
                    rect.height() > (Constants.title_max_height + (Constants.title_padding_y[font_size]*2))):
                continue
            else:
                break

        # Set our position
        self.setPos(
                Constants.room_text_padding,
                Constants.room_text_padding - Constants.title_padding_y[font_size],
            )

class GUIRoom(QtWidgets.QGraphicsRectItem):

    def __init__(self, parent, room):
        super().__init__()
        self.room = room
        self.set_position()
        self.setZValue(Constants.z_value_room)

        # Set up the colors we'll use
        self.color_border = Constants.c_type_map[self.room.type][self.room.color][0]
        self.color_bg = Constants.c_type_map[self.room.type][self.room.color][1]
        self.color_text = Constants.c_type_map[self.room.type][self.room.color][2]

        # Rooms with a name of "(unexplored)" become labels, effectively.
        # So that's what we're doing here.
        if (room.type != Room.TYPE_CONNHELPER and
                (room.type == Room.TYPE_LABEL or room.unexplored())):
            pretend_label = True
        else:
            pretend_label = (room.type == Room.TYPE_LABEL)

        self.notes = None
        self.title = None
        if pretend_label:

            # If we're a label, only show our name, using the notes style
            self.notes = GUIRoomTitleAsNotesTextItem(self)

        else:

            # Show our notes, if we need to
            if self.room.notes and self.room.notes != '':
                self.notes = GUIRoomNotesTextItem(self)

            # Show our title
            if room.type != Room.TYPE_CONNHELPER:
                self.title = GUIRoomTitleTextItem(self)

        # Set our background/border coloration
        # TODO: be sure to draw connhelper background if we're selected
        if room.type == Room.TYPE_CONNHELPER:
            self.setBrush(QtGui.QBrush(Constants.c_transparent))
            self.setPen(QtGui.QPen(Constants.c_transparent))
            for (x1, y1, x2, y2) in [
                    # NW corner
                    (0, 0, Constants.connhelper_corner_length, 0),
                    (0, 0, 0, Constants.connhelper_corner_length),
                    # NE corner
                    (Constants.room_size, 0, Constants.room_size-Constants.connhelper_corner_length, 0),
                    (Constants.room_size, 0, Constants.room_size, Constants.connhelper_corner_length),
                    # SW corner
                    (0, Constants.room_size, Constants.connhelper_corner_length, Constants.room_size),
                    (0, Constants.room_size, 0, Constants.room_size-Constants.connhelper_corner_length),
                    # SE corner
                    (Constants.room_size, Constants.room_size, Constants.room_size-Constants.connhelper_corner_length, Constants.room_size),
                    (Constants.room_size, Constants.room_size, Constants.room_size, Constants.room_size-Constants.connhelper_corner_length),
                    ]:
                line = QtWidgets.QGraphicsLineItem(x1, y1, x2, y2, self)
                line.setPen(QtGui.QPen(self.color_border))
        else:
            self.setBrush(QtGui.QBrush(self.color_bg))
            pen = QtGui.QPen(self.color_border)
            if pretend_label:
                pen.setDashPattern([9, 9])
            self.setPen(pen)
        
        # Also add a Hover object for ourselves
        self.hover_obj = GUIRoomHover(self)

    @staticmethod
    def get_title_font(size=Constants.title_font_sizes[0]):
        """
        Returns a QFont for the title, of the specified size
        """
        f = QtGui.QFont()
        f.setBold(True)
        f.setPointSize(size)
        return f

    @staticmethod
    def get_notes_font(size=Constants.notes_font_sizes[0]):
        """
        Returns a QFont for our notes text, of the specified size
        """
        f = QtGui.QFont()
        f.setItalic(True)
        f.setPointSize(size)
        return f

    @staticmethod
    def get_other_font(size=Constants.other_font_sizes[0]):
        """
        Returns a QFont for our "other" text, of the specified size
        """
        f = QtGui.QFont()
        f.setPointSize(size)
        return f

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
