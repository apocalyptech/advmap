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

import os.path
import math
import gtk
import gtk.gdk
import gobject
import cairo
import pango
import pangocairo
from struct import unpack

from advmap.data import *

class GUI(object):
    """
    The app
    """

    # Hovering modes
    HOVER_NONE = 0
    HOVER_ROOM = 1
    HOVER_EDGE = 2
    HOVER_CONN = 3
    HOVER_CONN_NEW = 4

    def __init__(self, initfile=None, readonly=False):
        """
        Initializes everything; this is where just about everything is set
        up.  We'll load an initial file if told too, as well - otherwise we'll
        just start out with a minimal map.  Finally (for now), we can request
        to start out in readonly mode.
        """

        # Make sure to dampen signals if we need to
        self.initgfx = False

        # Initial Glade setup
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.resfile('main.ui'))
        self.window = self.builder.get_object('mainwindow')
        self.mainscroll = self.builder.get_object('mainscroll')
        self.mainarea = self.builder.get_object('mainarea')
        self.titlelabel = self.builder.get_object('titlelabel')
        self.hoverlabel = self.builder.get_object('hoverlabel')
        self.map_combo = self.builder.get_object('map_combo')
        self.nudge_lock = self.builder.get_object('nudge_lock')
        self.grid_display = self.builder.get_object('grid_display')
        self.readonly_lock = self.builder.get_object('readonly_lock')
        self.menu_revert = self.builder.get_object('menu_revert')
        self.show_offset_check = self.builder.get_object('show_offset_check')
        self.statusbar = self.builder.get_object('statusbar')
        self.sbcontext = self.statusbar.get_context_id('Main Messages')
        self.secondary_status = self.builder.get_object('secondary_status')
        self.aboutwindow = None

        # View Room Readonly dialog
        self.view_room_dialog = self.builder.get_object('view_room_dialog')
        self.view_room_roomname_label = self.builder.get_object('view_room_roomname_label')
        self.view_room_roomtype_label = self.builder.get_object('view_room_roomtype_label')
        self.view_room_up_label = self.builder.get_object('view_room_up_label')
        self.view_room_up_hdr = self.builder.get_object('view_room_up_hdr')
        self.view_room_down_label = self.builder.get_object('view_room_down_label')
        self.view_room_down_hdr = self.builder.get_object('view_room_down_hdr')
        self.view_room_in_label = self.builder.get_object('view_room_in_label')
        self.view_room_in_hdr = self.builder.get_object('view_room_in_hdr')
        self.view_room_out_label = self.builder.get_object('view_room_out_label')
        self.view_room_out_hdr = self.builder.get_object('view_room_out_hdr')
        self.view_room_scroll = self.builder.get_object('view_room_scroll')
        self.view_room_notes_hdr = self.builder.get_object('view_room_notes_hdr')
        self.view_room_notes_view = self.builder.get_object('view_room_notes_view')

        # New Room / Edit Room dialog
        self.edit_room_dialog = self.builder.get_object('edit_room_dialog')
        self.edit_room_label = self.builder.get_object('edit_room_label')
        self.roomtype_radio_normal = self.builder.get_object('roomtype_radio_normal')
        self.roomtype_radio_hi_green = self.builder.get_object('roomtype_radio_hi_green')
        self.roomtype_radio_hi_red = self.builder.get_object('roomtype_radio_hi_red')
        self.roomtype_radio_hi_blue = self.builder.get_object('roomtype_radio_hi_blue')
        self.roomtype_radio_hi_yellow = self.builder.get_object('roomtype_radio_hi_yellow')
        self.roomtype_radio_hi_purple = self.builder.get_object('roomtype_radio_hi_purple')
        self.roomtype_radio_hi_cyan = self.builder.get_object('roomtype_radio_hi_cyan')
        self.roomtype_radio_faint = self.builder.get_object('roomtype_radio_faint')
        self.roomtype_radio_dark = self.builder.get_object('roomtype_radio_dark')
        self.roomtype_radio_label = self.builder.get_object('roomtype_radio_label')
        self.roomname_entry = self.builder.get_object('roomname_entry')
        self.room_up_entry = self.builder.get_object('room_up_entry')
        self.room_down_entry = self.builder.get_object('room_down_entry')
        self.room_in_entry = self.builder.get_object('room_in_entry')
        self.room_out_entry = self.builder.get_object('room_out_entry')
        self.roomnotes_view = self.builder.get_object('roomnotes_view')
        self.edit_room_ok = self.builder.get_object('edit_room_ok')
        self.edit_room_cancel = self.builder.get_object('edit_room_cancel')
        self.room_offset_x = self.builder.get_object('room_offset_x')
        self.room_offset_y = self.builder.get_object('room_offset_y')

        # Existing room group dropdown elements (will be hidden when the dialog is
        # setting up a new room, as opposed to editing existing)
        self.room_group_label = self.builder.get_object('room_group_label')
        self.room_group_box = self.builder.get_object('room_group_box')
        self.room_group_align = self.builder.get_object('room_group_align')

        # Form elements unique to creating a new connection
        self.new_to_dir_label = self.builder.get_object('new_to_dir_label')
        self.new_to_dir_align = self.builder.get_object('new_to_dir_align')
        self.new_conn_style_label = self.builder.get_object('new_conn_style_label')
        self.new_conn_style_align = self.builder.get_object('new_conn_style_align')
        self.new_conn_type_label = self.builder.get_object('new_conn_type_label')
        self.new_conn_type_align = self.builder.get_object('new_conn_type_align')
        self.new_group_with_label = self.builder.get_object('new_group_with_label')
        self.new_group_with_align = self.builder.get_object('new_group_with_align')
        self.new_group_with_button = self.builder.get_object('new_group_with_button')

        self.new_to_dir_box = gtk.combo_box_new_text()
        self.new_to_dir_box.set_name('new_to_dir_box')
        for txtdir in DIR_LIST:
            self.new_to_dir_box.append_text(DIR_2_TXT[txtdir].upper())
        self.new_to_dir_align.add(self.new_to_dir_box)

        self.new_conn_style_regular = gtk.RadioButton(None, 'Regular', False)
        self.new_conn_style_regular.set_name('new_conn_style_regular')
        self.new_conn_style_ladder = gtk.RadioButton(self.new_conn_style_regular, 'Ladder', False)
        self.new_conn_style_ladder.set_name('new_conn_style_ladder')
        self.new_conn_style_dotted = gtk.RadioButton(self.new_conn_style_regular, 'Dotted', False)
        self.new_conn_style_dotted.set_name('new_conn_style_dotted')
        self.new_conn_style_none = gtk.RadioButton(self.new_conn_style_regular, 'None', False)
        self.new_conn_style_none.set_name('new_conn_style_none')
        self.new_conn_style_box = gtk.HBox()
        self.new_conn_style_box.pack_start(self.new_conn_style_regular, False, True)
        self.new_conn_style_box.pack_start(self.new_conn_style_ladder, False, True)
        self.new_conn_style_box.pack_start(self.new_conn_style_dotted, False, True)
        self.new_conn_style_box.pack_start(self.new_conn_style_none, False, True)
        self.new_conn_style_align.add(self.new_conn_style_box)

        self.new_conn_type_pass_twoway = gtk.RadioButton(None, 'Two-Way', False)
        self.new_conn_type_pass_twoway.set_name('new_conn_type_pass_twoway')
        self.new_conn_type_pass_oneway_in = gtk.RadioButton(self.new_conn_type_pass_twoway, 'One-Way Into New Room', False)
        self.new_conn_type_pass_oneway_in.set_name('new_conn_type_pass_oneway_in')
        self.new_conn_type_pass_oneway_out = gtk.RadioButton(self.new_conn_type_pass_twoway, 'One-Way Out', False)
        self.new_conn_type_pass_oneway_out.set_name('new_conn_type_pass_oneway_out')
        self.new_conn_type_box = gtk.HBox()
        self.new_conn_type_box.pack_start(self.new_conn_type_pass_twoway, False, True)
        self.new_conn_type_box.pack_start(self.new_conn_type_pass_oneway_in, False, True)
        self.new_conn_type_box.pack_start(self.new_conn_type_pass_oneway_out, False, True)
        self.new_conn_type_align.add(self.new_conn_type_box)

        # Edit Game dialog
        self.edit_game_dialog = self.builder.get_object('edit_game_dialog')
        self.gamename_entry = self.builder.get_object('gamename_entry')
        self.map_treeview = self.builder.get_object('map_treeview')
        self.edit_game_ok = self.builder.get_object('edit_game_ok')
        self.edit_game_cancel = self.builder.get_object('edit_game_cancel')
        self.edit_game_map_add_button = self.builder.get_object('edit_game_map_add_button')
        self.edit_game_map_remove_button = self.builder.get_object('edit_game_map_remove_button')

        # New Map dialog
        self.new_map_dialog = self.builder.get_object('new_map_dialog')
        self.new_map_dialog_title = self.builder.get_object('new_map_dialog_title')
        self.new_map_entry = self.builder.get_object('new_map_entry')
        self.new_map_ok = self.builder.get_object('new_map_ok')

        # Notes view window
        self.notes_window = self.builder.get_object('notes_window')
        self.global_notes_view = self.builder.get_object('global_notes_view')

        # Nudge buttons
        self.nudge_n = self.builder.get_object('nudge_n')
        self.nudge_ne = self.builder.get_object('nudge_ne')
        self.nudge_e = self.builder.get_object('nudge_e')
        self.nudge_se = self.builder.get_object('nudge_se')
        self.nudge_s = self.builder.get_object('nudge_s')
        self.nudge_sw = self.builder.get_object('nudge_sw')
        self.nudge_w = self.builder.get_object('nudge_w')
        self.nudge_nw = self.builder.get_object('nudge_nw')
        self.nudge_buttons = [self.nudge_n, self.nudge_ne, self.nudge_e, self.nudge_se,
                self.nudge_s, self.nudge_sw, self.nudge_w, self.nudge_nw]

        # Resize buttons
        self.resize_n = self.builder.get_object('resize_n')
        self.resize_s = self.builder.get_object('resize_s')
        self.resize_w = self.builder.get_object('resize_w')
        self.resize_e = self.builder.get_object('resize_e')
        self.resize_buttons = [self.resize_n, self.resize_s, self.resize_w, self.resize_e]

        # Tooltips
        self.nudge_n.set_tooltip_text('Shift map to the north')
        self.nudge_ne.set_tooltip_text('Shift map to the northeast')
        self.nudge_e.set_tooltip_text('Shift map to the east')
        self.nudge_se.set_tooltip_text('Shift map to the southeast')
        self.nudge_s.set_tooltip_text('Shift map to the south')
        self.nudge_sw.set_tooltip_text('Shift map to the southwest')
        self.nudge_w.set_tooltip_text('Shift map to the west')
        self.nudge_nw.set_tooltip_text('Shift map to the northwest')
        self.nudge_lock.set_tooltip_text('Toggle in-map room nudging')
        self.grid_display.set_tooltip_text('Toggle map grid')
        self.readonly_lock.set_tooltip_text('Toggle readonly')
        self.resize_n.set_tooltip_text('Cut off bottom row of map')
        self.resize_s.set_tooltip_text('Add row to bottom of map')
        self.resize_w.set_tooltip_text('Cut off rightmost row of map')
        self.resize_e.set_tooltip_text('Add column to right of map')
        self.builder.get_object('edit_game_button').set_tooltip_text('Edit map properties')

        # Explicitly set our widget names (needed for gtk+ 2.20 compatibility)
        # See https://bugzilla.gnome.org/show_bug.cgi?id=591085
        for object in self.builder.get_objects():
            try:
                builder_name = gtk.Buildable.get_name(object)
                if builder_name:
                    object.set_name(builder_name)
            except TypeError:
                pass

        # Signals
        dic = {
                'on_quit': self.on_quit,
                'on_new': self.on_new,
                'on_load': self.on_load,
                'on_revert': self.on_revert,
                'on_save': self.on_save,
                'on_save_as': self.on_save_as,
                'on_about': self.on_about,
                'on_expose': self.on_expose,
                'on_notes_close': self.on_notes_close,
                'on_map_clicked': self.on_map_clicked,
                'on_map_released': self.on_map_released,
                'on_mouse_changed': self.on_mouse_changed,
                'key_handler': self.key_handler,
                'nudge_map': self.nudge_map,
                'nudge_lock_toggled': self.nudge_lock_toggled,
                'grid_display_toggled': self.grid_display_toggled,
                'readonly_toggled': self.readonly_toggled,
                'map_resize': self.map_resize,
                'edit_room_activate': self.edit_room_activate,
                'map_combo_changed': self.map_combo_changed,
                'edit_game': self.edit_game,
                'edit_game_activate': self.edit_game_activate,
                'map_add': self.map_add,
                'map_remove': self.map_remove,
                'new_map_activate': self.new_map_activate,
                'open_notes': self.open_notes,
                'open_notes_all': self.open_notes_all,
                'draw_offset_toggle': self.draw_offset_toggle,
                'duplicate_map': self.duplicate_map,
                'export_image': self.export_image
            }
        self.builder.connect_signals(dic)

        # Pango contexts for rendering text
        self.pangoctx = self.window.get_pango_context()
        self.room_layout = pango.Layout(self.pangoctx)
        self.room_layout.set_font_description(pango.FontDescription('sans normal 7'))

        # State vars
        self.dragging = False
        self.hover = self.HOVER_NONE
        self.curhover = None
        self.hover_roomobj = None
        self.hover_connobj = None
        self.move_room = None
        self.move_dir = None
        self.link_conn_room = None
        self.link_conn_dir = None
        self.add_extra_room = None
        self.add_extra_dir = None
        self.grouping_room = None
        self.cursor_move_drag = gtk.gdk.Cursor(gtk.gdk.DOT)
        self.cursor_wait = gtk.gdk.Cursor(gtk.gdk.WATCH)

        # Sizing information
        # TODO: Should really figure out zooming sooner rather than later
        # Note that our max total rooms is 255, because of how our mousemaps
        # work.  If we have a square map, that means that it's 15x15
        self.room_w = 110
        self.room_h = 110
        self.room_spc = 30
        self.room_spc_h = self.room_spc/2
        self.room_spc_grp = 10

        # Connection offsets
        self.CONN_OFF = []
        self.CONN_OFF.append((self.room_w/2, 0))
        self.CONN_OFF.append((self.room_w, 0))
        self.CONN_OFF.append((self.room_w, self.room_h/2))
        self.CONN_OFF.append((self.room_w, self.room_h))
        self.CONN_OFF.append((self.room_w/2, self.room_h))
        self.CONN_OFF.append((0, self.room_h))
        self.CONN_OFF.append((0, self.room_h/2))
        self.CONN_OFF.append((0, 0))

        # Hovering connection offsets
        self.CONN_H_OFF = list(self.CONN_OFF)
        for (dir, val) in enumerate(self.CONN_H_OFF):
            (x, y) = val
            x -= self.room_spc_h
            y -= self.room_spc_h
            self.CONN_H_OFF[dir] = (x, y)

        # Mousemap edge offsets
        self.EDGE_OFF = []
        self.EDGE_OFF.append((self.room_w/2-self.room_spc_h, 0))
        self.EDGE_OFF.append((self.room_w-self.room_spc, 0))
        self.EDGE_OFF.append((self.room_w-self.room_spc, self.room_h/2-self.room_spc_h))
        self.EDGE_OFF.append((self.room_w-self.room_spc, self.room_h-self.room_spc))
        self.EDGE_OFF.append((self.room_w/2-self.room_spc_h, self.room_h-self.room_spc))
        self.EDGE_OFF.append((0, self.room_h-self.room_spc))
        self.EDGE_OFF.append((0, self.room_h/2-self.room_spc_h))
        self.EDGE_OFF.append((0, 0))

        # Hover overlay information
        self.h_x = -1
        self.h_y = -1
        self.h_w = -1
        self.h_h = -1

        # Event mask for key presses
        self.keymask = gtk.gdk.CONTROL_MASK|gtk.gdk.MOD1_MASK|gtk.gdk.MOD3_MASK
        self.keymask |= gtk.gdk.MOD4_MASK|gtk.gdk.MOD5_MASK

        # Vars for use in delayed statusbar updates
        self.delay_status_curid = -1
        self.delay_status_text = ''

        # For now, let's just create a new game by default, will check args later
        self.curfile = None
        if (initfile):
            try:
                self.load_from_file(initfile)
            except Exception as e:
                print(e)
                self.errordialog('Unable to load file: %s - starting with a blank map' % e)
        if not self.curfile:
            self.create_new_game()

        # Lock ourselves to readonly if we're told to
        if readonly:
            self.readonly_lock.set_active(True)

        # Set the game name and level dropdown
        self.updating_gameinfo = False
        self.update_gameinfo()

        # Set our initial sizing information
        # TODO: why can't we just do this inside draw()?  If we don't do it
        # here, the scrollbars don't get centered properly, but why not?
        self.set_area_size()

        # Set up some vars for the Edit Game treeview
        self.MAP_COL_TEXT = 0
        self.MAP_COL_EDIT = 1
        self.MAP_COL_CURIDX = 2
        self.MAP_COL_ROOMS = 3
        self.MAP_COL_ROOMEDIT = 4
        self.mapstore = gtk.ListStore( gobject.TYPE_STRING,
                gobject.TYPE_BOOLEAN,
                gobject.TYPE_INT,
                gobject.TYPE_INT,
                gobject.TYPE_BOOLEAN)
        self.map_treeview.set_model(self.mapstore)
        renderer = gtk.CellRendererText()
        renderer.connect('edited', self.on_mapname_edited, self.mapstore)
        renderer.set_data('column', self.MAP_COL_TEXT)
        column = gtk.TreeViewColumn('Maps', renderer, text=self.MAP_COL_TEXT, editable=self.MAP_COL_EDIT)
        column.set_min_width(200)
        self.map_treeview.append_column(column)
        column = gtk.TreeViewColumn("Rooms", renderer, text=self.MAP_COL_ROOMS, editable=self.MAP_COL_ROOMEDIT)
        column.set_cell_data_func(renderer, self.cellformat_rooms)
        self.map_treeview.append_column(column)

        # Some similar vars for the room dropdown in "Edit Room"
        self.ROOM_COL_NAME = 0
        self.ROOM_COL_IDX = 1
        self.room_mapstore = gtk.ListStore( gobject.TYPE_STRING,
                gobject.TYPE_INT)
        renderer = gtk.CellRendererText()
        renderer.set_data('column', self.ROOM_COL_NAME)
        column = gtk.TreeViewColumn('Name', renderer, text=self.ROOM_COL_NAME)
        self.room_group_box.set_model(self.room_mapstore)
        self.room_group_box.clear()
        self.room_group_box.pack_start(renderer, True)
        self.room_group_box.add_attribute(renderer, 'markup', self.ROOM_COL_NAME)

        # Pango object for drawing "notes"
        self.notes_layout = pango.Layout(self.pangoctx)
        self.notes_layout.set_markup('<i>(notes)</i>')
        (notes_layout_w, notes_layout_h) = (x/pango.SCALE for x in self.notes_layout.get_size())
        self.notes_layout_x_off = ((self.room_w-notes_layout_w)/2)
        #self.notes_layout_y_off = ((self.room_h-notes_layout_h)/2)
        self.notes_layout_y_off = ((self.room_h/2)-notes_layout_h)
        self.notes_layout_y_bottom = self.notes_layout_y_off + notes_layout_h

        # Grab a couple of images for up/down
        self.ladder_up_surf = cairo.ImageSurface.create_from_png(self.resfile('ladder_up.png'))
        self.ladder_down_surf = cairo.ImageSurface.create_from_png(self.resfile('ladder_down.png'))
        self.door_in_surf = cairo.ImageSurface.create_from_png(self.resfile('door_in.png'))
        self.door_out_surf = cairo.ImageSurface.create_from_png(self.resfile('door_out.png'))
        self.ladder_up_rev_surf = cairo.ImageSurface.create_from_png(self.resfile('ladder_up_rev.png'))
        self.ladder_down_rev_surf = cairo.ImageSurface.create_from_png(self.resfile('ladder_down_rev.png'))
        self.door_in_rev_surf = cairo.ImageSurface.create_from_png(self.resfile('door_in_rev.png'))
        self.door_out_rev_surf = cairo.ImageSurface.create_from_png(self.resfile('door_out_rev.png'))

        # Keyboard mask for processing keys
        self.keymask = gtk.gdk.CONTROL_MASK|gtk.gdk.MOD1_MASK|gtk.gdk.MOD3_MASK
        self.keymask |= gtk.gdk.MOD4_MASK|gtk.gdk.MOD5_MASK

        # File filters to use for dialogs
        self.filefilter1 = gtk.FileFilter()
        self.filefilter1.set_name('Game Map Files')
        self.filefilter1.add_pattern('*.adv')
        self.filefilter2 = gtk.FileFilter()
        self.filefilter2.set_name('All Files')
        self.filefilter2.add_pattern('*')

        # Set up tags for the notes textview info area
        tag_table = self.global_notes_view.get_buffer().get_tag_table()
        tag = gtk.TextTag('mapheader')
        tag.set_property('weight', pango.WEIGHT_BOLD)
        tag.set_property('justification', gtk.JUSTIFY_CENTER)
        tag_table.add(tag)
        tag = gtk.TextTag('roomheader')
        tag.set_property('weight', pango.WEIGHT_BOLD)
        tag.set_property('justification', gtk.JUSTIFY_LEFT)
        tag_table.add(tag)
        tag = gtk.TextTag('coords')
        tag.set_property('weight', pango.WEIGHT_LIGHT)
        tag.set_property('justification', gtk.JUSTIFY_LEFT)
        tag.set_property('style', pango.STYLE_ITALIC)
        tag_table.add(tag)
        tag = gtk.TextTag('notes')
        tag.set_property('weight', pango.WEIGHT_NORMAL)
        tag.set_property('justification', gtk.JUSTIFY_LEFT)
        tag.set_property('left-margin', 15)
        tag_table.add(tag)
        tag = gtk.TextTag('nonotes')
        tag.set_property('weight', pango.WEIGHT_LIGHT)
        tag.set_property('justification', gtk.JUSTIFY_CENTER)
        tag.set_property('style', pango.STYLE_ITALIC)
        tag_table.add(tag)

        # ... and prepare for our mainloop
        gobject.idle_add(self.draw)

    def update_notes(self, note):
        # TODO: should have this happen in __init__, etc...
        if len(note) > 15:
            note = '%s...' % (note[:12])
        self.notes_layout.set_markup('<i>%s</i>' % (note.replace("\n", ' ')))
        (notes_layout_w, notes_layout_h) = (x/pango.SCALE for x in self.notes_layout.get_size())
        self.notes_layout_x_off = ((self.room_w-notes_layout_w)/2)
        #self.notes_layout_y_off = ((self.room_h-notes_layout_h)/2)
        self.notes_layout_y_off = ((self.room_h/2)-notes_layout_h)
        self.notes_layout_y_bottom = self.notes_layout_y_off + notes_layout_h

    def cellformat_rooms(self, column, renderer, model, iter, user_data=None):
        """
        Format our "rooms" column.  (basically just adds "room" or "rooms" to the end)
        """
        roomcount = model.get_value(iter, self.MAP_COL_ROOMS)
        if (roomcount == 1):
            renderer.set_property('text', '1 room')
        else:
            renderer.set_property('text', '%d rooms' % (roomcount))

    def set_hover(self, text):
        """
        Sets the text of our hover
        """
        if (text != ''):
            text = '<i>%s</i>' % (gobject.markup_escape_text(text))
        self.hoverlabel.set_markup(text)

    def set_status(self, text):
        """
        Pushes some text out to our status bar
        """
        self.statusbar.push(self.sbcontext, text)

    def set_secondary_status(self, text):
        """
        Sets our secondary statusbar text
        """
        self.secondary_status.set_markup('<i>%s</i>' % text)

    def set_status_delayed(self, text, timeout=5):
        """
        Function used to set the statusbar after some interval
        """
        self.delay_status_curid += 1
        self.delay_status_text = text
        gobject.timeout_add_seconds(timeout, self.set_status_delayed_timeout, self.delay_status_curid)

    def set_status_delayed_timeout(self, id):
        """
        This is the function fired off after an interval, to set the status
        """
        if (id == self.delay_status_curid):
            self.set_status(self.delay_status_text)
        return False

    def cancel_delayed_status(self):
        """
        Cancels any active delayed status update, without updating a new one.
        """
        self.delay_status_curid += 1
        self.delay_status_text = ''

    def set_delayed_edit(self):
        """
        Sets a delayed status update to revert back to the "Editing <file>" status
        """
        self.set_status_delayed('Editing %s' % self.curfile)

    def run(self):
        """
        Here we go!
        """
        self.window.show_all()
        gtk.main()

    def reldir(self, dir):
        """
        Returns a directory at the same level as our current directory.  Er, that makes little
        sense to anyone but me, probably.
        """
        return os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', dir))

    def resfile(self, filename):
        """
        Returns a proper full path to a file in our resource directory, given the base filename
        """
        return os.path.join(self.reldir('res'), filename)

    def datafile(self, filename):
        """
        Returns a proper full path to a file in our data directory, given the base filename
        """
        return os.path.join(self.reldir('data'), filename)

    def userdialog(self, type, buttons, markup, parent=None):
        """
        Opens up a dialog for the user, with the given attributes
        """
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                type, buttons)
        if not parent:
            parent = self.window
        dialog.set_transient_for(parent)
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_markup(markup)
        result = dialog.run()
        dialog.destroy()
        return result

    def infodialog(self, markup, parent=None):
        """
        Throws up a dialog with some info in it.
        """
        return self.userdialog(gtk.MESSAGE_INFO, gtk.BUTTONS_OK, markup, parent)

    def errordialog(self, markup, parent=None):
        """
        Throws up a dialog with an error in it.
        """
        return self.userdialog(gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, markup, parent)

    def confirmdialog(self, markup, parent=None):
        """
        Throws up a Yes/No dialog.
        """
        return self.userdialog(gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, markup, parent)

    def on_about(self, widget):
        """
        Display an About screen
        """
        if (not self.aboutwindow):
            about = gtk.AboutDialog()
            about.set_transient_for(self.window)
            about.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            about.set_name('Adventure Game Mapper')
            about.set_version('0.1')
            about.set_website('http://apocalyptech.com/adv_map/')
            about.set_authors(['CJ Kucera'])
            licensepath = self.reldir('COPYING.txt')
            if (os.path.isfile(licensepath)):
                try:
                    df = open(licensepath, 'r')
                    about.set_license(df.read())
                    df.close()
                except:
                    pass
            self.aboutwindow = about

        # Now run
        self.aboutwindow.run()
        self.aboutwindow.hide()

    def on_new(self, widget=None):
        """
        New
        """
        result = self.confirmdialog('Starting a new game will erase any unsaved changes.  Really wipe the current map?')
        if (result == gtk.RESPONSE_YES):
            self.create_new_game()

    def on_load(self, widget=None):
        """
        Throws up a Load dialog
        """
        dialog = gtk.FileChooserDialog('Open Game Map File...', None,
                gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_transient_for(self.window)
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.add_filter(self.filefilter1)
        dialog.add_filter(self.filefilter2)
        if self.curfile:
            path = os.path.dirname(os.path.realpath(self.curfile))
        else:
            path = self.reldir('data')
        dialog.set_current_folder(path)

        rundialog = True
        while (rundialog):
            rundialog = False
            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                try:
                    self.load_from_file(dialog.get_filename())
                except Exception as e:
                    self.errordialog('Unable to open file: %s' % e, dialog)
                    rundialog = True

        dialog.destroy()
        return True

    def on_revert(self, widget=None):
        """
        Revert
        """
        # TODO: grey out Revert until we've actually loaded
        if (self.curfile):
            try:
                self.load_from_file(self.curfile)
                self.set_delayed_edit()
                self.set_status('Reverted to on-disk copy of %s' % self.curfile)
            except Exception as e:
                self.errordialog('Unable to revert, error in on-disk file: %s' % e)
        else:
            self.errordialog('Cannot revert, this map has never been saved to disk.')
                

    def on_save(self, widget=None):
        """
        Save
        """
        if self.curfile:
            self.game.save(self.curfile)
            self.set_delayed_edit()
            self.set_status('Game saved to %s' % self.curfile)
        else:
            self.on_save_as()

    def on_save_as(self, widget=None):
        """
        Save As
        """
        dialog = gtk.FileChooserDialog('Save Game File...', None,
                gtk.FILE_CHOOSER_ACTION_SAVE,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_transient_for(self.window)
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.add_filter(self.filefilter1)
        dialog.add_filter(self.filefilter2)
        dialog.set_do_overwrite_confirmation(True)
        if self.curfile:
            path = os.path.dirname(os.path.realpath(self.curfile))
        else:
            path = self.reldir('data')
        dialog.set_current_folder(path)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.curfile = dialog.get_filename()
            if (self.curfile[-4:] != '.adv'):
                self.curfile = '%s.adv' % (self.curfile)
            self.game.save(self.curfile)
            self.menu_revert.set_sensitive(True)
            self.set_delayed_edit()
            self.set_status('Game saved to %s' % self.curfile)

        dialog.destroy()

    def create_new_game(self):
        """
        Starts a new Game file from scratch.
        """
        self.curfile = None
        self.menu_revert.set_sensitive(False)
        self.game = Game('New Game')
        self.mapobj = self.create_new_map('Starting Map')
        self.map_idx = self.game.add_map_obj(self.mapobj)
        self.cancel_delayed_status()
        self.set_status('Editing a new game')
        if (self.initgfx):
            self.update_gameinfo()
            self.trigger_redraw()

    def load_from_file(self, filename):
        """
        Loads a game from a file.  Note that we always return
        true; if loading failed, the load() method should raise an
        exception, which should be caught by anything attempting
        the load.
        """
        game = Game.load(filename)
        self.menu_revert.set_sensitive(True)
        self.game = game
        self.mapobj = self.game.maps[0]
        self.map_idx = 0
        self.curfile = filename
        if (self.initgfx):
            self.update_gameinfo()
            self.trigger_redraw()
        self.cancel_delayed_status()
        self.set_status('Editing %s' % filename)
        return True

    def update_title(self):
        """
        Updates our game/map name display
        """
        self.titlelabel.set_markup('<b>%s</b> | %s' % (gobject.markup_escape_text(self.game.name), gobject.markup_escape_text(self.mapobj.name)))

    def update_gameinfo(self):
        """
        Updates our game name and level dropdown
        """
        self.updating_gameinfo = True
        self.update_title()
        self.map_combo.get_model().clear()
        for mapobj in self.game.maps:
            self.map_combo.append_text(mapobj.name)
        self.map_combo.set_active(self.map_idx)
        self.updating_gameinfo = False

    def room_xy_coord(self, room_x, room_y):
        """
        Returns a tuple with (x, y) starting coordinates for a room which would
        be at its own (room_x, room_y)
        """
        x = self.room_spc + (self.room_w+self.room_spc)*room_x
        y = self.room_spc + (self.room_h+self.room_spc)*room_y
        return (x, y)

    def apply_xy_offset(self, x, y, room):
        """
        Applies any offsets active in 'room' to the x, y coordinate pair
        """
        if (self.show_offset_check.get_active()):
            if room.offset_x:
                x += ((self.room_w+self.room_spc)/2)
            if room.offset_y:
                y += ((self.room_h+self.room_spc)/2)
        return (x, y)

    def room_xy(self, room):
        """
        Returns a tuple with (x, y) starting coordinates for the given room,
        taking into consideration any offsets
        """
        (x, y) = self.room_xy_coord(room.x, room.y)
        return self.apply_xy_offset(x, y, room)

    def create_new_map(self, name):
        """
        Creates our default new map, with a single room in the center
        """
        mapobj = Map(name)
        room = mapobj.add_room_at(4, 4, 'Starting Room')
        room.type = Room.TYPE_HI_GREEN
        return mapobj

    def arrow_coords(self, x1, y1, x2, y2):
        """
        Given two points (x1, y1) and (x2, y2), this will provide
        coordinates necessary to draw an arrowhead centered on (x1, y1)
        It'll return a list with two 2-element tuples, representing
        the (x, y) coordinates.
        """

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

    def ladder_coords(self, x1, y1, x2, y2, width, rung_spacing):
        """
        Given two points (x1, y1) and (x2, y2), this will provide
        coordinates necessary to draw a ladder between the two.
        It'll return a list of 2-element tuples, each of which is a 
        2-element tuple with (x, y) coordinates.
        """
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

    def get_conn_xy(self, room, direction):
        """
        Returns the GUI x/y coordinates of the connection from the
        given room, in the given direction.  This will factor in
        offsets properly, as well.
        """
        coords_base = self.apply_xy_offset(*self.room_xy_coord(room.x, room.y), room=room)
        return (coords_base[0] + self.CONN_OFF[direction][0], coords_base[1] + self.CONN_OFF[direction][1])

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
        coords_r1 = self.get_conn_xy(conn.r1, conn.dir1)
        coords_r2 = self.get_conn_xy(conn.r2, conn.dir2)
        distance = math.sqrt((coords_r1[0]-coords_r2[0])**2 + (coords_r1[1]-coords_r2[1])**2)

        # ... aaaand there we go.
        return (distance <= self.room_w and distance <= self.room_h)

    def draw_conn_segment(self, ctx, x1, y1, x2, y2, end):
        """
        Draws a connection segment from (x1, y1) to (x2, y2), using the
        style provided by the passed in ConnectionEnd `end`.  Ordinarily
        this is just a single line, but if is_ladder is True, then it'll
        build a Ladder graphic between the two, instead.
        """
        ctx.save()
        if end.is_ladder():
            ladder_width=12
            rung_spacing=7
            coords = self.ladder_coords(x1, y1, x2, y2, ladder_width, rung_spacing)
            ctx.set_source_rgba(*self.c_borders)
            ctx.set_line_width(4)
            for coord in coords:
                ctx.move_to(coord[0][0], coord[0][1])
                ctx.line_to(coord[1][0], coord[1][1])
                ctx.stroke()
        else:
            ctx.set_source_rgba(*self.c_borders)
            ctx.set_line_width(1)
            if (end.is_dotted()):
                ctx.set_dash([3.0], 0)
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
            ctx.stroke()
        ctx.restore()

    def draw_stub_conn(self, ctx, room, direction, conn):
        """
        Draws a "stub" connection from the given room, in the given
        direction.  Returns the "remote" endpoint.  The stubs are used
        nonadjacent rooms.
        """
        (room_x, room_y) = self.room_xy(room)
        dir_coord = self.mapobj.dir_coord(room, direction, True)
        if not dir_coord:
            return None
        end = conn.get_end(room, direction)
        if not end:
            return None
        conn_coord = self.room_xy_coord(*self.mapobj.dir_coord(room, direction, True))
        if conn_coord:
            (conn_x, conn_y) = self.apply_xy_offset(conn_coord[0], conn_coord[1], room)
            x1 = room_x+self.CONN_OFF[direction][0]
            y1 = room_y+self.CONN_OFF[direction][1]
            orig_x2 = conn_x+self.CONN_OFF[DIR_OPP[direction]][0]
            orig_y2 = conn_y+self.CONN_OFF[DIR_OPP[direction]][1]

            # Factor in our varying stublength
            orig_x2 = x1 - end.stub_length*(x1 - orig_x2)
            orig_y2 = y1 - end.stub_length*(y1 - orig_y2)

            # We're actually going to pick a point halfway between the two,
            # to prevent stubs that appear to connect to rooms they don't
            # actually connect to
            x2 = int((x1+orig_x2)/2)
            y2 = int((y1+orig_y2)/2)

            if conn.is_oneway_a() and room == conn.r1:
                for coord in self.arrow_coords(x1, y1, orig_x2, orig_y2):
                    self.draw_conn_segment(ctx, coord[0], coord[1], x1, y1, end)
            elif conn.is_oneway_b() and room == conn.r2:
                for coord in self.arrow_coords(x1, y1, orig_x2, orig_y2):
                    self.draw_conn_segment(ctx, coord[0], coord[1], x1, y1, end)

            self.draw_conn_segment(ctx, x1, y1, x2, y2, end)
            return (x2, y2)
        else:
            return None

    def get_point_along_line(self, x1, y1, x2, y2, percent):
        """
        Given a line defined by (x1, y1) and (x2, y2), return
        the point along that line which is `percent` percent of
        the way between the first and second points.  `percent`
        should be a float from 0.0 to 1.0.  Returns a tuple
        of `(x, y)`
        """
        return (
                x1 + int((x2 - x1) * percent),
                y1 + int((y2 - y1) * percent),
            )

    def draw_room(self, room, ctx, mmctx, drawn_conns):
        """
        Draws a room onto the given context (and mousemap ctx).  Will
        skip drawing any connections already seen inside drawn_conns,
        and add to that list as need be
        """

        # Starting position of room
        (x, y) = self.room_xy(room)

        readonly = self.readonly_lock.get_active()

        # Rooms with a name of "(unexplored)" become labels, effectively.
        # So that's what we're doing here.
        if (room.type == Room.TYPE_LABEL or room.unexplored()):
            is_label = True
        else:
            is_label = False

        # Figure out our colors
        if (not is_label and room.type in self.c_type_map):
            border = self.c_type_map[room.type][0]
            background = self.c_type_map[room.type][1]
            textcolor = self.c_type_map[room.type][2]
        else:
            border = self.c_type_default[0]
            background = self.c_type_default[1]
            textcolor = self.c_type_default[2]

        # Draw the room
        ctx.save()
        if (is_label):
            ctx.set_source_rgba(*self.c_label)
            ctx.set_dash([9.0], 0)
        else:
            ctx.set_source_rgba(*background)
            ctx.rectangle(x, y, self.room_w, self.room_h)
            ctx.fill()
            ctx.set_source_rgba(*border)
        ctx.set_line_width(1)
        ctx.rectangle(x, y, self.room_w, self.room_h)
        ctx.stroke()
        ctx.restore()

        # Mousemap room box
        mmctx.set_source_rgba(self.m_step*self.HOVER_ROOM, 0, self.m_step*room.idnum)
        mmctx.rectangle(x, y, self.room_w, self.room_h)
        mmctx.fill()

        # Now also draw connections off of the room
        for direction in DIR_LIST:
            conn = room.get_conn(direction)
            if (conn):
                if conn not in drawn_conns:

                    drawn_conns.add(conn)
                    (room2, dirs2) = conn.get_opposite(room)

                    # First up - draw the primary connection.  This has the chance of being
                    # "adjacent", which will draw a simple line between the two rather than
                    # our stubs w/ varying render types.  This will only be the case if
                    # the primary conn directions are opposite of each other, and only if
                    # the rooms are close enough.  In practice you can get away with one
                    # room being offset vertically or horizontally, but not both.  Anything
                    # else will get the full stub/etc treatment below

                    # Vars to use while rendering the primary
                    if room == conn.r1:
                        prim_direction = conn.dir1
                        end_close = conn.ends1[prim_direction]
                        end_far = conn.ends2[conn.dir2]
                        dir2 = conn.dir2
                    else:
                        prim_direction = conn.dir2
                        end_close = conn.ends2[prim_direction]
                        end_far = conn.ends1[conn.dir1]
                        dir2 = conn.dir1

                    # Secondary midpoints which extra ends will draw towards
                    secondary_midpoints = {}

                    if self.is_primary_adjacent(conn):

                        # Drawing our primary connection as a simple "adjacent" link
                        (conn_x, conn_y) = self.room_xy(room2)
                        x1 = x+self.CONN_OFF[prim_direction][0]
                        y1 = y+self.CONN_OFF[prim_direction][1]
                        x2 = conn_x+self.CONN_OFF[dir2][0]
                        y2 = conn_y+self.CONN_OFF[dir2][1]
                        secondary_midpoints[room] = (x2, y2)
                        secondary_midpoints[room2] = (x1, y1)
                        if end_close.conn_type == end_far.conn_type:
                            self.draw_conn_segment(ctx, x1, y1, x2, y2, end_close)
                        else:
                            midpoint_x = (x1 + x2) / 2
                            midpoint_y = (y1 + y2) / 2
                            self.draw_conn_segment(ctx, x1, y1, midpoint_x, midpoint_y, end_close)
                            self.draw_conn_segment(ctx, midpoint_x, midpoint_y, x2, y2, end_far)
                        if conn.is_oneway_a():
                            if conn.r1 == room:
                                for coord in self.arrow_coords(x1, y1, x2, y2):
                                    self.draw_conn_segment(ctx, coord[0], coord[1], x1, y1, end_close)
                            else:
                                for coord in self.arrow_coords(x2, y2, x1, y1):
                                    self.draw_conn_segment(ctx, coord[0], coord[1], x2, y2, end_far)
                        elif conn.is_oneway_b():
                            if conn.r2 == room:
                                for coord in self.arrow_coords(x1, y1, x2, y2):
                                    self.draw_conn_segment(ctx, coord[0], coord[1], x1, y1, end_close)
                            else:
                                for coord in self.arrow_coords(x2, y2, x1, y1):
                                    self.draw_conn_segment(ctx, coord[0], coord[1], x2, y2, end_far)

                    else:

                        # Drawing our primary connection with stubs coming off the rooms and then
                        # based on its render_type
                        stub1 = self.draw_stub_conn(ctx, room, prim_direction, conn)
                        stub2 = self.draw_stub_conn(ctx, room2, dir2, conn)
                        if (stub1 and stub2):
                            if end_close.is_render_midpoint_a():
                                secondary_percent = .75
                                secondary_midpoints[room] = self.get_point_along_line(stub1[0], stub1[1],
                                        stub1[0], stub2[1], secondary_percent)
                                secondary_midpoints[room2] = self.get_point_along_line(stub2[0], stub2[1],
                                        stub1[0], stub2[1], secondary_percent)
                                self.draw_conn_segment(ctx, stub1[0], stub2[1], stub1[0], stub1[1], end_close)
                                self.draw_conn_segment(ctx, stub1[0], stub2[1], stub2[0], stub2[1], end_far)
                            elif end_close.is_render_midpoint_b():
                                secondary_percent = .75
                                secondary_midpoints[room] = self.get_point_along_line(stub1[0], stub1[1],
                                        stub2[0], stub1[1], secondary_percent)
                                secondary_midpoints[room2] = self.get_point_along_line(stub2[0], stub2[1],
                                        stub2[0], stub1[1], secondary_percent)
                                self.draw_conn_segment(ctx, stub2[0], stub1[1], stub1[0], stub1[1], end_close)
                                self.draw_conn_segment(ctx, stub2[0], stub1[1], stub2[0], stub2[1], end_far)
                            else:
                                secondary_percent = .40
                                secondary_midpoints[room] = self.get_point_along_line(stub1[0], stub1[1],
                                        stub2[0], stub2[1], secondary_percent)
                                secondary_midpoints[room2] = self.get_point_along_line(stub2[0], stub2[1],
                                        stub1[0], stub1[1], secondary_percent)
                                if end_close.conn_type == end_far.conn_type:
                                    self.draw_conn_segment(ctx, stub1[0], stub1[1], stub2[0], stub2[1], end_close)
                                else:
                                    midpoint_x = (stub1[0] + stub2[0]) / 2
                                    midpoint_y = (stub1[1] + stub2[1]) / 2
                                    self.draw_conn_segment(ctx, stub1[0], stub1[1], midpoint_x, midpoint_y, end_close)
                                    self.draw_conn_segment(ctx, midpoint_x, midpoint_y, stub2[0], stub2[1], end_far)

                    # And now draw any additional ends which may exist.  These will
                    # always have stubs coming off of them, and will have their own
                    # render_type describing how to connect to the main connection
                    for end in conn.get_all_extra_ends():

                        # First the stub
                        stub = self.draw_stub_conn(ctx, end.room, end.direction, conn)

                        # And then the rest of the connection
                        if end.room in secondary_midpoints:
                            (mid_x, mid_y) = secondary_midpoints[end.room]
                            if end.is_render_midpoint_a():
                                self.draw_conn_segment(ctx, stub[0], mid_y, stub[0], stub[1], end)
                                self.draw_conn_segment(ctx, stub[0], mid_y, mid_x, mid_y, end)
                            elif end.is_render_midpoint_b():
                                self.draw_conn_segment(ctx, mid_x, stub[1], stub[0], stub[1], end)
                                self.draw_conn_segment(ctx, mid_x, stub[1], mid_x, mid_y, end)
                            else:
                                self.draw_conn_segment(ctx, stub[0], stub[1], mid_x, mid_y, end)

                conn_hover = self.HOVER_CONN

            elif room.get_loopback(direction):
                conn_hover = self.HOVER_CONN
                coord = self.get_conn_xy(room, direction)
                # TODO: resizing the map so this gets to the edge will cause a TypeError
                coord_far = self.room_xy_coord(*self.mapobj.dir_coord(room, direction, True))
                if coord_far:
                    fakeend = ConnectionEnd(None, None)

                    (conn_x, conn_y) = self.apply_xy_offset(coord_far[0], coord_far[1], room)
                    orig_x2 = conn_x+self.CONN_OFF[DIR_OPP[direction]][0]
                    orig_y2 = conn_y+self.CONN_OFF[DIR_OPP[direction]][1]
                    if direction == DIR_NW or direction == DIR_NE or direction == DIR_SE or direction == DIR_SW:
                        x2 = int((coord[0]*2+orig_x2)/3)
                        y2 = int((coord[1]*2+orig_y2)/3)
                    else:
                        x2 = int((coord[0]*3+orig_x2*2)/5)
                        y2 = int((coord[1]*3+orig_y2*2)/5)
                    self.draw_conn_segment(ctx, coord[0], coord[1], x2, y2, fakeend)

                    dx_orig = x2-coord[0]
                    dy_orig = y2-coord[1]
                    dist = math.sqrt(dx_orig**2 + dy_orig**2)
                    dx = dx_orig / dist
                    dy = dy_orig / dist

                    x3 = x2 + (dist*dy)
                    y3 = y2 - (dist*dx)
                    self.draw_conn_segment(ctx, x2, y2, x3, y3, fakeend)

                    x4 = coord[0] + (dist*dy)
                    y4 = coord[1] - (dist*dx)
                    self.draw_conn_segment(ctx, x4, y4, x3, y3, fakeend)
                    for coord_arrow in self.arrow_coords(x3, y3, x4, y4):
                        self.draw_conn_segment(ctx, coord_arrow[0], coord_arrow[1], x4, y4, fakeend)

            else:
                if (len(self.mapobj.rooms) == 256):
                    coord = self.mapobj.dir_coord(room, direction)
                    if (not coord):
                        continue
                    if (not self.mapobj.get_room_at(*coord)):
                        continue
                conn_hover = self.HOVER_CONN_NEW

            # Draw the mousemap too, though only if we Should
            if not readonly:
                if (not room.get_conn(direction) and not room.get_loopback(direction) and (
                    (room.y == 0 and direction in [DIR_NW, DIR_N, DIR_NE]) or
                    (room.y == self.mapobj.h-1 and direction in [DIR_SW, DIR_S, DIR_SE]) or
                    (room.x == 0 and direction in [DIR_NW, DIR_W, DIR_SW]) or
                    (room.x == self.mapobj.w-1 and direction in [DIR_NE, DIR_E, DIR_SE]))):
                    continue
                mmctx.set_source_rgba(self.m_step*conn_hover, self.m_step*direction, self.m_step*room.idnum)
                mmctx.rectangle(x+self.CONN_H_OFF[direction][0], y+self.CONN_H_OFF[direction][1], self.room_spc, self.room_spc)
                mmctx.fill()

        # Mousemap edges
        if (not readonly and self.nudge_lock.get_active()):
            for (direction, junk) in enumerate(DIR_OPP):
                coords = self.mapobj.dir_coord(room, direction)
                if coords:
                    if (not self.mapobj.get_room_at(*coords)):
                        mmctx.set_source_rgba(self.m_step*self.HOVER_EDGE, self.m_step*direction, self.m_step*room.idnum)
                        mmctx.rectangle(x+self.EDGE_OFF[direction][0], y+self.EDGE_OFF[direction][1], self.room_spc, self.room_spc)
                        mmctx.fill()

        if (is_label):
            label_layout = pango.Layout(self.pangoctx)
            label_layout.set_markup('<i>%s</i>' % (gobject.markup_escape_text(room.name)))
            label_layout.set_width((self.room_w-self.room_spc)*pango.SCALE)
            label_layout.set_wrap(pango.WRAP_WORD)
            label_layout.set_alignment(pango.ALIGN_CENTER)
            max_width = self.room_w-self.room_spc_h
            max_height = self.room_h-self.room_spc_h
            for size in [10, 9, 8, 7, 6]:
                label_layout.set_font_description(pango.FontDescription('sans regular %d' % (size)))
                (width, height) = (x/pango.SCALE for x in label_layout.get_size())
                if (width <= max_width and height <= max_height):
                    break
            ctx.move_to(x+self.room_spc_h, y+((self.room_h - height)/2))
            ctx.set_source_rgba(*textcolor)
            pangoctx = pangocairo.CairoContext(ctx)
            pangoctx.show_layout(label_layout)
        else:
            # Draw the room title
            if (room.notes and room.notes != ''):
                self.update_notes(room.notes)
            title_layout = pango.Layout(self.pangoctx)
            title_layout.set_markup(gobject.markup_escape_text(room.name))
            title_layout.set_width((self.room_w-self.room_spc)*pango.SCALE)
            title_layout.set_wrap(pango.WRAP_WORD)
            title_layout.set_alignment(pango.ALIGN_CENTER)
            max_width = self.room_w-self.room_spc_h
            max_height = self.notes_layout_y_off-(self.room_spc_h/2)
            for size in [10, 9, 8, 7, 6]:
                title_layout.set_font_description(pango.FontDescription('sans bold %d' % (size)))
                (width, height) = (x/pango.SCALE for x in title_layout.get_size())
                if (width <= max_width and height <= max_height):
                    break
            ctx.move_to(x+self.room_spc_h, y+(self.room_spc_h/2))
            ctx.set_source_rgba(*textcolor)
            pangoctx = pangocairo.CairoContext(ctx)
            pangoctx.show_layout(title_layout)

            # ... show "notes" identifier
            if (room.notes and room.notes != ''):
                ctx.move_to(x+self.notes_layout_x_off, y+self.notes_layout_y_off)
                ctx.set_source_rgba(*textcolor)
                pangoctx.show_layout(self.notes_layout)

            # ... and any up/down/in/out arrows
            # TODO: some magic numbers in here
            icon_txt_spc = 3
            icon_dim = self.ladder_up_surf.get_width()
            cur_y = y + self.notes_layout_y_bottom + 7
            cur_x = x+(self.room_w-icon_dim)/2
            max_w = self.room_w - self.room_spc - icon_dim - icon_txt_spc
            max_h = icon_dim + 4
            for (label, (graphic_light, graphic_dark)) in [
                    (room.up, (self.ladder_up_surf, self.ladder_up_rev_surf)),
                    (room.down, (self.ladder_down_surf, self.ladder_down_rev_surf)),
                    (room.door_in, (self.door_in_surf, self.door_in_rev_surf)),
                    (room.door_out, (self.door_out_surf, self.door_out_rev_surf))]:
                if (label and label != ''):
                    layout = pango.Layout(self.pangoctx)
                    text = label
                    width = 999
                    height = 999
                    chars = 15
                    while (width > max_w or height > max_h):
                        layout.set_markup(gobject.markup_escape_text(text))
                        for size in [8, 7, 6]:
                            layout.set_font_description(pango.FontDescription('sans regular %d' % (size)))
                            (width, height) = (x/pango.SCALE for x in layout.get_size())
                            if (width <= max_w and height <= max_h):
                                break
                        if (width <= max_w or height <= max_h):
                            text = '%s ...' % (text[:chars])
                            chars -= 1
                    ladder_x = x + ((110-(icon_dim+icon_txt_spc+width))/2)
                    text_x = ladder_x + icon_dim + icon_txt_spc

                    # Draw the icon
                    if room.type == Room.TYPE_DARK:
                        graphic = graphic_dark
                    else:
                        graphic = graphic_light
                    ctx.set_source_surface(graphic, ladder_x, cur_y)
                    ctx.move_to(cur_x, cur_y)
                    ctx.paint()

                    # ... and render the text
                    # TODO: y processing, text can overlap somewhat
                    ctx.move_to(text_x, cur_y)
                    ctx.set_source_rgba(*textcolor)
                    pangoctx = pangocairo.CairoContext(ctx)
                    pangoctx.show_layout(layout)

                    # And carriage-return ourselves down for the possible next line
                    cur_y += self.ladder_up_surf.get_height() + 4

    def set_area_size(self):
        """
        Sets the size of our drawing areas, etc.  We need to call this from more
        than one place...
        """
        self.area_x = self.room_w*self.mapobj.w + self.room_spc*(self.mapobj.w+1)
        self.area_y = self.room_h*self.mapobj.h + self.room_spc*(self.mapobj.h+1)
        self.mainarea.set_size_request(self.area_x, self.area_y)

    def draw(self, widget=None):
        """
        Do the initial drawing of the map.

        mapmap
        mapctx - The ctx directly tied to the main window.  Transient graphics
                 (mouseovers, popups) should be drawn here.

        cleansurf
        cleanctx - Completely-clean context/surface, devoid of any disease cubes, pawns,
                   etc.

        mmsurf
        mmctx - Mousemap, for hovering, etc
        """

        # Colors
        self.c_background = (1, 1, 1, 1)
        self.c_borders = (0, 0, 0, 1)
        self.c_label = (.7, .7, .7, 1)
        self.c_highlight = (.5, 1, .5, .2)
        self.c_highlight_nudge = (.7, .7, .7, .2)
        self.c_highlight_del = (1, .5, .5, .2)
        self.c_highlight_new = (.5, .5, 1, .2)
        self.c_grid = (.9, .9, .9, 1)

        self.c_group_map = {
                Group.STYLE_NORMAL: (.85, .85, .85, 1),
                Group.STYLE_RED: (.95, .85, .85, 1),
                Group.STYLE_GREEN: (.85, .95, .85, 1),
                Group.STYLE_BLUE: (.85, .85, .95, 1),
                Group.STYLE_YELLOW: (.95, .95, .85, 1),
                Group.STYLE_PURPLE: (.95, .85, .95, 1),
                Group.STYLE_CYAN: (.85, .95, .95, 1),
                Group.STYLE_FAINT: (.95, .95, .95, 1),
                Group.STYLE_DARK: (.65, .65, .65, 1),
            }
        self.c_group_default = self.c_group_map[Group.STYLE_NORMAL]

        c_default_text = (0, 0, 0, 1)
        self.c_type_map = {
                Room.TYPE_HI_RED: ((.5, 0, 0, 1), (1, .98, .98, 1), c_default_text),
                Room.TYPE_HI_GREEN: ((0, .5, 0, 1), (.98, 1, .98, 1), c_default_text),
                Room.TYPE_HI_BLUE: ((0, 0, .5, 1), (.98, .98, 1, 1), c_default_text),
                Room.TYPE_HI_YELLOW: ((.5, .5, 0, 1), (1, 1, .98, 1), c_default_text),
                Room.TYPE_HI_PURPLE: ((.5, 0, .5, 1), (1, .98, 1, 1), c_default_text),
                Room.TYPE_HI_CYAN: ((0, .5, .5, 1), (.98, 1, 1, 1), c_default_text),
                Room.TYPE_FAINT: ((.6, .6, .6, 1), (1, 1, 1, 1), (.4, .4, .4, 1)),
                Room.TYPE_DARK: ((0, 0, 0, 1), (.35, .35, .35, 1), (.9, .9, .9, 1))
            }
        self.c_type_default = (self.c_borders, (.98, .98, .98, 1), c_default_text)

        # Set initial sizing information
        self.set_area_size()

        # Other vars
        self.mainwin = self.mainarea.window
        self.gc_state = self.mainarea.get_style().fg_gc[gtk.STATE_NORMAL]
        self.mapmap = gtk.gdk.Pixmap(self.mainarea.window, self.area_x, self.area_y)
        self.mapctx = self.mapmap.cairo_create()

        # Completely-clean surface
        self.cleansurf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.area_x, self.area_y)
        self.cleanctx = cairo.Context(self.cleansurf)
        
        # Mousemaps
        self.mmsurf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.area_x, self.area_y)
        self.mmctx = cairo.Context(self.mmsurf)
        self.mmctx.set_antialias(cairo.ANTIALIAS_NONE)
        self.m_step = 1/256.0

        # Set our backgrounds
        self.cleanctx.set_source_rgba(*self.c_background)
        self.cleanctx.paint()
        self.mmctx.set_source_rgba(0, 0, 0, 1)
        self.mmctx.paint()

        # Draw our grid, if we've been told to
        if self.grid_display.get_active():
            self.cleanctx.set_source_rgba(*self.c_grid)
            self.cleanctx.set_line_width(1)
            for x in [self.room_spc_h + i*(self.room_w + self.room_spc) for i in range(self.mapobj.w+1)]:
                self.cleanctx.move_to(x, 0)
                self.cleanctx.line_to(x, self.area_y)
                self.cleanctx.stroke()
            for y in [self.room_spc_h + i*(self.room_h + self.room_spc) for i in range(self.mapobj.h+1)]:
                self.cleanctx.move_to(0, y)
                self.cleanctx.line_to(self.area_x, y)
                self.cleanctx.stroke()

        # Loop through any groups and draw them, too
        for group in self.mapobj.groups:
            max_x = 0
            max_y = 0
            min_x = 9999
            min_y = 9999
            for room in group.get_rooms():
                (x, y) = self.room_xy(room)
                if (x < min_x):
                    min_x = x
                if (x > max_x):
                    max_x = x
                if (y < min_y):
                    min_y = y
                if (y > max_y):
                    max_y = y
            min_x -= self.room_spc_grp
            min_y -= self.room_spc_grp
            max_x += self.room_spc_grp + self.room_w
            max_y += self.room_spc_grp + self.room_h
            if group.style in self.c_group_map:
                self.cleanctx.set_source_rgba(*self.c_group_map[group.style])
            else:
                self.cleanctx.set_source_rgba(*self.c_group_default)
            self.cleanctx.rectangle(min_x, min_y, max_x-min_x, max_y-min_y)
            self.cleanctx.fill()

        # Loop through and draw our rooms
        drawn_conns = set()
        for room in self.mapobj.roomlist():
            if room:
                self.draw_room(room, self.cleanctx, self.mmctx, drawn_conns)

        # Now copy our clean image over to the appropriate surfaces
        self.mapctx.set_source_surface(self.cleansurf, 0, 0)
        self.mapctx.paint()
        
        # Pull out our mousemap data arrays
        self.mmdata = self.mmsurf.get_data()

        # If we're just loading for the first time, set our scrollbar adjustments
        if (not self.initgfx):
            hadj = self.mainscroll.get_hadjustment()
            if (hadj.upper > hadj.page_size):
                hadj.set_value((hadj.upper-hadj.page_size)/2)
            vadj = self.mainscroll.get_vadjustment()
            if (vadj.upper > vadj.page_size):
                vadj.set_value((vadj.upper-vadj.page_size)/2)

        # Render and let the prog know we're initted
        self.mainwin.draw_drawable(self.gc_state, self.mapmap, 0, 0, 0, 0, self.area_x, self.area_y)
        self.initgfx = True

        #self.mmsurf.write_to_png('omg.png')

        # To clear out our idle_add
        return False

    def on_quit(self, widget=None, event=None):
        """
        Quit
        """
        gtk.main_quit()

    def on_expose(self, widget, event):
        """
        Fill in data from our surface when needed
        """
        if self.initgfx:
            self.mainwin.draw_drawable(self.gc_state, self.mapmap, 0, 0, 0, 0, self.area_x, self.area_y)

    def hover_simple(self, x, y, w, h, color=None):
        """
        Hover some stuff, right now this is a simple composite
        """
        if not color:
            color = self.c_highlight
        # Do the composite
        ctx = self.mapctx
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ATOP)
        ctx.set_source_rgba(*color)
        ctx.rectangle(x, y, w, h)
        ctx.fill()
        ctx.restore()

        # and set our hovering vars
        self.h_x = x
        self.h_y = y
        self.h_w = w
        self.h_h = h

    def hover_room(self):
        """
        Draw a hovered room
        """
        room = self.curhover
        (x, y) = self.room_xy(room)
        self.hover_simple(x, y, self.room_w, self.room_h)

    def hover_conn(self, color=None):
        """
        Draw a hovered connection
        """
        if not color:
            color = self.c_highlight_new
        (room, dir) = self.curhover
        (x, y) = self.room_xy(room)
        x += self.CONN_H_OFF[dir][0]
        y += self.CONN_H_OFF[dir][1]
        self.hover_simple(x, y, self.room_spc, self.room_spc, color)

    def hover_edge(self):
        """
        Draw a hovered edge
        """
        (room, dir) = self.curhover
        (x, y) = self.room_xy(room)
        x += self.EDGE_OFF[dir][0]
        y += self.EDGE_OFF[dir][1]
        self.hover_simple(x, y, self.room_spc, self.room_spc, self.c_highlight_nudge)

    def hover_bound(self):
        """
        Draws a bounding box around the area that we're hovering.  Only
        useful for debugging.
        """
        self.mapctx.set_source_rgba(1, 1, 1, 1)
        self.mapctx.set_line_width(1)
        self.mapctx.rectangle(self.h_x+0.5, self.h_y+0.5, self.h_w-1, self.h_h-1)
        self.mapctx.stroke()

    def clean_hover(self):
        """
        Cleans up any hovers which may be active
        """
        if (self.hover != self.HOVER_NONE):
            self.mapctx.save()
            self.mapctx.set_operator(cairo.OPERATOR_SOURCE)
            self.mapctx.rectangle(self.h_x, self.h_y, self.h_w, self.h_h)
            self.mapctx.set_source_surface(self.cleansurf, 0, 0)
            self.mapctx.fill()
            self.mapctx.restore()
            self.hover = self.HOVER_NONE
            self.curhover = None
            self.hover_roomobj = None
            self.hover_connobj = None

    def room_sort(self, room1, room2):
        """
        Function for sorting rooms
        """
        res = cmp(room1.name.lower(), room2.name.lower())
        if res == 0:
            res = cmp(room1.y, room2.y)
            if res == 0:
                res = cmp(room1.x, room2.x)
        return res

    def on_map_clicked(self, widget, event):
        """
        Handle clicks-n-such
        """

        # If these vars remain False, at the end of this function, we'll be
        # clearing out any transient vars that exist (such as moving a connection,
        # or doing a freeform link between rooms).  In practice this means that
        # a transient operation is never going to "span" any number of clicks.
        saved_move_vars = False
        saved_link_conn_vars = False

        # Left-click
        if (event.button == 1):

            if (self.hover == self.HOVER_NONE):
                # If we don't have anything selected, we'll drag the canvas
                self.dragging = True
                self.hold_x = event.x_root
                self.hold_y = event.y_root
                self.diff_x = 0
                self.diff_y = 0
                self.mainarea.window.set_cursor(self.cursor_move_drag)

            elif (event.type == gtk.gdk.BUTTON_PRESS):
                # Presumably this check was put here for a reason, though I don't recall why
                need_gfx_update = False

                if (self.hover == self.HOVER_ROOM):
                    # edit/view room details
                    self.new_to_dir_label.hide()
                    self.new_to_dir_align.hide()
                    self.new_conn_style_label.hide()
                    self.new_conn_style_align.hide()
                    self.new_conn_type_label.hide()
                    self.new_conn_type_align.hide()
                    self.new_group_with_label.hide()
                    self.new_group_with_align.hide()
                    self.room_group_label.show_all()
                    self.room_group_align.show_all()
                    room = self.curhover
                    if (self.readonly_lock.get_active()):
                        self.view_room_roomname_label.set_markup('<b>%s</b>' % gobject.markup_escape_text(room.name))
                        self.view_room_roomtype_label.set_text(room.TYPE_TXT[room.type])
                        if (room.up and room.up != ''):
                            self.view_room_up_label.set_text(room.up)
                            self.view_room_up_label.show()
                            self.view_room_up_hdr.show()
                        else:
                            self.view_room_up_label.hide()
                            self.view_room_up_hdr.hide()
                        if (room.down and room.down != ''):
                            self.view_room_down_label.set_text(room.down)
                            self.view_room_down_label.show()
                            self.view_room_down_hdr.show()
                        else:
                            self.view_room_down_label.hide()
                            self.view_room_down_hdr.hide()
                        if (room.door_in and room.door_in != ''):
                            self.view_room_in_label.set_text(room.door_in)
                            self.view_room_in_label.show()
                            self.view_room_in_hdr.show()
                        else:
                            self.view_room_in_label.hide()
                            self.view_room_in_hdr.hide()
                        if (room.door_out and room.door_out != ''):
                            self.view_room_out_label.set_text(room.door_out)
                            self.view_room_out_label.show()
                            self.view_room_out_hdr.show()
                        else:
                            self.view_room_out_label.hide()
                            self.view_room_out_hdr.hide()
                        if (room.notes and room.notes != ''):
                            self.view_room_notes_view.get_buffer().set_text(room.notes)
                            self.view_room_scroll.show()
                            self.view_room_notes_hdr.show()
                        else:
                            self.view_room_scroll.hide()
                            self.view_room_notes_hdr.hide()
                        self.view_room_dialog.run()
                        self.view_room_dialog.hide()
                        return
                    self.edit_room_label.set_markup('<b>Edit Room</b>')
                    self.roomname_entry.set_text(room.name)
                    self.roomnotes_view.get_buffer().set_text(room.notes)
                    if (room.type == Room.TYPE_HI_GREEN):
                        self.roomtype_radio_hi_green.set_active(True)
                    elif (room.type == Room.TYPE_HI_BLUE):
                        self.roomtype_radio_hi_blue.set_active(True)
                    elif (room.type == Room.TYPE_HI_RED):
                        self.roomtype_radio_hi_red.set_active(True)
                    elif (room.type == Room.TYPE_HI_YELLOW):
                        self.roomtype_radio_hi_yellow.set_active(True)
                    elif (room.type == Room.TYPE_HI_PURPLE):
                        self.roomtype_radio_hi_purple.set_active(True)
                    elif (room.type == Room.TYPE_HI_CYAN):
                        self.roomtype_radio_hi_cyan.set_active(True)
                    elif (room.type == Room.TYPE_LABEL):
                        self.roomtype_radio_label.set_active(True)
                    elif (room.type == Room.TYPE_FAINT):
                        self.roomtype_radio_faint.set_active(True)
                    elif (room.type == Room.TYPE_DARK):
                        self.roomtype_radio_dark.set_active(True)
                    else:
                        self.roomtype_radio_normal.set_active(True)
                    self.room_up_entry.set_text(room.up)
                    self.room_up_entry.set_position(0)
                    self.room_down_entry.set_text(room.down)
                    self.room_down_entry.set_position(0)
                    self.room_in_entry.set_text(room.door_in)
                    self.room_in_entry.set_position(0)
                    self.room_out_entry.set_text(room.door_out)
                    self.room_out_entry.set_position(0)
                    if (room.unexplored()):
                        self.roomname_entry.grab_focus()
                    else:
                        self.roomnotes_view.grab_focus()
                    buf = self.roomnotes_view.get_buffer()
                    buf.place_cursor(buf.get_start_iter())

                    # Advanced offsets
                    self.room_offset_x.set_active(room.offset_x)
                    self.room_offset_y.set_active(room.offset_y)

                    # Room dropdown for group membership
                    self.room_mapstore.clear()
                    iterator = self.room_mapstore.append()
                    rowmap = {}
                    self.room_mapstore.set(iterator,
                            self.ROOM_COL_NAME, '-',
                            self.ROOM_COL_IDX, -1)
                    currow = 0
                    self.room_group_box.set_active(0)
                    have_group = False
                    rooms = list(self.mapobj.roomlist())
                    rooms.sort(self.room_sort)
                    for iterroom in rooms:
                        if (room != iterroom):
                            currow += 1
                            rowmap[iterroom.idnum] = currow
                            iterator = self.room_mapstore.append()
                            self.room_mapstore.set(iterator,
                                    self.ROOM_COL_NAME, '<b>%s</b> <i>at (%d, %d)</i>' % (gobject.markup_escape_text(iterroom.name), iterroom.x+1, iterroom.y+1),
                                    self.ROOM_COL_IDX, iterroom.idnum)
                            if (not have_group and room.in_group_with(iterroom)):
                                self.room_group_box.set_active(currow)
                                have_group = True
                        else:
                            rowmap[iterroom.idnum] = 0

                    # TODO: should we poke around with scroll/cursor here?
                    result = self.edit_room_dialog.run()
                    self.edit_room_dialog.hide()
                    if (result == gtk.RESPONSE_OK):
                        if (room.name != self.roomname_entry.get_text()):
                            need_gfx_update = True
                            room.name = self.roomname_entry.get_text()
                        if (self.roomtype_radio_hi_green.get_active()):
                            new_type = Room.TYPE_HI_GREEN
                        elif (self.roomtype_radio_hi_red.get_active()):
                            new_type = Room.TYPE_HI_RED
                        elif (self.roomtype_radio_hi_blue.get_active()):
                            new_type = Room.TYPE_HI_BLUE
                        elif (self.roomtype_radio_hi_yellow.get_active()):
                            new_type = Room.TYPE_HI_YELLOW
                        elif (self.roomtype_radio_hi_purple.get_active()):
                            new_type = Room.TYPE_HI_PURPLE
                        elif (self.roomtype_radio_hi_cyan.get_active()):
                            new_type = Room.TYPE_HI_CYAN
                        elif (self.roomtype_radio_label.get_active()):
                            new_type = Room.TYPE_LABEL
                        elif (self.roomtype_radio_faint.get_active()):
                            new_type = Room.TYPE_FAINT
                        elif (self.roomtype_radio_dark.get_active()):
                            new_type = Room.TYPE_DARK
                        else:
                            new_type = Room.TYPE_NORMAL
                        if (room.type != new_type):
                            need_gfx_update = True
                            room.type = new_type
                        if (room.up != self.room_up_entry.get_text()):
                            need_gfx_update = True
                            room.up = self.room_up_entry.get_text()
                        if (room.down != self.room_down_entry.get_text()):
                            need_gfx_update = True
                            room.down = self.room_down_entry.get_text()
                        if (room.door_in != self.room_in_entry.get_text()):
                            need_gfx_update = True
                            room.door_in = self.room_in_entry.get_text()
                        if (room.door_out != self.room_out_entry.get_text()):
                            need_gfx_update = True
                            room.door_out = self.room_out_entry.get_text()
                        buftxt = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
                        if (room.notes != buftxt):
                            need_gfx_update = True
                            room.notes = buftxt

                        if (self.room_offset_x.get_active() != room.offset_x):
                            need_gfx_update = True
                            room.offset_x = self.room_offset_x.get_active()
                        if (self.room_offset_y.get_active() != room.offset_y):
                            need_gfx_update = True
                            room.offset_y = self.room_offset_y.get_active()

                        # Grouping
                        iterator = self.room_group_box.get_active_iter()
                        group_roomid = self.room_mapstore.get_value(iterator, self.ROOM_COL_IDX)
                        if (group_roomid == -1):
                            if room.group:
                                self.mapobj.remove_room_from_group(room)
                                need_gfx_update = True
                        else:
                            if (self.mapobj.group_rooms(room, self.mapobj.get_room(group_roomid))):
                                need_gfx_update = True

                        # Temp, report
                        #print('Existing Groups:')
                        #print('')
                        #for (idx, group) in enumerate(self.map.groups):
                        #    print('Group %d:' % (idx+1))
                        #    for room_view in group.rooms:
                        #        print(' * %s' % room_view.name)
                        #    print('')
                        #print('')

                elif (self.hover == self.HOVER_CONN_NEW):
                    # create a new room / connection
                    room = self.curhover[0]
                    direction = self.curhover[1]
                    coords = self.mapobj.dir_coord(room, direction)
                    if coords:
                        newroom = self.mapobj.get_room_at(*coords)
                        if newroom:
                            if (DIR_OPP[direction] not in newroom.conns):
                                self.mapobj.connect(room, direction, newroom)
                                need_gfx_update = True
                        else:
                            self.new_to_dir_label.show_all()
                            self.new_to_dir_align.show_all()
                            self.new_conn_style_label.show_all()
                            self.new_conn_style_align.show_all()
                            self.new_conn_type_label.show_all()
                            self.new_conn_type_align.show_all()
                            self.new_group_with_label.show_all()
                            self.new_group_with_align.show_all()
                            self.room_group_label.hide()
                            self.room_group_align.hide()
                            self.new_group_with_button.set_active(False)
                            self.new_to_dir_box.set_active(DIR_OPP[direction])
                            self.new_conn_type_pass_twoway.set_active(True)
                            self.new_conn_style_regular.set_active(True)
                            self.edit_room_label.set_markup('<b>New Room</b>')
                            self.roomname_entry.set_text('(unexplored)')
                            self.roomnotes_view.get_buffer().set_text('')
                            self.roomtype_radio_normal.set_active(True)
                            self.room_up_entry.set_text('')
                            self.room_down_entry.set_text('')
                            self.room_in_entry.set_text('')
                            self.room_out_entry.set_text('')
                            self.room_offset_x.set_active(room.offset_x)
                            self.room_offset_y.set_active(room.offset_y)
                            self.roomname_entry.grab_focus()
                            result = self.edit_room_dialog.run()
                            self.edit_room_dialog.hide()
                            if (result == gtk.RESPONSE_OK):
                                try:
                                    newroom = self.mapobj.add_room_at(coords[0], coords[1], self.roomname_entry.get_text())
                                except Exception as e:
                                    self.errordialog("Couldn't add room: %s" % (e))
                                    return
                                if (self.roomtype_radio_hi_green.get_active()):
                                    newroom.type = Room.TYPE_HI_GREEN
                                elif (self.roomtype_radio_hi_red.get_active()):
                                    newroom.type = Room.TYPE_HI_RED
                                elif (self.roomtype_radio_hi_blue.get_active()):
                                    newroom.type = Room.TYPE_HI_BLUE
                                elif (self.roomtype_radio_hi_yellow.get_active()):
                                    newroom.type = Room.TYPE_HI_YELLOW
                                elif (self.roomtype_radio_hi_purple.get_active()):
                                    newroom.type = Room.TYPE_HI_PURPLE
                                elif (self.roomtype_radio_hi_cyan.get_active()):
                                    newroom.type = Room.TYPE_HI_CYAN
                                elif (self.roomtype_radio_label.get_active()):
                                    newroom.type = Room.TYPE_LABEL
                                elif (self.roomtype_radio_faint.get_active()):
                                    newroom.type = Room.TYPE_FAINT
                                elif (self.roomtype_radio_dark.get_active()):
                                    newroom.type = Room.TYPE_DARK
                                else:
                                    newroom.type = Room.TYPE_NORMAL
                                newroom.up = self.room_up_entry.get_text()
                                newroom.down = self.room_down_entry.get_text()
                                newroom.door_in = self.room_in_entry.get_text()
                                newroom.door_out = self.room_out_entry.get_text()
                                buf = self.roomnotes_view.get_buffer()
                                newroom.notes = buf.get_text(buf.get_start_iter(), buf.get_end_iter())

                                # Connect the new room to the first room, if we haven't been told not to.
                                if not self.new_conn_style_none.get_active():
                                    new_direction = self.new_to_dir_box.get_active()
                                    newconn = self.mapobj.connect(room, direction, newroom, new_direction)
                                    if self.new_conn_type_pass_oneway_in.get_active():
                                        newconn.set_oneway_b()
                                    elif self.new_conn_type_pass_oneway_out.get_active():
                                        newconn.set_oneway_a()
                                    if self.new_conn_style_ladder.get_active():
                                        newconn.set_ladder(newroom, new_direction)
                                    elif self.new_conn_style_dotted.get_active():
                                        newconn.set_dotted(newroom, new_direction)

                                # Handle adding grouping if we've been told to, as well.
                                if self.new_group_with_button.get_active():
                                    self.mapobj.group_rooms(newroom, room)

                                # Handle offsets
                                if self.room_offset_x.get_active():
                                    newroom.offset_x = True
                                if self.room_offset_y.get_active():
                                    newroom.offset_y = True

                                # Temp, report
                                #print('Existing Groups:')
                                #print('')
                                #for (idx, group) in enumerate(self.map.groups):
                                #    print('Group %d:' % (idx+1))
                                #    for room_view in group.rooms:
                                #        print(' * %s' % room_view.name)
                                #    print('')
                                #print('')

                                need_gfx_update = True
                                if (len(self.mapobj.rooms) == 256):
                                    self.infodialog('Note: Currently this application can only support 256 rooms on each map.  You have just added the last one, so new rooms will no longer be available, unless you delete some existing ones.')

                elif (self.hover == self.HOVER_EDGE):
                    # move the room, if possible
                    room = self.curhover[0]
                    direction = self.curhover[1]
                    if (self.mapobj.move_room(room, direction)):
                        need_gfx_update = True

                else:
                    # Nothing...
                    pass

                if (need_gfx_update):
                    self.trigger_redraw()

        elif (event.button == 2):

            # Processing a middle click
            if (event.type == gtk.gdk.BUTTON_PRESS):
                need_gfx_update = False

                if (self.hover == self.HOVER_CONN_NEW):
                    # If we're hovering over a new connection, middle-click will
                    # create a loopback
                    room = self.curhover[0]
                    direction = self.curhover[1]
                    room.set_loopback(direction)
                    need_gfx_update = True

                if (need_gfx_update):
                    self.trigger_redraw()

        elif (event.button == 3):
            # Processing a right click

            if (event.type == gtk.gdk.BUTTON_PRESS):
                need_gfx_update = False

                # First check for a couple of "move" operations which we might be doing.
                if self.move_room is not None and self.move_dir is not None:
                    # We've received a previous "move connection" click, so process it now,
                    # so long as we're hovering over a new connection area
                    if self.hover == self.HOVER_CONN_NEW:
                        new_room = self.curhover[0]
                        new_dir = self.curhover[1]

                        # The logic for what's valid and what's not, here, was all moved into
                        # the actual data classes, in Connection.move_end().  Yay!
                        conn = self.move_room.get_conn(self.move_dir)
                        if conn.move_end(self.move_room, self.move_dir, new_room, new_dir):
                            need_gfx_update = True

                elif self.link_conn_room is not None and self.link_conn_dir is not None:
                    # We've received a previous "new connection" click, so process it now,
                    # so long as we're hoving over a new connection area
                    if (self.hover == self.HOVER_CONN_NEW):
                        new_room = self.curhover[0]
                        new_dir = self.curhover[1]

                        if new_room != self.link_conn_room:
                            self.mapobj.connect(self.link_conn_room, self.link_conn_dir, new_room, new_dir)
                            need_gfx_update = True

                # ... and at this point we're no longer looking for ongoing operations

                if (self.hover == self.HOVER_CONN):
                    # We're moving an existing connection
                    self.move_room = self.curhover[0]
                    self.move_dir = self.curhover[1]
                    saved_move_vars = True
                    self.set_secondary_status('Right-click to move connection')
                    # TODO: it would probably be nice to have some different GUI highlighting
                    # when this is active, as well.

                elif (self.hover == self.HOVER_CONN_NEW):
                    # We're adding a new connection in a free-form sort of way
                    self.link_conn_room = self.curhover[0]
                    self.link_conn_dir = self.curhover[1]
                    saved_link_conn_vars = True
                    self.set_secondary_status('Right-click to link to existing room')
                    # TODO: it would probably be nice to have some different GUI highlighting
                    # when this is active, as well.

                if (need_gfx_update):
                    self.trigger_redraw()

        self.reset_transient_operations(saved_move_vars, saved_link_conn_vars)

    def reset_transient_operations(self,
            saved_move_vars=False,
            saved_link_conn_vars=False,
            saved_add_extra_vars=False,
            saved_grouping_vars=False,
            ):
        """
        We have four "transient" operations: moving existing connections, linking
        two previously-unlinked directions between rooms, adding an extra end
        to a connection, and grouping two rooms.  This will reset all the
        necessary vars.
        """

        if not saved_move_vars:
            self.move_room = None
            self.move_dir = None
        if not saved_link_conn_vars:
            self.link_conn_room = None
            self.link_conn_dir = None
        if not saved_add_extra_vars:
            self.add_extra_room = None
            self.add_extra_dir = None
        if not saved_grouping_vars:
            self.grouping_room = None
        if (not saved_move_vars and not saved_link_conn_vars and
                not saved_add_extra_vars and not saved_grouping_vars):
            self.set_secondary_status('')

    def trigger_redraw(self, clean_hover=True):
        """
        Things that need to be done when the map is redrawn
        """
        if clean_hover:
            self.clean_hover()
        self.draw()
        self.mainarea.queue_draw()
        if not clean_hover:
            self.redraw_current_hover()

    def on_map_released(self, widget, event):
        """
        What to do when the mouse button lifts.  No effect unless we're dragging.
        """
        if self.dragging:
            self.dragging = False
            self.mainarea.window.set_cursor(None)

    def redraw_current_hover(self):
        """
        Called after some redraws to make sure that we remain highlighting
        our current hover.
        """
        if self.hover == self.HOVER_ROOM:
            self.hover_room()
        elif self.hover == self.HOVER_CONN:
            self.hover_conn(self.c_highlight_del)
        elif self.hover == self.HOVER_CONN_NEW:
            self.hover_conn()
        elif self.hover == self.HOVER_EDGE:
            self.hover_edge()

    def update_hover_text(self):
        """
        Updates our hover text which tells the user what actions are available.
        """

        # Look to see if we're in readonly mode
        readonly = self.readonly_lock.get_active()

        hover_text = ''

        if self.hover == self.HOVER_NONE:

            hover_text = 'LMB: click-and-drag'

        else:

            if self.hover_roomobj:

                prefix = '(%d, %d)' % (self.hover_roomobj.x+1, self.hover_roomobj.y+1)
                actions = []

                if self.hover == self.HOVER_ROOM:
                    if readonly:
                        actions.append(('LMB', 'view details'))
                    else:
                        actions.append(('LMB', 'edit room'))
                        actions.append(('WASD', 'nudge room'))
                        actions.append(('X', 'delete'))
                        actions.append(('H/V', 'toggle horiz/vert offset'))
                        actions.append(('T', 'change type'))
                        if self.hover_roomobj.group:
                            actions.append(('G', 'change group render'))
                            actions.append(('O', 'remove from group'))
                        else:
                            actions.append(('G', 'add to group'))

                elif self.hover == self.HOVER_CONN:
                    if not readonly:
                        if self.hover_roomobj.get_loopback(self.curhover[1]):
                            actions.append(('C', 'remove loopback'))
                        else:
                            actions.append(('RMB', 'move connection'))
                            actions.append(('C', 'remove connection'))
                            actions.append(('E', 'add extra'))
                            actions.append(('T', 'type'))
                            actions.append(('P', 'path'))
                            actions.append(('O', 'orientation'))
                            actions.append(('L', 'stub length'))
                            if self.hover_connobj:
                                if self.hover_connobj.symmetric:
                                    actions.append(('S', 'symmetric OFF'))
                                else:
                                    actions.append(('S', 'symmetric ON'))
                                if not self.hover_connobj.is_primary(self.hover_roomobj, self.curhover[1]):
                                    actions.append(('R', 'set primary'))
                            else:
                                    actions.append(('S', 'symmetric'))

                elif self.hover == self.HOVER_CONN_NEW:
                    if not readonly:
                        actions.append(('LMB', 'new room'))
                        actions.append(('RMB', 'new connection'))
                        actions.append(('MMB', 'new loopback'))

                elif self.hover == self.HOVER_EDGE:
                    if not readonly:
                        actions.append(('LMB', 'nudge room'))

                if len(actions) == 0:
                    hover_text = prefix
                else:
                    hover_text = '%s - %s' % (prefix, ', '.join(['%s: %s' % (key, action) for (key, action) in actions]))

        self.set_hover(hover_text)

    def on_mouse_changed(self, widget, event):
        """
        Track mouse changes
        """

        if not self.initgfx:
            return
        if self.dragging:
            diff_x = self.hold_x - event.x_root
            diff_y = self.hold_y - event.y_root
            if (diff_x != 0):
                adjust = self.mainscroll.get_hadjustment()
                newvalue = adjust.get_value() + diff_x
                if (newvalue < adjust.lower):
                    newvalue = adjust.lower
                elif (newvalue > adjust.upper-adjust.page_size):
                    newvalue = adjust.upper-adjust.page_size
                adjust.set_value(newvalue)
            if (diff_y != 0):
                adjust = self.mainscroll.get_vadjustment()
                newvalue = adjust.get_value() + diff_y
                if (newvalue < adjust.lower):
                    newvalue = adjust.lower
                elif (newvalue > adjust.upper-adjust.page_size):
                    newvalue = adjust.upper-adjust.page_size
                adjust.set_value(newvalue)
            self.hold_x = event.x_root
            self.hold_y = event.y_root
            return

        # Look to see if we're in readonly mode
        readonly = self.readonly_lock.get_active()

        # Figure out if we're hoving over anything
        pixel_offset = int((self.mmsurf.get_stride() * event.y) + (event.x*4))
        if (event.y > self.area_y or event.x > self.area_x):
            hoverpixel = (0, 0, 0, 0)
        else:
            hoverpixel = unpack('BBBB', self.mmdata[pixel_offset:pixel_offset+4])
        if (hoverpixel[2] != 0):
            # TODO: Visualization for mouseovers on these
            typeidx = hoverpixel[2]
            room = self.mapobj.get_room(hoverpixel[0])
            if (typeidx == self.HOVER_ROOM):
                if (self.hover != self.HOVER_ROOM or self.curhover != room):
                    self.clean_hover()
                    self.hover = self.HOVER_ROOM
                    self.curhover = room
                    self.hover_roomobj = room
                    self.hover_room()
                    self.mainarea.queue_draw()
            elif (typeidx == self.HOVER_CONN or typeidx == self.HOVER_CONN_NEW):
                if not readonly:
                    conn = (room, hoverpixel[1])
                    if (self.hover != self.HOVER_CONN or self.curhover[0] != conn[0] or self.curhover[1] != conn[1]):
                        self.clean_hover()
                        self.hover = typeidx
                        self.curhover = conn
                        self.hover_roomobj = room
                        self.hover_connobj = self.curhover[0].get_conn(self.curhover[1])
                        if (self.hover == self.HOVER_CONN_NEW):
                            self.hover_conn()
                        else:
                            self.hover_conn(self.c_highlight_del)
                        self.mainarea.queue_draw()
            elif (typeidx == self.HOVER_EDGE):
                if not readonly:
                    edge = (room, hoverpixel[1])
                    if (self.hover != self.HOVER_EDGE or self.curhover[0] != edge[0] or self.curhover[1] != edge[1]):
                        self.clean_hover()
                        self.hover = self.HOVER_EDGE
                        self.curhover = edge
                        self.hover_roomobj = room
                        self.hover_edge()
                        self.mainarea.queue_draw()
            else:
                raise Exception("Invalid R code in bit mousemap")
        else:
            self.clean_hover()
            self.mainarea.queue_draw()

        self.update_hover_text()

    def key_handler(self, widget, event):
        """
        Handles keypresses
        """
        # Currently all of our keypresses edit data, so we can return right away
        # if we're in readonly mode
        if self.readonly_lock.get_active():
            return

        # If these vars remain False, at the end of this function, we'll be
        # clearing out any transient vars that exist (such as moving a connection,
        # or doing a freeform link between rooms).  In practice this means that
        # a transient operation is never going to "span" any number of clicks.
        saved_add_extra_vars = False
        saved_grouping_vars = False

        if (event.keyval < 256 and (event.state & self.keymask) == 0):
            key = chr(event.keyval).lower()

            if self.hover == self.HOVER_ROOM:
                if (key == 'x'):
                    if (len(self.mapobj.rooms) < 2):
                        self.errordialog('You cannot remove the last room from a map', self.window)
                        return
                    self.mapobj.del_room(self.curhover)
                    self.trigger_redraw()
                elif (key == 'g'):
                    room = self.curhover
                    if self.grouping_room is not None:
                        if self.mapobj.group_rooms(room, self.grouping_room):
                            self.trigger_redraw(False)
                            self.update_hover_text()
                    elif room.group is None:
                        self.grouping_room = room
                        saved_grouping_vars = True
                        self.set_secondary_status('G again to add to a group')
                    else:
                        room.group.increment_style()
                        self.trigger_redraw(False)
                elif (key == 'o'):
                    if self.mapobj.remove_room_from_group(self.curhover):
                        self.trigger_redraw(False)
                        self.update_hover_text()
                elif (key == 'h'):
                    self.curhover.offset_x = not self.curhover.offset_x
                    self.trigger_redraw()
                elif (key == 'v'):
                    self.curhover.offset_y = not self.curhover.offset_y
                    self.trigger_redraw()
                elif (key == 't'):
                    self.curhover.increment_type()
                    self.trigger_redraw(False)
                elif (key == 'w'):
                    self.mapobj.move_room(self.curhover, DIR_N)
                    self.trigger_redraw(True)
                elif (key == 'a'):
                    self.mapobj.move_room(self.curhover, DIR_W)
                    self.trigger_redraw(True)
                elif (key == 's'):
                    self.mapobj.move_room(self.curhover, DIR_S)
                    self.trigger_redraw(True)
                elif (key == 'd'):
                    self.mapobj.move_room(self.curhover, DIR_E)
                    self.trigger_redraw(True)

            elif self.hover == self.HOVER_CONN:
                room = self.curhover[0]
                conn_dir = self.curhover[1]
                conn = room.get_conn(conn_dir)
                if conn:
                    end = conn.get_end(room, conn_dir)
                    if (key == 'c'):
                        self.mapobj.detach(room, conn_dir)
                        self.trigger_redraw(True)
                    elif (key == 'p'):
                        conn.cycle_render_type(room, conn_dir)
                        self.trigger_redraw(False)
                    elif (key == 'l'):
                        conn.increment_stub_length(room, conn_dir)
                        self.trigger_redraw(False)
                    elif (key == 't'):
                        conn.cycle_conn_type(room, conn_dir)
                        self.trigger_redraw(False)
                    elif (key == 'o'):
                        conn.cycle_passage()
                        self.trigger_redraw(False)
                    elif (key == 's'):
                        conn.toggle_symmetric(room=room, direction=conn_dir)
                        self.update_hover_text()
                        self.trigger_redraw(False)
                    elif (key == 'r'):
                        # Technically this option isn't displayed most of the time, but it
                        # won't hurt anything if it's triggered whenever, since it'd generally
                        # be a no-op.
                        conn.set_primary(room, conn_dir)
                        self.update_hover_text()
                        self.trigger_redraw(False)
                    elif (key == 'e'):
                        if self.add_extra_room is None or self.add_extra_dir is None:
                            self.add_extra_room = self.curhover[0]
                            self.add_extra_dir = self.curhover[1]
                            saved_add_extra_vars = True
                            self.set_secondary_status('E to add an extra connection to the same room')
                else:

                    # Must be a loopback instead.
                    if (key == 'c'):
                        self.mapobj.detach(room, conn_dir)
                        self.trigger_redraw(True)

            elif self.hover == self.HOVER_CONN_NEW:
                room = self.curhover[0]
                conn_dir = self.curhover[1]
                if (key == 'e'):
                    if self.add_extra_room is not None and self.add_extra_dir is not None:
                        conn = self.add_extra_room.get_conn(self.add_extra_dir)
                        try:
                            conn.connect_extra(room, conn_dir)
                        except Exception as e:
                            pass
                        self.trigger_redraw(True)

        self.reset_transient_operations(saved_add_extra_vars=saved_add_extra_vars,
                saved_grouping_vars=saved_grouping_vars)

    def nudge_lock_toggled(self, widget):
        """
        Things to do when our nudge lock is toggled on/off.
        """

        # Trigger a redraw if we have to
        if (not self.readonly_lock.get_active()):
            self.trigger_redraw()

    def grid_display_toggled(self, widget):
        """
        Tasks to perform when we've toggled our map grid.  (Just trigger a redraw
        is all.)
        """
        self.trigger_redraw()

    def readonly_toggled(self, widget):
        """
        Tasks to perform when we've toggled into readonly mode.
        """

        # Loop through our nudge/resize buttons and set them as active or not,
        # depending on our status
        if self.readonly_lock.get_active():
            button_status = False
        else:
            button_status = True
        for widget in self.nudge_buttons + self.resize_buttons + [self.nudge_lock]:
            widget.set_sensitive(button_status)

        # I think that I'd originally done this to try and have the lock icon image
        # get a dark background just like the Button does (or at least, whatever the
        # appropriate color is).  It looks like we're specifying the color incorrectly
        # though; the call to pixbuf.composite_color_simple raises:
        #   TypeError: Gdk.Pixbuf.composite_color_simple() argument 6 must be an integer, not gtk.gdk.Color
        # ... I *think* that this probably has something to do with colormaps; rather
        # than specifying a color, I bet the integer is an index within the colormap
        # rather than a color specification itself.  Anyway, just commenting it out.
        # I expect I'll never bother fixing this.

        # Update our image if need be
        #if self.readonly_lock.get_active():
        #    color = self.readonly_lock.get_style().bg[gtk.STATE_ACTIVE]
        #    image = self.readonly_lock.child
        #    pixbuf = image.get_pixbuf()
        #    pixbuf = pixbuf.composite_color_simple(pixbuf.get_property('width'),
        #            pixbuf.get_property('height'), gtk.gdk.INTERP_NEAREST,
        #            255, 128, color, color)
        #    image.set_from_pixbuf(pixbuf)

        # Trigger a redraw if our graphics have been initialized
        if self.initgfx:
            self.trigger_redraw()

    def nudge_map(self, widget):
        """
        Handles getting a signal to nudge the map in a given direction
        """
        (nudge, dir_txt) = widget.name.split('_', 2)
        direction = TXT_2_DIR[dir_txt]
        if (self.mapobj.nudge(direction)):
            self.trigger_redraw()

    def edit_room_activate(self, widget):
        """
        Handles the user hitting Enter while doing a room name
        """
        self.edit_room_ok.activate()

    def edit_game_activate(self, widget):
        """
        Handles the user hitting Enter while doing a game name
        """
        self.edit_game_ok.activate()

    def new_map_activate(self, widget):
        """
        Handles the user hitting Enter while creating a new map
        """
        self.new_map_ok.activate()

    def map_combo_changed(self, widget):
        """
        Handles switching to a different map
        """
        if (self.initgfx and not self.updating_gameinfo):
            self.map_idx = self.map_combo.get_active()
            self.mapobj = self.game.maps[self.map_idx]
            self.update_title()
            self.trigger_redraw()

    def edit_game(self, widget):
        """
        Calls the game edit screen
        """

        self.gamename_entry.set_text(self.game.name)

        self.mapstore.clear()
        for (idx, mapobj) in enumerate(self.game.maps):
            iterator = self.mapstore.append()
            self.mapstore.set(iterator,
                    self.MAP_COL_TEXT, mapobj.name,
                    self.MAP_COL_EDIT, True,
                    self.MAP_COL_CURIDX, idx,
                    self.MAP_COL_ROOMS, len(mapobj.rooms),
                    self.MAP_COL_ROOMEDIT, False)

        # ... and update GUI components as needed
        self.update_mapremove_button()

        # Now actually run the dialog
        result = self.edit_game_dialog.run()
        self.edit_game_dialog.hide()
        if (result == gtk.RESPONSE_OK):
            # First update our game name
            self.game.name = self.gamename_entry.get_text()

            # Now process any changes to the map list
            newmaps = []
            iterator = self.mapstore.get_iter_first()
            new_map_idx = 0
            found_cur_map = False
            while (iterator):
                mapname = self.mapstore.get_value(iterator, self.MAP_COL_TEXT)
                curidx = self.mapstore.get_value(iterator, self.MAP_COL_CURIDX)
                if (curidx == -1):
                    newmaps.append(self.create_new_map(mapname))
                else:
                    if (curidx == self.map_idx):
                        new_map_idx = len(newmaps)
                        found_cur_map = True
                    self.game.maps[curidx].name = mapname
                    newmaps.append(self.game.maps[curidx])
                iterator = self.mapstore.iter_next(iterator)
            self.game.replace_maps(newmaps)

            # Update our currently-selected map
            self.map_idx = new_map_idx
            self.mapobj = self.game.maps[self.map_idx]

            # And now update our map dropdown
            self.update_gameinfo()
            
            # ... and finally update our graphics if our current map changed
            if not found_cur_map:
                self.trigger_redraw()

    def update_mapremove_button(self):
        """
        Activates or deactivates the Remove Map button, as-needed.
        """
        if (len(self.mapstore) < 2):
            self.edit_game_map_remove_button.set_sensitive(False)
        else:
            self.edit_game_map_remove_button.set_sensitive(True)

    def map_add(self, widget):
        """
        Adds a new map
        """
        self.new_map_entry.set_text('New Map')
        self.new_map_entry.grab_focus()
        result = self.new_map_dialog.run()
        self.new_map_dialog.hide()
        if (result == gtk.RESPONSE_OK):
            if (self.new_map_entry.get_text() == ''):
                self.errordialog('You must specify a name for the new map', self.edit_game_dialog)
                return
            iterator = self.mapstore.append()
            self.mapstore.set(iterator,
                    self.MAP_COL_TEXT, self.new_map_entry.get_text(),
                    self.MAP_COL_EDIT, True,
                    self.MAP_COL_CURIDX, -1,
                    self.MAP_COL_ROOMS, 0,
                    self.MAP_COL_ROOMEDIT, False)
            self.update_mapremove_button()

    def map_remove(self, widget):
        """
        Removes a map
        """
        if (len(self.mapstore) < 2):
            self.errordialog('You cannot delete the last map', self.edit_game_dialog)
            return
        sel = self.map_treeview.get_selection()
        model, iterator = sel.get_selected()

        if iterator:
            roomcount = model.get_value(iterator, self.MAP_COL_ROOMS)
            if (roomcount > 0):
                res = self.confirmdialog('If you delete this map, all rooms will be removed with it.  Are you sure you want to continue?', self.edit_game_dialog)
                if (res != gtk.RESPONSE_YES):
                    return
            idx = model.get_path(iterator)[0]
            model.remove(iterator)
            self.update_mapremove_button()

    def on_mapname_edited(self, cell, path_string, new_text, model):
        """
        Handle a map name being changed via our Game Edit screen
        """
        if (new_text == ''):
            self.errordialog('Map must have a name', self.edit_game_dialog)
            return
        iterator = model.get_iter_from_string(path_string)
        path = model.get_path(iterator)[0]
        column = cell.get_data('column')

        if (column == 0):
            model.set(iterator, column, new_text)

    def open_notes(self, widget, allmaps=False):
        """
        Open up our notes window
        """
        if allmaps:
            maplist = self.game.maps
            self.notes_window.set_title('Room Notes (for all maps)')
        else:
            maplist = [self.mapobj]
            self.notes_window.set_title('Room Notes (for %s)' % (self.mapobj.name))

        # First loop through to find out what notes we have
        notes = {}
        for (idx, mapobj) in enumerate(maplist):
            notes[idx] = {}
            for room in mapobj.roomlist():
                if (room and room.notes and room.notes != ''):
                    notes[idx][room.idnum] = room.notes

        # ... and now report
        buff = self.global_notes_view.get_buffer()
        buff.set_text('')
        have_notes = False
        end = buff.get_end_iter()
        buff.insert(end, "\n")
        for (idx, rooms) in notes.items():
            if (len(rooms) > 0):
                have_notes = True
                buff.insert_with_tags_by_name(end, 'Notes for %s' % (maplist[idx].name), 'mapheader')
                buff.insert(end, "\n\n")
                for (idnum, notes) in rooms.items():
                    room = maplist[idx].get_room(idnum)
                    buff.insert_with_tags_by_name(end, room.name, 'roomheader')
                    buff.insert_with_tags_by_name(end, ' at (%d, %d)' % (room.x+1, room.y+1), 'coords')
                    buff.insert(end, "\n")
                    buff.insert_with_tags_by_name(end, notes, 'notes')
                    buff.insert(end, "\n\n")
        if not have_notes:
            buff.insert_with_tags_by_name(end, "\n\n\n(no notes)", 'nonotes')

        self.notes_window.show()
    
    def open_notes_all(self, widget):
        """
        Open up our notes window, with all maps
        """
        self.open_notes(widget, True)

    def on_notes_close(self, widget, event=None):
        """
        When we close our Notes View window
        """
        self.notes_window.hide()
        return True

    def map_resize(self, widget):
        """
        Resizes the map, if possible
        """
        (resize, dir_txt) = widget.name.split('_', 2)
        direction = TXT_2_DIR[dir_txt]
        if (self.mapobj.resize(direction)):
            self.trigger_redraw()

    def draw_offset_toggle(self, widget):
        """
        What to do when the user's toggled the drawing of offsets
        """
        self.trigger_redraw()

    def duplicate_map(self, widget):
        """
        Duplicates the current map
        """
        self.new_map_dialog_title.set_markup('<b>Duplicate Map</b>')
        transbak = self.new_map_dialog.get_transient_for()
        self.new_map_dialog.set_transient_for(self.window)
        self.new_map_entry.set_text('%s (copy)' % self.mapobj.name)
        self.new_map_entry.grab_focus()
        result = self.new_map_dialog.run()
        self.new_map_dialog.hide()
        self.new_map_dialog_title.set_markup('<b>New Map</b>')
        self.new_map_dialog.set_transient_for(transbak)
        if (result == gtk.RESPONSE_OK):
            if (self.new_map_entry.get_text() == ''):
                self.errordialog('You must specify a name for the new map', self.window)
                return
            newmap = self.mapobj.duplicate(self.new_map_entry.get_text())
            self.game.add_map_obj(newmap)
            self.update_gameinfo()

    def export_image(self, widget):
        """
        Exports the current image to a PNG
        """
    def export_image(self, widget=None):
        """ Used to export a PNG of the current map image to disk. """

        # Create the dialog
        dialog = gtk.FileChooserDialog('Export Image...', None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_transient_for(self.window)
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_do_overwrite_confirmation(True)
        infolabel = gtk.Label()
        infolabel.set_markup('<b>Note:</b> Only PNG images are supported.  If you name your export something other than .png, it will still be a PNG image.')
        infolabel.set_line_wrap(True)
        dialog.set_extra_widget(infolabel)
        if (self.curfile != None):
            path = os.path.dirname(os.path.realpath(self.curfile))
            if (path != ''):
                dialog.set_current_folder(path)

        fil = gtk.FileFilter()
        fil.set_name("PNG Files")
        fil.add_pattern("*.png")
        dialog.add_filter(fil)

        # Run the dialog and process its return values
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            self.cleansurf.write_to_png(filename)
            self.set_status('Image exported to %s' % (filename))
            self.set_delayed_edit()

        # Clean up
        dialog.destroy()

