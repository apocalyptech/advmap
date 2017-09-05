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

    # Border around the room where we theoretically want to not have text
    room_text_padding = 6

    # Vars for our in/out/up/down labels
    icon_start_y = room_size_half + 6
    icon_label_space = 3
    icon_space_between = 4

    # Various room text spacing constants.  Some of these actually rely on
    # values we get from querying QFont and QFontMetrics data directly,
    # which will segfault the app if there's not a full Qt environment up
    # and running, so we can't do it here.  These will get populated when
    # our main GUI class is initializing.

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
    default_note_size = 9

    # Similar to the others, for our in/out/up/down labels.  A dict because the
    # size can vary.
    other_font_sizes = [8, 7, 6]
    other_padding_x = {}
    other_padding_y = {}
    other_max_width = None

    # Y position where we'll always draw the notes field, if it exists
    notes_start_y = None

    # Parameters for fitting the room title
    title_max_width = room_size - (room_text_padding*2)
    title_max_height = None

    # Images.  As with some of the font stuff above, we need a QApplication first,
    # so these will be loaded in later
    gfx_room_in = None
    gfx_room_out = None
    gfx_ladder_up = None
    gfx_ladder_down = None
    gfx_room_in_rev = None
    gfx_room_out_rev = None
    gfx_ladder_up_rev = None
    gfx_ladder_down_rev = None
    gfx_icon_width = None

    # Z-values we'll use in the scene - layers, effectively.  This makes
    # sure that our hovers are prioritized the way we want them to, and also
    # makes connection+room rendering show up in a consistent way.
    (z_value_background,
        z_value_group,
        z_value_new_room,
        z_value_connection,
        z_value_new_room_hover,
        z_value_room,
        z_value_room_hover,
        z_value_connection_hover,
        z_value_edge_hover,
        ) = range(9)

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

    # Some convenience objects which will get populated as the GUI
    # gets built.  This is stretching the definition of "Constant"
    # pretty terribly, but I do not feel bad about this.
    statusbar = None

class MainStatusBar(QtWidgets.QStatusBar):
    """
    Main status bar for our app.  Basically we're adding in a QVBoxLayout which
    includes both a QLabel and a QStatusBar, and passing through statusbar-related
    functions to the inner status bar
    """

    def __init__(self, parent):

        super().__init__(parent)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setSpacing(0)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.hover_label = QtWidgets.QLabel(self)
        self.hover_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.inner_sb = QtWidgets.QStatusBar(self)
        self.secondary_hover = QtWidgets.QLabel(self)
        self.inner_sb.addPermanentWidget(self.secondary_hover)
        # TODO: I would like to figure out a way to remove the padding around the
        # QStatusBar but have been unable to do so.  Couldn't find CSS that worked,
        # either.
        #self.inner_sb.setContentsMargins(0, 0, 0, 0)
        #self.inner_sb.layout().setContentsMargins(0, 0, 0, 0)
        self.vbox.addWidget(self.hover_label)
        self.vbox.addWidget(self.inner_sb)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.vbox)
        self.addWidget(self.widget, 1)

        # Setting size policy; this generally didn't seem to actually do anything
        # while I was playing with spacing here, keeping it commented just for
        # reference, though.
        #self.widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

    def currentMessage(self):
        """
        Returns our current message on the inner status bar
        """
        return self.inner_sb.currentMessage()

    def showMessage(self, message, timeout=0):
        """
        Shows the given message on our inner statusbar
        """
        return self.inner_sb.showMessage(message, timeout)

    def set_hover_actions(self, actions=None, prefix=None):
        """
        Displays a list of actions on our hover_label
        """
        hover_text = ''
        if not actions:
            actions = []
        if len(actions) == 0:
            if prefix:
                hover_text = prefix
        else:
            hover_text = ', '.join(['%s: %s' % (key, action) for (key, action) in actions])
            if prefix is not None:
                hover_text = '%s - %s' % (prefix, hover_text)
        self.hover_label.setText(hover_text)

