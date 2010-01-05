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

import os.path
import gtk
import gtk.gdk
import gtk.glade
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

    def __init__(self):

        # Make sure to dampen signals if we need to
        self.initgfx = False

        # Initial Glade setup
        self.gladefile = self.resfile('main.glade')
        self.wtree = gtk.glade.XML(self.gladefile)
        self.window = self.wtree.get_widget('mainwindow')
        self.mainscroll = self.wtree.get_widget('mainscroll')
        self.mainarea = self.wtree.get_widget('mainarea')
        self.titlelabel = self.wtree.get_widget('titlelabel')
        self.hoverlabel = self.wtree.get_widget('hoverlabel')
        self.map_combo = self.wtree.get_widget('map_combo')
        self.nudge_lock = self.wtree.get_widget('nudge_lock')
        self.menu_revert = self.wtree.get_widget('menu_revert')
        self.statusbar = self.wtree.get_widget('statusbar')
        self.sbcontext = self.statusbar.get_context_id('Main Messages')
        self.aboutwindow = None

        # New Room / Edit Room dialog
        self.edit_room_dialog = self.wtree.get_widget('edit_room_dialog')
        self.edit_room_label = self.wtree.get_widget('edit_room_label')
        self.roomtype_radio_normal = self.wtree.get_widget('roomtype_radio_normal')
        self.roomtype_radio_entrance = self.wtree.get_widget('roomtype_radio_entrance')
        self.roomtype_radio_label = self.wtree.get_widget('roomtype_radio_label')
        self.roomname_entry = self.wtree.get_widget('roomname_entry')
        self.room_up_entry = self.wtree.get_widget('room_up_entry')
        self.room_down_entry = self.wtree.get_widget('room_down_entry')
        self.roomnotes_view = self.wtree.get_widget('roomnotes_view')
        self.edit_room_ok = self.wtree.get_widget('edit_room_ok')
        self.edit_room_cancel = self.wtree.get_widget('edit_room_cancel')

        # Edit Game dialog
        self.edit_game_dialog = self.wtree.get_widget('edit_game_dialog')
        self.gamename_entry = self.wtree.get_widget('gamename_entry')
        self.map_treeview = self.wtree.get_widget('map_treeview')
        self.edit_game_ok = self.wtree.get_widget('edit_game_ok')
        self.edit_game_cancel = self.wtree.get_widget('edit_game_cancel')
        self.edit_game_map_add_button = self.wtree.get_widget('edit_game_map_add_button')
        self.edit_game_map_remove_button = self.wtree.get_widget('edit_game_map_remove_button')

        # New Map dialog
        self.new_map_dialog = self.wtree.get_widget('new_map_dialog')
        self.new_map_entry = self.wtree.get_widget('new_map_entry')
        self.new_map_ok = self.wtree.get_widget('new_map_ok')

        # Notes view window
        self.notes_window = self.wtree.get_widget('notes_window')
        self.global_notes_view = self.wtree.get_widget('global_notes_view')

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
                'edit_room_activate': self.edit_room_activate,
                'map_combo_changed': self.map_combo_changed,
                'edit_game': self.edit_game,
                'edit_game_activate': self.edit_game_activate,
                'map_add': self.map_add,
                'map_remove': self.map_remove,
                'new_map_activate': self.new_map_activate,
                'open_notes': self.open_notes,
                'open_notes_all': self.open_notes_all
            }
        self.wtree.signal_autoconnect(dic)

        # Pango contexts for rendering text
        self.pangoctx = self.window.get_pango_context()
        self.room_layout = pango.Layout(self.pangoctx)
        self.room_layout.set_font_description(pango.FontDescription('sans normal 7'))

        # State vars
        self.dragging = False
        self.hover = self.HOVER_NONE
        self.curhover = None
        self.cursor_move_drag = gtk.gdk.Cursor(gtk.gdk.DOT)

        # Sizing information
        # TODO: Should really figure out zooming sooner rather than later
        # Note that our max total rooms is 255, because of how our mousemaps
        # work.  If we have a square map, that means that it's 15x15
        self.room_w = 110
        self.room_h = 110
        self.room_spc = 30
        self.room_spc_h = self.room_spc/2
        self.rooms_x = 9
        self.rooms_y = 9
        self.area_x = self.room_w*self.rooms_x + self.room_spc*(self.rooms_x+1)
        self.area_y = self.room_h*self.rooms_y + self.room_spc*(self.rooms_y+1)
        self.mainarea.set_size_request(self.area_x, self.area_y)

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
        self.create_new_game()

        # Set the game name and level dropdown
        self.updating_gameinfo = False
        self.update_gameinfo()

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
            text = '<i>%s</i>' % (text)
        self.hoverlabel.set_markup(text)

    def set_status(self, text):
        """
        Pushes some text out to our status bar
        """
        self.statusbar.push(self.sbcontext, text)

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
                if not self.load_from_file(dialog.get_filename()):
                    self.errordialog('Unable to open file.', dialog)
                    rundialog = True

        dialog.destroy()
        return True

    def on_revert(self, widget=None):
        """
        Revert
        """
        # TODO: grey out Revert until we've actually loaded
        if (self.curfile):
            if self.load_from_file(self.curfile):
                self.set_delayed_edit()
                self.set_status('Reverted to on-disk copy of %s' % self.curfile)
            else:
                self.errordialog('Unable to revert, error in on-disk file.')
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
        self.map = self.create_new_map('Starting Map')
        self.map_idx = self.game.add_map_obj(self.map)
        self.cancel_delayed_status()
        self.set_status('Editing a new game')
        if (self.initgfx):
            self.update_gameinfo()
            self.trigger_redraw()

    def load_from_file(self, filename):
        """
        Loads a game from a file
        """
        try:
            game = Game.load(filename)
            self.menu_revert.set_sensitive(True)
            self.game = game
            self.map = self.game.maps[0]
            self.map_idx = 0
            self.curfile = filename
            if (self.initgfx):
                self.update_gameinfo()
                self.trigger_redraw()
            self.cancel_delayed_status()
            self.set_status('Editing %s' % filename)
            return True
        except Exception:
            return False

    def update_title(self):
        """
        Updates our game/map name display
        """
        self.titlelabel.set_markup('<b>%s</b> | %s' % (self.game.name, self.map.name))

    def update_gameinfo(self):
        """
        Updates our game name and level dropdown
        """
        self.updating_gameinfo = True
        self.update_title()
        self.map_combo.get_model().clear()
        for map in self.game.maps:
            self.map_combo.append_text(map.name)
        self.map_combo.set_active(self.map_idx)
        self.updating_gameinfo = False

    def room_xy(self, room):
        """
        Returns a tuple with (x, y) starting coordinates for the given room
        """
        x = self.room_spc + (self.room_w+self.room_spc)*room.x
        y = self.room_spc + (self.room_h+self.room_spc)*room.y
        return (x, y)

    def create_new_map(self, name):
        """
        Creates our default new map, with a single room in the center
        """
        map = Map(name)
        room = map.add_room_at(4, 4, 'Starting Room')
        room.type = Room.TYPE_ENTRANCE
        return map

    def draw_room(self, room, ctx, mmctx):
        """
        Draws a room onto the given context (and mousemap ctx)
        """
        # Starting position of room
        (x, y) = self.room_xy(room)

        # Rooms with a name of "(unexplored)" become labels, effectively.
        # So that's what we're doing here.
        if (room.type == Room.TYPE_LABEL or room.unexplored()):
            is_label = True
        else:
            is_label = False

        # Draw the box
        ctx.save()
        if (not is_label):
            ctx.set_source_rgba(*self.c_room_background)
            ctx.rectangle(x, y, self.room_w, self.room_h)
            ctx.fill()
        if (is_label):
            ctx.set_source_rgba(*self.c_label)
            ctx.set_dash([9.0], 0)
        elif (room.type == Room.TYPE_ENTRANCE):
            ctx.set_source_rgba(*self.c_entrance)
        else:
            ctx.set_source_rgba(*self.c_borders)
        ctx.set_line_width(1)
        ctx.rectangle(x, y, self.room_w, self.room_h)
        ctx.stroke()
        ctx.restore()

        # Mousemap room box
        mmctx.set_source_rgba(self.m_step*self.HOVER_ROOM, 0, self.m_step*room.id)
        mmctx.rectangle(x, y, self.room_w, self.room_h)
        mmctx.fill()

        # Now also draw connections off of the room
        for (dir, conn) in enumerate(room.conns):
            if conn:
                (conn_x, conn_y) = self.room_xy(conn)
                x1 = x+self.CONN_OFF[dir][0]
                y1 = y+self.CONN_OFF[dir][1]
                x2 = conn_x+self.CONN_OFF[DIR_OPP[dir]][0]
                y2 = conn_y+self.CONN_OFF[DIR_OPP[dir]][1]

                ctx.set_source_rgba(*self.c_borders)
                ctx.set_line_width(1)
                ctx.move_to(x1, y1)
                ctx.line_to(x2, y2)
                ctx.stroke()

                conn_hover = self.HOVER_CONN
            else:
                conn_hover = self.HOVER_CONN_NEW

            # Draw the mousemap too, though only if we Should
            if ((room.y == 0 and dir in [DIR_NW, DIR_N, DIR_NE]) or
                (room.y == self.map.h-1 and dir in [DIR_SW, DIR_S, DIR_SE]) or
                (room.x == 0 and dir in [DIR_NW, DIR_W, DIR_SW]) or
                (room.x == self.map.w-1 and dir in [DIR_NE, DIR_E, DIR_SE])):
                continue
            mmctx.set_source_rgba(self.m_step*conn_hover, self.m_step*dir, self.m_step*room.id)
            mmctx.rectangle(x+self.CONN_H_OFF[dir][0], y+self.CONN_H_OFF[dir][1], self.room_spc, self.room_spc)
            mmctx.fill()

        # Mousemap edges
        if (not self.nudge_lock.get_active()):
            for (dir, junk) in enumerate(DIR_OPP):
                coords = self.map.dir_coord(room, dir)
                if coords:
                    if (not self.map.get_room_at(*coords)):
                        mmctx.set_source_rgba(self.m_step*self.HOVER_EDGE, self.m_step*dir, self.m_step*room.id)
                        mmctx.rectangle(x+self.EDGE_OFF[dir][0], y+self.EDGE_OFF[dir][1], self.room_spc, self.room_spc)
                        mmctx.fill()

        if (is_label):
            label_layout = pango.Layout(self.pangoctx)
            label_layout.set_markup('<i>%s</i>' % (room.name))
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
            ctx.set_source_rgba(*self.c_text)
            pangoctx = pangocairo.CairoContext(ctx)
            pangoctx.show_layout(label_layout)
        else:
            # Draw the room title
            title_layout = pango.Layout(self.pangoctx)
            title_layout.set_markup(room.name)
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
            ctx.set_source_rgba(*self.c_text)
            pangoctx = pangocairo.CairoContext(ctx)
            pangoctx.show_layout(title_layout)

            # ... show "notes" identifier
            if (room.notes and room.notes != ''):
                ctx.move_to(x+self.notes_layout_x_off, y+self.notes_layout_y_off)
                ctx.set_source_rgba(*self.c_text)
                pangoctx.show_layout(self.notes_layout)

            # ... and any up/down arrows
            # TODO: some magic numbers in here
            icon_txt_spc = 3
            icon_dim = self.ladder_up_surf.get_width()
            cur_y = y + self.notes_layout_y_bottom + 7
            cur_x = x+(self.room_w-icon_dim)/2
            max_w = self.room_w - self.room_spc - icon_dim - icon_txt_spc
            max_h = icon_dim + 4
            for (label, graphic) in [(room.up, self.ladder_up_surf), (room.down, self.ladder_down_surf)]:
                if (label and label != ''):
                    layout = pango.Layout(self.pangoctx)
                    text = label
                    width = 999
                    height = 999
                    chars = 15
                    while (width > max_w or height > max_h):
                        layout.set_markup(text)
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
                    ctx.set_source_surface(graphic, ladder_x, cur_y)
                    ctx.move_to(cur_x, cur_y)
                    ctx.paint()

                    # ... and render the text
                    # TODO: y processing, text can overlap somewhat
                    ctx.move_to(text_x, cur_y)
                    ctx.set_source_rgba(*self.c_text)
                    pangoctx = pangocairo.CairoContext(ctx)
                    pangoctx.show_layout(layout)

                    # And carriage-return ourselves down for the possible next line
                    cur_y += self.ladder_up_surf.get_height() + 4

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
        self.c_room_background = (.98, .98, .98, 1)
        self.c_borders = (0, 0, 0, 1)
        self.c_label = (.7, .7, .7, 1)
        self.c_highlight = (.5, 1, .5, .2)
        self.c_text = (0, 0, 0, 1)
        self.c_entrance = (0, .5, 0, 1)

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

        # Loop through and draw our rooms
        for room in self.map.rooms:
            if room:
                self.draw_room(room, self.cleanctx, self.mmctx)

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

    def hover_simple(self, x, y, w, h):
        """
        Hover some stuff, right now this is a simple composite
        """
        # Do the composite
        ctx = self.mapctx
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ATOP)
        ctx.set_source_rgba(*self.c_highlight)
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

    def hover_conn(self):
        """
        Draw a hovered connection
        """
        (room, dir) = self.curhover
        (x, y) = self.room_xy(room)
        x += self.CONN_H_OFF[dir][0]
        y += self.CONN_H_OFF[dir][1]
        self.hover_simple(x, y, self.room_spc, self.room_spc)

    def hover_edge(self):
        """
        Draw a hovered edge
        """
        (room, dir) = self.curhover
        (x, y) = self.room_xy(room)
        x += self.EDGE_OFF[dir][0]
        y += self.EDGE_OFF[dir][1]
        self.hover_simple(x, y, self.room_spc, self.room_spc)

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

    def on_map_clicked(self, widget, event):
        """
        Handle clicks-n-such
        """
        if (event.button == 1):
            if (self.hover == self.HOVER_NONE):
                self.dragging = True
                self.hold_x = event.x_root
                self.hold_y = event.y_root
                self.diff_x = 0
                self.diff_y = 0
                self.mainarea.window.set_cursor(self.cursor_move_drag)
            elif (event.type == gtk.gdk.BUTTON_PRESS):
                need_gfx_update = False
                if (self.hover == self.HOVER_ROOM):
                    # edit/view room details
                    room = self.curhover
                    self.edit_room_label.set_markup('<b>Edit Room</b>')
                    self.roomname_entry.set_text(room.name)
                    self.roomnotes_view.get_buffer().set_text(room.notes)
                    if (room.type == Room.TYPE_ENTRANCE):
                        self.roomtype_radio_entrance.set_active(True)
                    elif (room.type == Room.TYPE_LABEL):
                        self.roomtype_radio_label.set_active(True)
                    else:
                        self.roomtype_radio_normal.set_active(True)
                    self.room_up_entry.set_text(room.up)
                    self.room_up_entry.set_position(0)
                    self.room_down_entry.set_text(room.down)
                    self.room_down_entry.set_position(0)
                    if (room.unexplored()):
                        self.roomname_entry.grab_focus()
                    else:
                        self.roomnotes_view.grab_focus()
                    buf = self.roomnotes_view.get_buffer()
                    buf.place_cursor(buf.get_start_iter())
                    # TODO: should we poke around with scroll/cursor here?
                    result = self.edit_room_dialog.run()
                    self.edit_room_dialog.hide()
                    if (result == gtk.RESPONSE_OK):
                        if (room.name != self.roomname_entry.get_text()):
                            need_gfx_update = True
                            room.name = self.roomname_entry.get_text()
                        if (self.roomtype_radio_entrance.get_active()):
                            new_type = Room.TYPE_ENTRANCE
                        elif (self.roomtype_radio_label.get_active()):
                            new_type = Room.TYPE_LABEL
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
                        buftxt = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
                        if (room.notes != buftxt):
                            need_gfx_update = True
                            room.notes = buftxt
                elif (self.hover == self.HOVER_CONN):
                    # remove the connection
                    room = self.curhover[0]
                    dir = self.curhover[1]
                    self.map.detach(dir, room.id)
                    need_gfx_update = True
                elif (self.hover == self.HOVER_CONN_NEW):
                    # create a new room / connection
                    room = self.curhover[0]
                    dir = self.curhover[1]
                    coords = self.map.dir_coord(room, dir)
                    if coords:
                        newroom = self.map.get_room_at(*coords)
                        if newroom:
                            if (newroom.conns[DIR_OPP[dir]]):
                                # Remove previous connection on other room
                                # (indicates that the room has moved since that connection
                                # was made)
                                self.map.detach(DIR_OPP[dir], newroom.id)
                            self.map.connect(dir, room, newroom)
                            need_gfx_update = True
                        else:
                            self.edit_room_label.set_markup('<b>New Room</b>')
                            self.roomname_entry.set_text('(unexplored)')
                            self.roomnotes_view.get_buffer().set_text('')
                            self.roomtype_radio_normal.set_active(True)
                            self.room_up_entry.set_text('')
                            self.room_down_entry.set_text('')
                            self.roomname_entry.grab_focus()
                            result = self.edit_room_dialog.run()
                            self.edit_room_dialog.hide()
                            if (result == gtk.RESPONSE_OK):
                                newroom = self.map.add_room_at(coords[0], coords[1], self.roomname_entry.get_text())
                                if (self.roomtype_radio_entrance.get_active()):
                                    newroom.type = Room.TYPE_ENTRANCE
                                elif (self.roomtype_radio_label.get_active()):
                                    newroom.type = Room.TYPE_LABEL
                                else:
                                    newroom.type = Room.TYPE_NORMAL
                                newroom.up = self.room_up_entry.get_text()
                                newroom.down = self.room_down_entry.get_text()
                                buf = self.roomnotes_view.get_buffer()
                                newroom.notes = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
                                self.map.connect(dir, room, newroom)
                                need_gfx_update = True
                elif (self.hover == self.HOVER_EDGE):
                    # move the room, if possible
                    room = self.curhover[0]
                    dir = self.curhover[1]
                    if (self.map.move_room(room, dir)):
                        need_gfx_update = True
                else:
                    # Nothing...
                    pass

                if (need_gfx_update):
                    self.trigger_redraw()

    def trigger_redraw(self):
        """
        Things that need to be done when the map is redrawn
        """
        self.clean_hover()
        self.draw()
        self.mainarea.queue_draw()

    def on_map_released(self, widget, event):
        """
        What to do when the mouse button lifts.  No effect unless we're dragging.
        """
        if self.dragging:
            self.dragging = False
            self.mainarea.window.set_cursor(None)

    def on_mouse_changed(self, widget, event):
        """
        Track mouse changes
        """
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

        # Figure out if we're hoving over anything
        pixel_offset = int((self.mmsurf.get_stride() * event.y) + (event.x*4))
        hoverpixel = unpack('BBBB', self.mmdata[pixel_offset:pixel_offset+4])
        if (hoverpixel[2] != 0):
            # TODO: Visualization for mouseovers on these
            typeidx = hoverpixel[2]
            room = self.map.get_room(hoverpixel[0])
            if (typeidx == self.HOVER_ROOM):
                if (self.hover != self.HOVER_ROOM or self.curhover != room):
                    self.clean_hover()
                    self.hover = self.HOVER_ROOM
                    self.curhover = room
                    self.hover_room()
                    self.mainarea.queue_draw()
                    self.set_hover('(%d, %d) - Edit Room' % (room.x+1, room.y+1))
            elif (typeidx == self.HOVER_CONN or typeidx == self.HOVER_CONN_NEW):
                conn = (room, hoverpixel[1])
                if (self.hover != self.HOVER_CONN or self.curhover[0] != conn[0] or self.curhover[1] != conn[1]):
                    self.clean_hover()
                    self.hover = typeidx
                    self.curhover = conn
                    self.hover_conn()
                    self.mainarea.queue_draw()
                    if (self.hover == self.HOVER_CONN):
                        self.set_hover('(%d, %d) - Remove %s connection' % (room.x+1, room.y+1, DIR_2_TXT[self.curhover[1]]))
                    else:
                        self.set_hover('(%d, %d) - New connection to the %s' % (room.x+1, room.y+1, DIR_2_TXT[self.curhover[1]]))
            elif (typeidx == self.HOVER_EDGE):
                edge = (room, hoverpixel[1])
                if (self.hover != self.HOVER_EDGE or self.curhover[0] != edge[0] or self.curhover[1] != edge[1]):
                    self.clean_hover()
                    self.hover = self.HOVER_EDGE
                    self.curhover = edge
                    self.hover_edge()
                    self.mainarea.queue_draw()
                    self.set_hover('(%d, %d) - Nudge Room to %s' % (room.x+1, room.y+1, DIR_2_TXT[self.curhover[1]]))
            else:
                raise Exception("Invalid R code in bit mousemap")
        else:
            self.clean_hover()
            self.mainarea.queue_draw()
            self.set_hover('')

    def key_handler(self, widget, event):
        """
        Handles keypresses
        """
        if (event.keyval < 256 and (event.state & self.keymask) == 0):
            key = chr(event.keyval).lower()
            # Next two key handlers are just testing until we tie them into
            # the actual menus, etc
            if (self.hover == self.HOVER_ROOM):
                if (key == 'd'):
                    if (self.map.roomcount < 2):
                        self.errordialog('You cannot remove the last room from a map', self.window)
                        return
                    self.map.del_room(self.curhover)
                    self.trigger_redraw()

    def nudge_lock_toggled(self, widget):
        """
        Lets us know to redraw the mousemaps because nudging is locked/unlocked.
        (Note that this actually just triggers a full redraw)
        """
        self.trigger_redraw()

    def nudge_map(self, widget):
        """
        Handles getting a signal to nudge the map in a given direction
        """
        (nudge, dir_txt) = widget.name.split('_', 2)
        dir = TXT_2_DIR[dir_txt]
        if (self.map.nudge(dir)):
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
            self.map = self.game.maps[self.map_idx]
            self.update_title()
            self.trigger_redraw()

    def edit_game(self, widget):
        """
        Calls the game edit screen
        """

        self.gamename_entry.set_text(self.game.name)

        self.mapstore.clear()
        for (idx, map) in enumerate(self.game.maps):
            iter = self.mapstore.append()
            self.mapstore.set(iter,
                    self.MAP_COL_TEXT, map.name,
                    self.MAP_COL_EDIT, True,
                    self.MAP_COL_CURIDX, idx,
                    self.MAP_COL_ROOMS, map.roomcount,
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
            iter = self.mapstore.get_iter_first()
            new_map_idx = 0
            found_cur_map = False
            while (iter):
                mapname = self.mapstore.get_value(iter, self.MAP_COL_TEXT)
                curidx = self.mapstore.get_value(iter, self.MAP_COL_CURIDX)
                if (curidx == -1):
                    newmaps.append(self.create_new_map(mapname))
                else:
                    if (curidx == self.map_idx):
                        new_map_idx = len(newmaps)
                        found_cur_map = True
                    self.game.maps[curidx].name = mapname
                    newmaps.append(self.game.maps[curidx])
                iter = self.mapstore.iter_next(iter)
            self.game.replace_maps(newmaps)

            # Update our currently-selected map
            self.map_idx = new_map_idx
            self.map = self.game.maps[self.map_idx]

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
            iter = self.mapstore.append()
            self.mapstore.set(iter,
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
        model, iter = sel.get_selected()

        if iter:
            roomcount = model.get_value(iter, self.MAP_COL_ROOMS)
            if (roomcount > 0):
                res = self.confirmdialog('If you delete this map, all rooms will be removed with it.  Are you sure you want to continue?', self.edit_game_dialog)
                if (res != gtk.RESPONSE_YES):
                    return
            idx = model.get_path(iter)[0]
            model.remove(iter)
            self.update_mapremove_button()

    def on_mapname_edited(self, cell, path_string, new_text, model):
        """
        Handle a map name being changed via our Game Edit screen
        """
        if (new_text == ''):
            self.errordialog('Map must have a name', self.edit_game_dialog)
            return
        iter = model.get_iter_from_string(path_string)
        path = model.get_path(iter)[0]
        column = cell.get_data('column')

        if (column == 0):
            model.set(iter, column, new_text)

    def open_notes(self, widget, all=False):
        """
        Open up our notes window
        """
        if all:
            maplist = self.game.maps
            self.notes_window.set_title('Room Notes (for all maps)')
        else:
            maplist = [self.map]
            self.notes_window.set_title('Room Notes (for %s)' % (self.map.name))

        # First loop through to find out what notes we have
        notes = {}
        for (idx, map) in enumerate(maplist):
            notes[idx] = {}
            for room in map.rooms:
                if (room and room.notes and room.notes != ''):
                    notes[idx][room.id] = room.notes

        # ... and now report
        buffer = self.global_notes_view.get_buffer()
        buffer.set_text('')
        have_notes = False
        end = buffer.get_end_iter()
        buffer.insert(end, "\n")
        for (idx, rooms) in notes.items():
            if (len(rooms) > 0):
                have_notes = True
                buffer.insert_with_tags_by_name(end, 'Notes for %s' % (maplist[idx].name), 'mapheader')
                buffer.insert(end, "\n\n")
                for (id, notes) in rooms.items():
                    room = maplist[idx].get_room(id)
                    buffer.insert_with_tags_by_name(end, room.name, 'roomheader')
                    buffer.insert_with_tags_by_name(end, ' at (%d, %d)' % (room.x+1, room.y+1), 'coords')
                    buffer.insert(end, "\n")
                    buffer.insert_with_tags_by_name(end, notes, 'notes')
                    buffer.insert(end, "\n\n")
        if not have_notes:
            buffer.insert_with_tags_by_name(end, "\n\n\n(no notes)", 'nonotes')

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
