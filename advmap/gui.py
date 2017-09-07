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

    # Ladder connection vars
    ladder_width = 12
    ladder_rung_spacing = 7
    ladder_line_width = 4

    # Connection offsets - where to find the given connection based on
    # the room's initial (x,y) coord.
    connection_offset = {}
    connection_offset[DIR_N] = (room_size_half, 0)
    connection_offset[DIR_NE] = (room_size, 0)
    connection_offset[DIR_E] = (room_size, room_size_half)
    connection_offset[DIR_SE] = (room_size, room_size)
    connection_offset[DIR_S] = (room_size_half, room_size)
    connection_offset[DIR_SW] = (0, room_size)
    connection_offset[DIR_W] = (0, room_size_half)
    connection_offset[DIR_NW] = (0, 0)

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
    c_connection = QtGui.QColor(0, 0, 0, 255)
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

        # Set up our main widgets
        self.maparea = MapArea(self)
        self.scene = self.maparea.scene
        self.setCentralWidget(self.maparea)
        self.maparea.statusbar[str].connect(self.statusbar.showMessage)
        self.resize(1000, 700)
        self.setWindowTitle('Adventure Game Mapper')

        # Load the specified game, or create a blank map
        self.curfile = None
        if initfile:
            try:
                self.load_from_file(initfile)
            except Exception as e:
                print(e)
        if not self.curfile:
            self.create_new_game()

        # Show ourselves
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
        scene = self.scene()
        scene.hover_start(self)
        self.setBrush(QtGui.QBrush(Constants.c_highlight))
        self.setPen(QtGui.QPen(Constants.c_highlight))
        self.setFocus()
        self.show_actions()

    def show_actions(self):
        """
        Show all appropriate actions when we're hovering
        """
        scene = self.scene()
        actions = []
        if scene.is_selected(self.gui_room.room):
            actions.append(('shift-click', 'deselect'))
        else:
            actions.append(('shift-click', 'select'))
        if scene.has_selections():
            actions.extend(scene.multi_select_actions())
        else:
            actions.append(('WASD', 'nudge room'))
            actions.append(('X', 'delete'))
            actions.append(('H/V', 'toggle horiz/vert offset'))
            actions.append(('T', 'change type'))
            actions.append(('R', 'change color'))
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
        if scene.has_selections():
            scene.process_multi_action(key)
        else:
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
        self.show_actions()

    def show_actions(self):
        """
        Show all valid actions while we're hovering
        """
        actions = []
        actions.append(('LMB', 'click-and-drag'))
        actions.extend(self.scene().multi_select_actions())
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

    def keyPressEvent(self, event):
        """
        Handle a key press event
        """
        # TODO: adding a new room, obvs.
        key = event.text().lower()
        self.scene().process_multi_action(key)

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

    def get_global_connection_xy(self, direction):
        """
        Returns the global Scene positioning of a connection at the given direction.
        Will return a tuple of `(x, y)`
        """
        return (
                self.gfx_x + Constants.connection_offset[direction][0],
                self.gfx_y + Constants.connection_offset[direction][1],
            )

    def get_opposite_room_conn_point(self, direction):
        """
        Returns the global Scene positioning of a hypothetical remote endpoint of
        a room immediately adjacent to us (factoring in our x/y offsets).  Basically
        just used in our "stub" and loopback drawings, so we know where to build the
        line out towards.
        """
        other_x = self.gfx_x
        other_y = self.gfx_y
        step = Constants.room_size + Constants.room_space
        if direction in [DIR_NW, DIR_N, DIR_NE]:
            other_y -= step
        if direction in [DIR_NW, DIR_W, DIR_SW]:
            other_x -= step
        if direction in [DIR_SW, DIR_S, DIR_SE]:
            other_y += step
        if direction in [DIR_NE, DIR_E, DIR_SE]:
            other_x += step
        return (
                other_x + Constants.connection_offset[DIR_OPP[direction]][0],
                other_y + Constants.connection_offset[DIR_OPP[direction]][1],
            )