class GUI(QtWidgets.QMainWindow):
    """
    Main application window.
    """

    def __init__(self, initfile, readonly):
        super().__init__()
        self.initUI(initfile, readonly)

    def initUI(self, initfile, readonly):

        # Set up a status bar
        self.statusbar = MainStatusBar(self)
        self.setStatusBar(self.statusbar)
        Constants.statusbar = self.statusbar

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
        Constants.notes_start_y = Constants.room_size_half - m_rect.height() - Constants.notes_padding_y[Constants.default_note_size]*2
        Constants.title_max_height = Constants.room_size_half - (Constants.room_text_padding*1) - m_rect.height()

        # Load in some external images; currently all assumed to be the same width
        Constants.gfx_door_in = QtGui.QPixmap(self.resfile('door_in.png'))
        Constants.gfx_door_out = QtGui.QPixmap(self.resfile('door_out.png'))
        Constants.gfx_ladder_up = QtGui.QPixmap(self.resfile('ladder_up.png'))
        Constants.gfx_ladder_down = QtGui.QPixmap(self.resfile('ladder_down.png'))
        Constants.gfx_door_in_rev = QtGui.QPixmap(self.resfile('door_in_rev.png'))
        Constants.gfx_door_out_rev = QtGui.QPixmap(self.resfile('door_out_rev.png'))
        Constants.gfx_ladder_up_rev = QtGui.QPixmap(self.resfile('ladder_up_rev.png'))
        Constants.gfx_ladder_down_rev = QtGui.QPixmap(self.resfile('ladder_down_rev.png'))
        Constants.gfx_icon_width = Constants.gfx_door_in.width()
        Constants.other_max_width = Constants.room_size - Constants.room_text_padding*2 - Constants.gfx_icon_width - Constants.icon_label_space

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

    def reldir(self, directory):
        """
        Returns a directory at the same level as our current directory.  Er, that makes little
        sense to anyone but me, probably.
        """
        return os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', directory))

    def resfile(self, filename):
        """
        Returns a proper full path to a file in our resource directory, given the base filename
        """
        return os.path.join(self.reldir('res'), filename)

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

    def hoverEnterEvent(self, event=None):
        """
        We've entered hovering
        """
        # TODO: multi-select actions, of course
        self.scene().hover_start(self)
        self.setBrush(QtGui.QBrush(Constants.c_highlight))
        self.setPen(QtGui.QPen(Constants.c_highlight))
        self.setFocus()
        actions = []
        actions.append(('WASD', 'nudge room'))
        actions.append(('X', 'delete'))
        actions.append(('H/V', 'toggle horiz/vert offset'))
        actions.append(('R', 'change color'))
        actions.append(('T', 'change type'))
        Constants.statusbar.set_hover_actions(
            actions=actions,
            prefix='({}, {})'.format(self.gui_room.room.x+1, self.gui_room.room.y+1),
            )

    def hoverLeaveEvent(self, event=None):
        """
        We've left hovering
        """
        self.scene().hover_end()
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.clearFocus()
        self.scene().default_actions()

    def keyPressEvent(self, event):
        """
        Keyboard input
        """
        # TODO: readonly checks
        key = event.text().lower()
        scene = self.scene()
        mapobj = scene.mapobj
        room = self.gui_room.room
        need_scene_recreate = False
        keep_hover = None
        if key == 'r':
            room.increment_color()
            need_scene_recreate = True
            keep_hover = room
        elif key == 't':
            room.increment_type()
            need_scene_recreate = True
            keep_hover = room
        elif key == 'h':
            room.offset_x = not room.offset_x
            need_scene_recreate = True
            keep_hover = room
        elif key == 'v':
            room.offset_y = not room.offset_y
            need_scene_recreate = True
            keep_hover = room
        elif key == 'w':
            mapobj.move_room(room, DIR_N)
            need_scene_recreate = True
            keep_hover = room
        elif key == 'a':
            mapobj.move_room(room, DIR_W)
            need_scene_recreate = True
            keep_hover = room
        elif key == 's':
            mapobj.move_room(room, DIR_S)
            need_scene_recreate = True
            keep_hover = room
        elif key == 'd':
            mapobj.move_room(room, DIR_E)
            need_scene_recreate = True
            keep_hover = room
        elif key == 'x':
            if len(mapobj.rooms) < 2:
                # TODO: notification
                return
            mapobj.del_room(room)
            self.hoverLeaveEvent()
            need_scene_recreate = True

        # Update, if need be
        if need_scene_recreate:
            scene.recreate(keep_hover)

    def mousePressEvent(self, event):
        """
        What to do when the mouse is pressed
        """
        mods = event.modifiers()
        if (mods & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier:
            scene = self.scene()
            room = self.gui_room.room
            scene.select_room(room)
            scene.recreate(room)


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
        self.setFont(GUIRoom.get_notes_font(Constants.default_note_size))
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

class GUIRoomTextLabel(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, parent, text, graphic, y):

        super().__init__(graphic, parent)

        # Loop through to find out what size we can put in there
        width = 999
        chars = min(15, len(text))
        self.label = QtWidgets.QGraphicsTextItem(parent)
        self.label.setDefaultTextColor(parent.color_text)
        while (width > Constants.other_max_width):
            self.label.setPlainText(text)
            for font_size in Constants.other_font_sizes:
                self.label.setFont(GUIRoom.get_other_font(font_size))
                rect = self.label.boundingRect()
                width = rect.width() - Constants.other_padding_x[font_size]*2
                if width <= Constants.other_max_width:
                    break
            if width > Constants.other_max_width:
                chars -= 1
                if chars == 0:
                    break
                text = '{} ...'.format(text[:chars])
        icon_x = Constants.room_size_half - (Constants.gfx_icon_width + Constants.icon_space_between + width)/2

        # Set our own position
        self.setPos(icon_x, y)

        # Set the text position
        self.label.setPos(
                icon_x + Constants.gfx_icon_width + Constants.icon_space_between - Constants.other_padding_x[font_size],
                y - Constants.other_padding_y[font_size]
            )

class GUINewRoomHover(QtWidgets.QGraphicsRectItem):

    def __init__(self, gui_newroom):
        super().__init__(gui_newroom)
        self.gui_newroom = gui_newroom
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsFocusable)
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.setRect(0, 0, Constants.room_size, Constants.room_size)
        self.setZValue(Constants.z_value_new_room_hover)

    def hoverEnterEvent(self, event=None):
        """
        We've entered hovering
        """
        # TODO: multi-select actions, of course
        self.scene().hover_start(self)
        self.setBrush(QtGui.QBrush(Constants.c_highlight))
        self.setPen(QtGui.QPen(Constants.c_highlight))
        self.setFocus()
        actions = []
        actions.append(('LMB', 'click-and-drag'))
        Constants.statusbar.set_hover_actions(
            actions=actions,
            prefix='({}, {})'.format(self.gui_newroom.x+1, self.gui_newroom.y+1),
            )

    def hoverLeaveEvent(self, event=None):
        """
        We've left hovering
        """
        self.scene().hover_end()
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.clearFocus()
        self.scene().default_actions()

    def mousePressEvent(self, event):
        """
        Handle a mouse press event
        """
        self.scene().start_dragging()

    def mouseReleaseEvent(self, event):
        """
        Handle a mouse release event
        """
        self.scene().stop_dragging()

class GUINewRoom(QtWidgets.QGraphicsRectItem):

    def __init__(self, x, y, mainwindow):
        super().__init__()
        self.x = x
        self.y = y
        self.mainwindow = mainwindow
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.setZValue(Constants.z_value_new_room)
        self.set_position()

        # Also add a Hover object for ourselves
        self.hover_obj = GUINewRoomHover(self)

    def set_position(self):
        """
        Sets our position within the scene, based on our room coords
        """
        self.gfx_x = Constants.room_space_half + (Constants.room_size+Constants.room_space)*self.x
        self.gfx_y = Constants.room_space_half + (Constants.room_size+Constants.room_space)*self.y
        self.setRect(0, 0, Constants.room_size, Constants.room_size)
        self.setPos(self.gfx_x, self.gfx_y)

class GUIRoom(QtWidgets.QGraphicsRectItem):

    def __init__(self, room, mainwindow):
        super().__init__()
        self.room = room
        self.mainwindow = mainwindow
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

        elif room.type != Room.TYPE_CONNHELPER:

            # Show our notes, if we need to
            if self.room.notes and self.room.notes != '':
                self.notes = GUIRoomNotesTextItem(self)

            # Show our title
            if room.type != Room.TYPE_CONNHELPER:
                self.title = GUIRoomTitleTextItem(self)

        # Draw any in/out/up/down labels we might have
        if room.type != Room.TYPE_CONNHELPER and room.type != Room.TYPE_LABEL:
            cur_y = Constants.icon_start_y
            for (label, (graphic_light, graphic_dark)) in [
                    (room.up, (Constants.gfx_ladder_up, Constants.gfx_ladder_up_rev)),
                    (room.down, (Constants.gfx_ladder_down, Constants.gfx_ladder_down_rev)),
                    (room.door_in, (Constants.gfx_door_in, Constants.gfx_door_in_rev)),
                    (room.door_out, (Constants.gfx_door_out, Constants.gfx_door_out_rev))]:
                if label and label != '':
                    if room.type == Room.TYPE_DARK:
                        graphic = graphic_dark
                    else:
                        graphic = graphic_light
                    label = GUIRoomTextLabel(self, label, graphic, cur_y)
                    cur_y += graphic.height() + Constants.icon_space_between

        # Set our background/border coloration
        border_pen = QtGui.QPen(self.color_border)
        if self.mainwindow.scene.is_selected(self.room):
            border_pen.setWidth(3)
            if room.type == Room.TYPE_DARK:
                self.setBrush(QtGui.QBrush(self.color_bg.lighter(150)))
            else:
                self.setBrush(QtGui.QBrush(self.color_bg.darker(110)))
        else:
            border_pen.setWidth(1)
            if room.type == Room.TYPE_CONNHELPER:
                self.setBrush(QtGui.QBrush(Constants.c_transparent))
            else:
                self.setBrush(QtGui.QBrush(self.color_bg))

        if room.type == Room.TYPE_CONNHELPER:
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
                line.setPen(border_pen)
        else:
            if pretend_label:
                dash_len = 9/border_pen.width()
                border_pen.setDashPattern([dash_len, dash_len])
            self.setPen(border_pen)
        
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

        # Keep track of what's currently hovering in the scene
        self.hover_current = None

        # Keep track of whether we're currently dragging
        self.dragging = False

        # Keep track of current room selection
        self.selected = set()

        # Default actions
        self.default_actions()

    def hover_start(self, new_hover):
        """
        Make `new_hover` our current hover object.  If there's already
        something being hovered, clear out its hover vars.
        """
        if self.hover_current:
            self.hover_current.hoverLeaveEvent()
        self.hover_current = new_hover

    def hover_end(self):
        """
        Mark that we're no longer hovering over our current hover
        """
        self.hover_current = None

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
        self.selected = set()
        self.mapobj = mapobj
        self.set_dimensions(self.mapobj.w, self.mapobj.h)
        self.recreate()

    def recreate(self, keep_hover=None):
        """
        Recreates the entire scene based on our mapobj object.  This is
        totally the nuclear option - a more subtle program would keep
        track of what's changed and just update those elements, but I'm
        doing it this way for now.  Less to keep track off, less chance
        of a subtle bug causing a disconnect between the data objects
        and the GUI representation.  Pass in `keep_hover` to retain
        hovering on the specified object.
        """
        self.clear()
        self.hover_end()
        # TODO: It shouldn't be possible to have selected rooms disappear
        # on us, but it wouldn't hurt to check for it
        for x in range(self.mapobj.w):
            for y in range(self.mapobj.h):
                room = self.mapobj.get_room_at(x, y)
                if room:
                    guiroom = GUIRoom(room, self.parent().mainwindow)
                    self.addItem(guiroom)
                    if keep_hover == room:
                        guiroom.hover_obj.hoverEnterEvent()
                else:
                    newroom = GUINewRoom(x, y, self.parent().mainwindow)
                    self.addItem(newroom)
                    if keep_hover == (x, y):
                        newroom.hover_obj.hoverEnterEvent()

    def default_actions(self):
        """
        Actions to show when we're not hovering on anything.
        """
        actions = []
        actions.append(('LMB', 'click-and-drag'))
        Constants.statusbar.set_hover_actions(actions=actions)

    def mousePressEvent(self, event):
        """
        Handle a mouse press event
        """
        if self.hover_current:
            super().mousePressEvent(event)
        else:
            self.start_dragging()

    def mouseReleaseEvent(self, event):
        """
        Handle a mouse release event
        """
        if self.hover_current:
            super().mouseReleaseEvent(event)
        else:
            self.stop_dragging()

    def start_dragging(self):
        """
        Start dragging the scene around
        """
        self.dragging = True
        self.parent().setCursor(QtCore.Qt.ClosedHandCursor)

    def stop_dragging(self):
        """
        Stop dragging the scene around
        """
        self.dragging = False
        self.parent().unsetCursor()

    def mouseMoveEvent(self, event):
        """
        Mouse Movement
        """
        if self.dragging:
            last = event.lastScreenPos()
            pos = event.screenPos()
            delta_x = last.x() - pos.x()
            delta_y = last.y() - pos.y()
            if delta_x != 0:
                sb = self.parent().horizontalScrollBar()
                new_x = sb.value() + delta_x
                if new_x >= sb.minimum() and new_x <= sb.maximum():
                    sb.setValue(new_x)
            if delta_y != 0:
                sb = self.parent().verticalScrollBar()
                new_y = sb.value() + delta_y
                if new_y >= sb.minimum() and new_y <= sb.maximum():
                    sb.setValue(new_y)
        else:
            super().mouseMoveEvent(event)

    def has_selections(self):
        """
        Returns `True` or `False` for whether we have any rooms selected
        or not
        """
        return (len(self.selected) > 0)

    def select_room(self, room):
        """
        Adds or removes the given room to our selection list
        """
        if room in self.selected:
            self.selected.remove(room)
        else:
            self.selected.add(room)

    def is_selected(self, room):
        """
        Checks to see if the given Room is selected
        """
        if room in self.selected:
            return True
        else:
            return False

class MapArea(QtWidgets.QGraphicsView):

    statusbar = QtCore.pyqtSignal(str)

    def __init__(self, parent):

        super().__init__(parent)
        self.mainwindow = parent
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