class GUIConnLine(QtWidgets.QGraphicsLineItem):
    
    def __init__(self, x1, y1, x2, y2, width=1, dashed=False):
        super().__init__(x1, y1, x2, y2)
        self.setZValue(Constants.z_value_connection)
        pen = QtGui.QPen(Constants.c_connection)
        pen.setWidthF(width)
        if dashed:
            dash_len = 3/width
            pen.setDashPattern([dash_len, dash_len])
        self.setPen(pen)

class GUIConnectionFactory(object):
    """
    It's a bit stupid to have this as a class, but I'd like it to be contained
    as well as possible.
    """

    def __init__(self, scene):
        self.scene = scene

    def line(self, x1, y1, x2, y2, width=1, dashed=False):
        """
        Draws a line from `(x1, y1)` to `(x2, y2)`
        """
        line_obj = GUIConnLine(x1, y1, x2, y2, width=width, dashed=dashed)
        self.scene.addItem(line_obj)

    def is_primary_adjacent(self, conn):
        """
        Returns True if the primary connection between two rooms are
        "exactly" adjacent to each other (and implied that the
        connection "lines up" evenly as well).  False if not.  This
        will only act on the primary set of ConnectionEnds (in fact,
        it doens't need to consider Ends since the primary dirs are
        outside of that), and will only return True if the directions
        are opposite from each other.

        This becomes problematic when factoring in the "offset" values
        for rooms - maps like my AMFV attempt end up with very wrong-looking
        connections if you're strict about each room's x+y coordinates
        being "proper," and it feels very wrong to put in gigantic if/elif
        blocks to try and deal with all possible permutations.  Instead,
        we're just going to compute the DISTANCE of the connection which
        would have to be drawn.  Anything more than a room's width away
        and we'll consider them to be nonadjacent.  Since this is sort of
        a GUI concern, that's why it's here instead of in the Connection
        class, which is where it would otherwise make more sense.
        """

        # First off, if we're not connecting on opposite directions, we're
        # not considered adjacent
        if conn.dir1 != DIR_OPP[conn.dir2]:
            return False

        # Now figure out how far apart we are.
        coords_r1 = self.scene.room_to_gui[conn.r1].get_global_connection_xy(conn.dir1)
        coords_r2 = self.scene.room_to_gui[conn.r2].get_global_connection_xy(conn.dir2)
        distance = math.sqrt((coords_r1[0]-coords_r2[0])**2 + (coords_r1[1]-coords_r2[1])**2)

        # ... aaaand there we go.
        return (distance <= Constants.room_size and distance <= Constants.room_size)

    def ladder_coords(self, x1, y1, x2, y2):
        """
        Given two points `(x1, y1)` and `(x2, y2)`, this will provide
        coordinates necessary to draw a ladder between the two.
        It'll return a list of 2-element tuples, each of which is a
        2-element tuple with `(x, y)` coordinates.
        """
        width = Constants.ladder_width
        rung_spacing = Constants.ladder_rung_spacing
        width_h = width/2
        dx_orig = x2-x1
        dy_orig = y2-y1
        dist = math.sqrt(dx_orig**2 + dy_orig**2)
        if dist < 1:
            # Prevent some division-by-zero errors
            dist = 1
        dx = dx_orig / dist
        dy = dy_orig / dist
        coord_list = []

        # First, the two side members
        coord_list.append(
                ((x1+(width_h*dy), y1-(width_h*dx)),
                 (x2+(width_h*dy), y2-(width_h*dx)))
                )
        coord_list.append(
                ((x1-(width_h*dy), y1+(width_h*dx)),
                 (x2-(width_h*dy), y2+(width_h*dx)))
                )

        # Now the rungs
        rungcount = int(dist / rung_spacing) - 1
        if rungcount == 0:
            rungcount = 1
        x_spacing = dx_orig/float(rungcount)
        y_spacing = dy_orig/float(rungcount)
        cur_x = x1 + (x_spacing/2)
        cur_y = y1 + (y_spacing/2)
        for i in range(rungcount):
            coord_list.append(
                    ((cur_x+(width_h*dy), cur_y-(width_h*dx)),
                    (cur_x-(width_h*dy), cur_y+(width_h*dx)))
                )
            cur_x += x_spacing
            cur_y += y_spacing

        return coord_list

    def arrow_coords(self, x1, y1, x2, y2):
        """
        Given two points (x1, y1) and (x2, y2), this will provide
        coordinates necessary to draw an arrowhead centered on (x1, y1)
        It'll return a list with two 2-element tuples, representing
        the (x, y) coordinates.
        """

        # TODO: Figure out a decent name for this var and get it in
        # Constants
        width_h = 8
        dx_orig = x2-x1
        dy_orig = y2-y1
        dist = math.sqrt(dx_orig**2 + dy_orig**2)
        dx = dx_orig / dist
        dy = dy_orig / dist
        coord_list = []

        x_spacing = dx_orig * .5
        y_spacing = dy_orig * .5
        cur_x = x1 + (x_spacing/2)
        cur_y = y1 + (y_spacing/2)

        coord_list.append( (cur_x+(width_h*dy), cur_y-(width_h*dx)) )
        coord_list.append( (cur_x-(width_h*dy), cur_y+(width_h*dx)) )

        return coord_list

    def draw_stub_conn(self, room, direction, conn):
        """
        Draws a "stub" connection from the given room, in the given
        direction.  Returns the "remote" endpoint.  The stubs are used 
        for nonadjacent rooms.
        """
        end = conn.get_end(room, direction)
        if not end:
            return None

        gui_room = self.scene.room_to_gui[room]

        # Basic src/dst as if we were connecting immediately adjacent
        (src_x, src_y) = gui_room.get_global_connection_xy(direction)
        (dst_x, dst_y) = gui_room.get_opposite_room_conn_point(direction)

        # Now apply our stub_length
        if end.stub_length > 1:
            dx = src_x - dst_x
            dy = src_y - dst_y
            dst_x = src_x - (dx*end.stub_length)
            dst_y = src_y - (dy*end.stub_length)

        # When drawing arrows, we want to render based on the length of
        # the stub *before* we cut it in half, just so it's more noticeable.
        # This is most important for ladder one-way connections with short
        # stublengths.
        # TODO: really what we should do is enforce a minimum+maximum here
        # rather than doing this blindly - longer stublengths make for weird
        # looking arrows.  And as for ladders, the BEST thing to do would be
        # to make those look better anyway
        ladder_dst_x = dst_x
        ladder_dst_y = dst_y

        # aaaand we actually only want to render a line half this long.
        dst_x = (src_x+dst_x)/2
        dst_y = (src_y+dst_y)/2

        # If we're a connhelper connection, the source endpoint will
        # actually be in the very center of the room.
        if room.type == Room.TYPE_CONNHELPER:
            src_x = gui_room.gfx_x + Constants.room_size_half
            src_y = gui_room.gfx_y + Constants.room_size_half

        # draw one-way connections.  This will look weird if it's going
        # into a connhelper room, but then again that's probably not
        # what you'd want to be doing anyway
        if conn.is_oneway_a() and room == conn.r1:
            for coord in self.arrow_coords(src_x, src_y, ladder_dst_x, ladder_dst_y):
                self.draw_conn_segment(coord[0], coord[1], src_x, src_y, end)
        if conn.is_oneway_b() and room == conn.r2:
            for coord in self.arrow_coords(src_x, src_y, ladder_dst_x, ladder_dst_y):
                self.draw_conn_segment(coord[0], coord[1], src_x, src_y, end)

        # Draw the actual stub
        self.draw_conn_segment(src_x, src_y, dst_x, dst_y, end)

        # ... and return the destination point
        return (dst_x, dst_y)

    def draw_conn_segment(self, x1, y1, x2, y2, end):
        """
        Draws a connection segment from `(x1, y1)` to `(x2, y2)`, using the
        style provided by the passed-in ConnectionEnd `end`.  Ordinarily
        this is just a single line, but if `is_ladder` is True, then it'll
        build a Ladder graphic between the two, instead.
        """
        if end.is_ladder():
            coords = self.ladder_coords(x1, y1, x2, y2)
            for coord in coords:
                self.line(coord[0][0], coord[0][1],
                        coord[1][0], coord[1][1],
                        width=Constants.ladder_line_width)
        else:
            self.line(x1, y1, x2, y2, dashed=end.is_dotted())

    def draw_connection(self, conn):
        """
        Draws a connection onto a QGraphicsScene
        """

        room1 = conn.r1
        dir1 = conn.dir1
        end_close = conn.ends1[dir1]
        gui_room1 = self.scene.room_to_gui[room1]

        room2 = conn.r2
        dir2 = conn.dir2
        end_far = conn.ends2[dir2]
        gui_room2 = self.scene.room_to_gui[room2]

        # First up - draw the primary connection.  This has the chance of being
        # "adjacent", which will draw a simple line between the two rather than
        # our stubs w/ varying render types.  This will only be the case if
        # the primary conn directions are opposite of each other, and only if
        # the rooms are close enough.  In practice you can get away with one
        # room being offset vertically or horizontally, but not both.  Anything
        # else will get the full stub/etc treatment below

        # Secondary midpoints which extra ends will draw towards
        secondary_midpoints = {}

        if self.is_primary_adjacent(conn):

            if room1.type == Room.TYPE_CONNHELPER:
                first_is_connhelper = True
            else:
                first_is_connhelper = False

            if room2.type == Room.TYPE_CONNHELPER:
                second_is_connhelper = True
            else:
                second_is_connhelper = False

            # Drawing our primary connection as a simple "adjacent" link
            if first_is_connhelper:
                x1 = gui_room1.gfx_x + Constants.room_size_half
                y1 = gui_room1.gfx_y + Constants.room_size_half
            else:
                (x1, y1) = gui_room1.get_global_connection_xy(dir1)
            if second_is_connhelper:
                x2 = gui_room2.gfx_x + Constants.room_size_half
                y2 = gui_room2.gfx_y + Constants.room_size_half
            else:
                (x2, y2) = gui_room2.get_global_connection_xy(dir2)
            secondary_midpoints[room1] = (x2, y2)
            secondary_midpoints[room2] = (x1, y1)
            if end_close.conn_type == end_far.conn_type:
                self.draw_conn_segment(x1, y1, x2, y2, end_close)
            else:
                midpoint_x = (x1 + x2) / 2
                midpoint_y = (y1 + y2) / 2
                self.draw_conn_segment(x1, y1, midpoint_x, midpoint_y, end_close)
                self.draw_conn_segment(midpoint_x, midpoint_y, x2, y2, end_far)
            if conn.is_oneway_a():
                for coord in self.arrow_coords(x1, y1, x2, y2):
                    self.draw_conn_segment(coord[0], coord[1], x1, y1, end_close)
            elif conn.is_oneway_b():
                for coord in self.arrow_coords(x2, y2, x1, y1):
                    self.draw_conn_segment(coord[0], coord[1], x2, y2, end_far)

        else:

            # Drawing our primary connection with stubs coming off the rooms and then
            # based on its render_type
            stub1 = self.draw_stub_conn(room1, dir1, conn)
            stub2 = self.draw_stub_conn(room2, dir2, conn)

class MapScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent):

        super().__init__(parent)

        self.mapobj = None
        self.set_dimensions(1, 1)

        # Keep track of what's currently hovering in the scene
        self.hover_current = None

        # Keep track of whether we're currently dragging
        self.dragging = False
        self.dragged = False

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
        # First render our rooms
        self.room_to_gui = {}
        for x in range(self.mapobj.w):
            for y in range(self.mapobj.h):
                room = self.mapobj.get_room_at(x, y)
                if room:
                    guiroom = GUIRoom(room, self.parent().mainwindow)
                    self.addItem(guiroom)
                    self.room_to_gui[room] = guiroom
                    if keep_hover == room:
                        guiroom.hover_obj.hoverEnterEvent()
                else:
                    newroom = GUINewRoom(x, y, self.parent().mainwindow)
                    self.addItem(newroom)
                    if keep_hover == (x, y):
                        newroom.hover_obj.hoverEnterEvent()

        # Next all the connections
        cf = GUIConnectionFactory(self)
        for conn in self.mapobj.conns:
            cf.draw_connection(conn)

        # If we haven't re-hovered anything, revert to our default hover text
        if not self.hover_current:
            self.default_actions()

    def default_actions(self):
        """
        Actions to show when we're not hovering on anything.
        """
        actions = []
        actions.append(('LMB', 'click-and-drag'))
        actions.extend(self.multi_select_actions())
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
        if not self.dragged and len(self.selected) > 0:
            self.selected = set()
            self.recreate()
            if not self.hover_current:
                self.default_actions()

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
                self.dragged = True
                sb = self.parent().horizontalScrollBar()
                new_x = sb.value() + delta_x
                if new_x >= sb.minimum() and new_x <= sb.maximum():
                    sb.setValue(new_x)
            if delta_y != 0:
                self.dragged = True
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

    def multi_select_actions(self):
        """
        Return a list of multi-select actions, if appropriate.
        """
        actions = []
        if self.has_selections():
            actions.append(('WASD', 'nudge rooms'))
            actions.append(('H/V', 'toggle horiz/vert offsets'))
            actions.append(('T', 'change types'))
            actions.append(('R', 'change colors'))
        return actions

    def keyPressEvent(self, event):
        """
        Keyboard input
        """
        if self.has_selections():
            self.process_multi_action(event.text().lower())
        else:
            super().keyPressEvent(event)

    def process_multi_action(self, key):
        """
        Processes an action operating on (hypothetically) more than one
        selected room.
        """
        if self.has_selections():
            need_scene_recreate = False
            if (key == 'h'):
                need_scene_recreate = True
                num_offset = 0
                num_not_offset = 0
                for room in self.selected:
                    if room.offset_x:
                        num_offset += 1
                    else:
                        num_not_offset += 1
                # Invert whatever the current majority is.  In the event of
                # a tie, we'll default to making everything offset.
                if num_offset > num_not_offset:
                    set_value = False
                else:
                    set_value = True
                for room in self.selected:
                    room.offset_x = set_value
            elif (key == 'v'):
                need_scene_recreate = True
                num_offset = 0
                num_not_offset = 0
                for room in self.selected:
                    if room.offset_y:
                        num_offset += 1
                    else:
                        num_not_offset += 1
                # Invert whatever the current majority is.  In the event of
                # a tie, we'll default to making everything offset.
                if num_offset > num_not_offset:
                    set_value = False
                else:
                    set_value = True
                for room in self.selected:
                    room.offset_y = set_value
            elif (key == 't'):
                need_scene_recreate = True
                type_hist = {}
                type_to_room = {}
                max_rooms_in_single_type = 0
                room_to_increment = None
                for room in self.selected:
                    if room.type in type_hist:
                        type_hist[room.type] += 1
                    else:
                        type_hist[room.type] = 1
                        type_to_room[room.type] = room
                    if type_hist[room.type] > max_rooms_in_single_type:
                        max_rooms_in_single_type = type_hist[room.type]
                        room_to_increment = room
                if room_to_increment:
                    room_to_increment.increment_type()
                    for room in self.selected:
                        room.type = room_to_increment.type
            elif (key == 'r'):
                need_scene_recreate = True
                color_hist = {}
                color_to_room = {}
                max_rooms_in_single_color = 0
                room_to_increment = None
                for room in self.selected:
                    if room.color in color_hist:
                        color_hist[room.color] += 1
                    else:
                        color_hist[room.color] = 1
                        color_to_room[room.color] = room
                    if color_hist[room.color] > max_rooms_in_single_color:
                        max_rooms_in_single_color = color_hist[room.color]
                        room_to_increment = room
                if room_to_increment:
                    room_to_increment.increment_color()
                    for room in self.selected:
                        room.color = room_to_increment.color
            elif (key == 'w'):
                if self.mapobj.nudge(DIR_N, self.selected):
                    need_scene_recreate = True
            elif (key == 'a'):
                if self.mapobj.nudge(DIR_W, self.selected):
                    need_scene_recreate = True
            elif (key == 's'):
                if self.mapobj.nudge(DIR_S, self.selected):
                    need_scene_recreate = True
            elif (key == 'd'):
                if self.mapobj.nudge(DIR_E, self.selected):
                    need_scene_recreate = True

            # Update, if need be
            if need_scene_recreate:
                self.recreate()

class MapArea(QtWidgets.QGraphicsView):

    statusbar = QtCore.pyqtSignal(str)

    def __init__(self, parent):

        super().__init__(parent)
        self.mainwindow = parent
        # If we notice issues with text rendering in the
        # future, 'or' in the TextAntialiasing hint too
        self.setRenderHints(QtGui.QPainter.Antialiasing)
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
