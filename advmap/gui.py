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

import math
import os.path
import operator
import textwrap
import collections
from PyQt5 import QtWidgets, QtGui, QtCore

from advmap import version
from advmap.data import *

class Constants(object):
    """
    Basically just a container for a bunch of static vars used by a number
    of classes
    """

    # Size of icons in our toolbar
    toolbar_icon_size = 24

    # Geometry of our rooms, etc
    room_size = 110
    room_size_half = room_size/2
    room_space = 30
    room_space_half = room_space/2
    connhelper_corner_length = room_size_half*.2
    group_padding = 10
    conn_hover_size = room_space
    conn_hover_size_half = room_space_half

    # Border around the room where we theoretically want to not have text
    room_text_padding = 4

    # Vars for our in/out/up/down labels
    icon_label_space = 3
    icon_space_between = 4

    # Ladder connection vars
    ladder_width = 12
    ladder_rung_spacing = 7
    ladder_line_width = 4

    # How "wide" to draw the arrowhead for one-way connections.  This is
    # the number of pixels from the centerline which each half of the arrow
    # will be drawn, not the space between them.
    arrow_head_width = 8

    # How "long" the arrowhead should be, away from the point
    arrow_head_length = room_space*1.5

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

    # Percentage along a connection line where secondary conns will meet
    # up with the primary
    conn_secondary_connect_midpoint = .75
    conn_secondary_connect_regular = .40

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

    # Minimum height of a single-line Notes field
    notes_min_height = None

    # Height of each row in our MapListTable
    maplist_row_height = None

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

    gfx_nudge_nw = None
    gfx_nudge_n = None
    gfx_nudge_ne = None
    gfx_nudge_e = None
    gfx_nudge_se = None
    gfx_nudge_s = None
    gfx_nudge_sw = None
    gfx_nudge_w = None

    gfx_resize_down = None
    gfx_resize_up = None
    gfx_resize_left = None
    gfx_resize_right = None

    gfx_grid = None
    gfx_readonly = None
    gfx_nudge = None

    gfx_error_full = None
    gfx_error = None
    gfx_question_full = None
    gfx_question = None
    gfx_information_full = None
    gfx_information = None

    gfx_icon_new = None
    gfx_icon_open = None
    gfx_icon_revert = None
    gfx_icon_save = None
    gfx_icon_save_as = None
    gfx_icon_import = None
    gfx_icon_export = None
    gfx_icon_quit = None
    gfx_icon_gameedit = None
    gfx_icon_duplicate = None
    gfx_icon_notes_single = None
    gfx_icon_notes_all = None
    gfx_icon_about = None
    gfx_icon_license = None
    gfx_icon_plus = None
    gfx_icon_minus = None
    gfx_icon_copy = None
    gfx_icon_paste = None

    gfx_icon_ok = None
    gfx_icon_yes = None
    gfx_icon_no = None
    gfx_icon_cancel = None
    gfx_icon_close = None

    gfx_hover_add_conn = None
    gfx_hover_edit_conn = None

    gfx_hover_nudge_nw = None
    gfx_hover_nudge_n = None
    gfx_hover_nudge_ne = None
    gfx_hover_nudge_e = None
    gfx_hover_nudge_se = None
    gfx_hover_nudge_s = None
    gfx_hover_nudge_sw = None
    gfx_hover_nudge_w = None
    gfx_hover_icon_map = {}

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

    # How large our QMessageBox main icon should be
    messagebox_icon_size = 50

    # Initialize a bunch of Colors that we'll use
    c_background = QtGui.QColor(255, 255, 255, 255)
    c_background_out_of_scene = QtGui.QColor(200, 200, 200)
    c_connection = QtGui.QColor(0, 0, 0, 255)
    c_borders = QtGui.QColor(0, 0, 0, 255)
    c_label = QtGui.QColor(178, 178, 178, 255)
    c_highlight = QtGui.QColor(140, 255, 140, 51)
    c_highlight_nudge = QtGui.QColor(178, 178, 178, 51)
    c_highlight_modify = QtGui.QColor(200, 127, 255, 51)
    c_highlight_new = QtGui.QColor(127, 127, 255, 51)
    c_grid = QtGui.QColor(229, 229, 229, 255)
    c_transparent = QtGui.QColor(0, 0, 0, 0)

    c_group_map = {
            Group.STYLE_NORMAL: QtGui.QColor(216, 216, 216, 255),
            Group.STYLE_RED: QtGui.QColor(242, 216, 216, 255),
            Group.STYLE_GREEN: QtGui.QColor(190, 232, 190, 255),
            Group.STYLE_BLUE: QtGui.QColor(216, 216, 242, 255),
            Group.STYLE_YELLOW: QtGui.QColor(242, 242, 216, 255),
            Group.STYLE_PURPLE: QtGui.QColor(242, 216, 242, 255),
            Group.STYLE_CYAN: QtGui.QColor(216, 242, 242, 255),
            Group.STYLE_FAINT: QtGui.QColor(242, 242, 242, 255),
            Group.STYLE_DARK: QtGui.QColor(165, 165, 165, 255),
        }

    # Entries here are tuples with the following:
    #   1) Foreground color for borders
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
                    Room.COLOR_BW: (QtGui.QColor(193, 193, 193, 150), QtGui.QColor(249, 249, 249, 255), None),
                    Room.COLOR_RED: (QtGui.QColor(244, 193, 193, 150), QtGui.QColor(255, 249, 249, 255), None),
                    Room.COLOR_GREEN: (QtGui.QColor(193, 244, 193, 150), QtGui.QColor(249, 255, 249, 255), None),
                    Room.COLOR_BLUE: (QtGui.QColor(193, 193, 244, 150), QtGui.QColor(249, 249, 255, 255), None),
                    Room.COLOR_YELLOW: (QtGui.QColor(244, 244, 193, 150), QtGui.QColor(255, 255, 249, 255), None),
                    Room.COLOR_PURPLE: (QtGui.QColor(244, 193, 244, 150), QtGui.QColor(255, 249, 255, 255), None),
                    Room.COLOR_CYAN: (QtGui.QColor(193, 244, 244, 150), QtGui.QColor(249, 255, 255, 255), None),
                    Room.COLOR_ORANGE: (QtGui.QColor(244, 218, 193, 150), QtGui.QColor(249, 252, 255, 255), None),
                },
        }

    # Some convenience objects which will get populated as the GUI
    # gets built.  This is stretching the definition of "Constant"
    # pretty terribly, but I do not feel bad about this.
    statusbar = None

    # How many Undo actions we store before cycling 'em out
    max_undo_len = 30

def draw_dashed_line(x1, y1, x2, y2, dash_pixels, pen,
        parent=None, scene=None, zvalue=None):
    """
    This global function is hanging out here so it can be easily called
    from any of our classes without having to finagle a reference to some
    other instance.  Basically this is here because of the twin spectres
    of these two bugs related to using `QPen.setDashPattern()`:

        https://bugreports.qt.io/browse/QTBUG-63322
        https://bugreports.qt.io/browse/QTBUG-63386

    Stupidly, the one is a "fix" for the other - you've gotta pick your
    method of failure.  To be fair, the second one isn't awful really,
    but it makes dashed lines look bizarre while scrolling, often.

    Anyway, rather than use `setDashPattern` like we should be able to,
    this is basically just a custom implementation of dashed lines which
    uses individual `QGraphicsLineItem` objects for each section of the
    dash.

    Only implements a simple dash pattern where a line of `dash_pixels` 
    is drawn, followed by empty space also of `dash_pixels` (and so on).
    """

    # TODO: if one of those two bugs is ever fixed (or if I figure out
    # some way around them), rip this out and get back to just using
    # dashPattern like we should.

    # First figure out the total length of our line to draw
    x_len = (x2 - x1)
    y_len = (y2 - y1)
    line_len = math.sqrt(x_len**2 + y_len**2)
    num_segments = line_len/dash_pixels
    if num_segments == 0:
        return

    # Calculate some other stuff if we have segments to draw
    x_delta = x_len/num_segments
    y_delta = y_len/num_segments
    num_segments_int = math.ceil(num_segments)

    # And loop through to draw them
    cur_x = x1
    cur_y = y1
    for i in range(num_segments_int):
        if i == num_segments_int - 1:
            new_x = x2
            new_y = y2
        else:
            new_x = cur_x + x_delta
            new_y = cur_y + y_delta
        if (i % 2) == 0:
            line = QtWidgets.QGraphicsLineItem(cur_x, cur_y, new_x, new_y, parent)
            pen.setCapStyle(QtCore.Qt.FlatCap)
            line.setPen(pen)
            if zvalue:
                line.setZValue(zvalue)
            if scene:
                scene.addItem(line)
        cur_x = new_x
        cur_y = new_y

class HTMLStyle(QtWidgets.QProxyStyle):
    """
    A QProxyStyle which can be used to render HTML/Rich text inside
    QComboBoxes and QCheckBoxes.  Note that for QComboBox, this does
    NOT alter rendering of the items when you're choosing from the
    list.  For that you'll need to set an item delegate.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_doc = QtGui.QTextDocument()

    def drawItemText(self, painter, rect, alignment, pal, enabled, text, text_role):
        """
        This is what draws the text - we use an internal QTextDocument
        to do the formatting.  The general form of this function follows the
        C++ version at https://github.com/qt/qtbase/blob/5.9/src/widgets/styles/qstyle.cpp

        Note that we completely ignore the `alignment` and `enabled` variable.
        This is always left-aligned, and does not currently support disabled
        widgets.
        """
        if not text or text == '':
            return

        # Save our current pen if we need to
        saved_pen = None
        if text_role != QtGui.QPalette.NoRole:
            saved_pen = painter.pen()
            painter.setPen(QtGui.QPen(pal.brush(text_role), saved_pen.widthF()))

        # Render the text.  There's a bit of voodoo here with the rectangles
        # and painter translation; there was various bits of finagling necessary
        # to get this to seem to work with both combo boxes and checkboxes.
        # There's probably better ways to be doing this.
        margin = 3
        painter.save()
        painter.translate(rect.left()-margin, 0)
        self.text_doc.setHtml(text)
        self.text_doc.drawContents(painter,
                QtCore.QRectF(rect.adjusted(-rect.left(), 0, -margin, 0)))
        painter.restore()

        # Restore our previous pen if we need to
        if text_role != QtGui.QPalette.NoRole:
            painter.setPen(saved_pen)

    def sizeFromContents(self, contents_type, option, size, widget=None):
        """
        For ComboBoxes, this gets called to determine the size of the list of
        options for the comboboxes.  This is too wide for our HTMLComboBox, so
        we pull in the width from there instead.
        """
        width = size.width()
        height = size.height()
        if contents_type == self.CT_ComboBox and widget and type(widget) == HTMLComboBox:
            size = widget.sizeHint()
            width = size.width() + widget.width_adjust_contents
        return super().sizeFromContents(contents_type,
                option,
                QtCore.QSize(width, height),
                widget)

class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    """
    Class for use in a QComboBox to allow HTML Text.  I'm still a bit
    miffed that this isn't just a default part of Qt.  There's a lot of
    Google hits from people looking to do this, most suggesting
    implementing something like this, but so far I've only found this
    one actual implementation, at the end of a thread here:
    http://www.qtcentre.org/threads/62867-HTML-rich-text-delegate-and-text-centering-aligning-code-amp-pictures

    I suspect this implementation is probably heavier than we actually
    need, but it seems fairly voodooey anyway.  And keep in mind that
    after all this, you've still got to produce a completely bloody
    different solution for displaying the currently-selected item in
    the QComboBox; this is only for the list of choices.  I'm happy
    to be leaving Gtk but this kind of thing makes the move more
    bittersweet than it should be.
    """

    def __init__(self, parent=None):
        super().__init__()
        self.doc = QtGui.QTextDocument(self)

    def paint(self, painter, option, index):
        """
        Paint routine for our items in the QComboBox
        """

        # Save our painter so it can be restored later
        painter.save()

        # Copy our option var so we can make some changes without modifying
        # the underlying object
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        # Add in our data to our QTextDocument
        self.doc.setHtml(options.text)

        # Acquire our style
        if options.widget is None:
            style = QtWidgets.QApplication.style()
        else:
            style = options.widget.style()

        # Draw a barebones version of the control which doesn't have any
        # text specified - this is to render the background, basically, so
        # that when we're mousing over one of the items the bg changes.
        options.text = ''
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        # Grab a PaintContext and set our text color depending on if we're
        # selected or not
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        if option.state & QtWidgets.QStyle.State_Selected:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.Text))

        # Calculating some rendering geometry.
        textRect = style.subElementRect(
            QtWidgets.QStyle.SE_ItemViewItemText, options)
        textRect.adjust(3, 0, 0, 0)
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))

        # Now, finally, actually render the text
        self.doc.documentLayout().draw(painter, ctx)

        # Restore our paintbrush
        painter.restore()

    def sizeHint(self, option, index):
        """
        Our size.  This actually gets called before `paint`, I think, and therefore
        is called before our text has actually been loaded into the QTextDocument,
        but apparently seems to Do The Right Thing Anyway.
        """
        return QtCore.QSize(int(self.doc.idealWidth()),
                int(self.doc.size().height()))

class HTMLComboBox(QtWidgets.QComboBox):
    """
    Custom QComboBox class to handle dealing with HTML/Rich text.  This
    is basically just here to set a few attributes and then implement
    a custom sizeHint.  This implementation does NOT support ComboBoxes
    whose contents get updated - sizeHint will cache its information
    the first time it's called and then never update it.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setStyle(HTMLStyle())
        self.setItemDelegate(HTMLDelegate())
        self.stored_size = None

        # TODO: Figure out how to actually calculate these properly
        self.width_adjust_sizehint = 20
        self.width_adjust_contents = -30

    def sizeHint(self):
        """
        Use a QTextDocument to compute our rendered text size
        """
        if not self.stored_size:
            doc = QtGui.QTextDocument()
            model = self.model()
            max_w = 0
            max_h = 0
            for rownum in range(model.rowCount()):
                item = model.item(rownum)
                doc.setHtml(item.text())
                size = doc.size()
                if size.width() > max_w:
                    max_w = size.width()
                if size.height() > max_h:
                    max_h = size.height()

            # Need to add in a bit of padding to account for the
            # arrow selector
            max_w += self.width_adjust_sizehint

            self.stored_size = QtCore.QSize(int(max_w), int(max_h))
        return self.stored_size

    def minimumSizeHint(self):
        """
        Just use the same logic as `sizeHint`
        """
        return self.sizeHint()

class HTMLWidgetHelper(object):
    """
    Class to enable HTML/Rich text on a "simple" Qt widget such as QCheckBox
    or QRadioButton.  The most important bit is setting the widget style to
    HTMLStyle.  The rest is all just making sure that the widget is sized
    properly; without it, the widget will be too wide.  If you don't care
    about that, you can easily just use .setStyle(HTMLStyle()) on a regular
    widget without bothering with subclassing.

    There's doubtless some corner cases we're missing here, but it works
    for my purposes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(HTMLStyle())
        self.stored_size = None

    def sizeHint(self):
        """
        Use a QTextDocument to compute our rendered text size
        """
        if not self.stored_size:
            doc = QtGui.QTextDocument()
            doc.setHtml(self.text())
            size = doc.size()
            # Details from this derived from QCheckBox/QRadioButton sizeHint sourcecode:
            # https://github.com/qt/qtbase/blob/5.9/src/widgets/widgets/qcheckbox.cpp
            # https://github.com/qt/qtbase/blob/5.9/src/widgets/widgets/qradiobutton.cpp
            opt = QtWidgets.QStyleOptionButton()
            self.initStyleOption(opt)
            self.stored_size = QtCore.QSize(
                    int(size.width() + opt.iconSize.width() + 4),
                    int(max(size.height(), opt.iconSize.height())))
        return self.stored_size

    def minimumSizeHint(self):
        """
        Just use the same logic as `sizeHint`
        """
        return self.sizeHint()

class HTMLCheckBox(HTMLWidgetHelper, QtWidgets.QCheckBox):
    """
    An HTML-enabled QCheckBox.  All the actual work is done in HTMLWidgetHelper.
    We're abusing (well, using) Python's multiple inheritance since the same code
    works well for more than one widget type.
    """

class HTMLRadioButton(HTMLWidgetHelper, QtWidgets.QRadioButton):
    """
    An HTML-enabled QRadioButton.  All the actual work is done in HTMLWidgetHelper.
    We're abusing (well, using) Python's multiple inheritance since the same code
    works well for more than one widget type.
    """

class FirstLineEdit(QtWidgets.QLineEdit):
    """
    Stupid little class which automatically sets the cursor position
    to the beginning of the field, when the value is set.
    """

    def setText(self, text):
        super().setText(text)
        self.setCursorPosition(0)

class MainStatusBar(QtWidgets.QStatusBar):
    """
    Main status bar for our app.  Basically we're adding in a QVBoxLayout which
    includes both a QLabel and a QStatusBar, and passing through statusbar-related
    functions to the inner status bar
    """

    def __init__(self, parent):

        super().__init__(parent)

        # We don't want a separate size grip for this
        self.setSizeGripEnabled(False)

        # Main VBox
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setSpacing(0)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        # The QLabel which shows what actions are available
        self.hover_label = QtWidgets.QLabel(self)
        self.hover_label.setAlignment(QtCore.Qt.AlignHCenter)

        # The "real" inner QStatusBar which updates go to
        self.inner_sb = QtWidgets.QStatusBar(self)

        # Two-step label, indicating that a two-step process is in progress
        self.two_step_hover = QtWidgets.QLabel(self)
        self.inner_sb.addPermanentWidget(self.two_step_hover)

        # Now the widget that our inner statusbar uses to display
        self.normal = QtWidgets.QLabel(self)
        self.inner_sb.addWidget(self.normal)

        # Housekeeping...
        self.vbox.addWidget(self.hover_label)
        self.vbox.addWidget(self.inner_sb)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.vbox)
        self.addWidget(self.widget, 1)

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

    def setNormalMessage(self, text):
        """
        Sets text as a "normal" message, rather than a temporary one
        """
        self.normal.setText(text)

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
        self.hover_label.setText('<i>{}</i>'.format(hover_text))

    def clear_two_step_text(self):
        """
        Clears our two-step hover label
        """
        self.two_step_hover.clear()

    def set_two_step_text(self, text):
        """
        Sets our two-step hover label
        """
        self.two_step_hover.setText('<b>{}</b>'.format(text))

class MapCombo(QtWidgets.QComboBox):

    def __init__(self, parent, maingui):
        super().__init__(parent)
        self.maingui = maingui
        self.currentIndexChanged.connect(self.index_changed)
        self.setSizeAdjustPolicy(self.AdjustToContents)
        self.loading = False

    def clear_maplist(self):
        """
        Clears our maplist without raising any signals.  Will not
        trigger anything until another call to sset_maplist
        """
        self.loading = True
        self.clear()

    def set_maplist(self, maplist, keep_position=False):
        """
        Sets our contents.  `maplist` should be a list of
        tuples, with the following indexes:
            1) Map name
            2) Map index
        If `keep_position` is `True`, we will keep the map at
        the current position at time of running
        """
        if keep_position:
            cur_position = self.currentIndex()
        self.clear_maplist()
        for (mapname, mapidx) in maplist:
            self.addItem(mapname, mapidx)
        self.loading = False
        if keep_position:
            self.setCurrentIndex(cur_position)

    def index_changed(self, index):
        """
        The user selected a new map to display
        """
        if not self.loading:
            self.maingui.set_current_map(self.currentData())

class MainToolBar(QtWidgets.QToolBar):
    """
    Main dock widget
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setFloatable(False)
        self.setMovable(False)
        self.setIconSize(Constants.gfx_nudge_n.size())
        self.readonly_actions = []

        # Nudge buttons
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_nudge_n),
            'Shift map to the north', lambda: parent.nudge_map(DIR_N)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_nudge_ne),
            'Shift map to the northeast', lambda: parent.nudge_map(DIR_NE)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_nudge_e),
            'Shift map to the east', lambda: parent.nudge_map(DIR_E)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_nudge_se),
            'Shift map to the southeast', lambda: parent.nudge_map(DIR_SE)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_nudge_s),
            'Shift map to the south', lambda: parent.nudge_map(DIR_S)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_nudge_sw),
            'Shift map to the southwest', lambda: parent.nudge_map(DIR_SW)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_nudge_w),
            'Shift map to the west', lambda: parent.nudge_map(DIR_W)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_nudge_nw),
            'Shift map to the northwest', lambda: parent.nudge_map(DIR_NW)))
        self.addSeparator()

        # Map resizing
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_resize_up),
            'Cut off bottom row of map', lambda: parent.resize_map(DIR_N)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_resize_down),
            'Add row to bottom of map', lambda: parent.resize_map(DIR_S)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_resize_left),
            'Cut off rightmost column of map', lambda: parent.resize_map(DIR_W)))
        self.readonly_actions.append(self.addAction(QtGui.QIcon(Constants.gfx_resize_right),
            'Add column to right of map', lambda: parent.resize_map(DIR_E)))
        self.addSeparator()

        # In-room nudge hovers
        self.nudge_toggle = self.addAction(QtGui.QIcon(Constants.gfx_nudge), 'Toggle in-room map nudging', parent.toggle_nudge)
        self.nudge_toggle.setCheckable(True)
        self.addSeparator()

        # Grid
        self.grid_toggle = self.addAction(QtGui.QIcon(Constants.gfx_grid), 'Toggle map grid', parent.toggle_grid)
        self.grid_toggle.setCheckable(True)
        self.addSeparator()

        # Readonly
        self.readonly_toggle = self.addAction(QtGui.QIcon(Constants.gfx_readonly), 'Toggle readonly', parent.toggle_readonly)
        self.readonly_toggle.setCheckable(True)

        # Game Label (which happens to be a spacer which will push everything after to be
        # right-aligned)
        self.game_label = QtWidgets.QLabel()
        self.game_label.setAlignment(QtCore.Qt.AlignCenter)
        self.game_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.addWidget(self.game_label)

        # Map Selection Combo
        self.mapcombo = MapCombo(self, parent)
        self.mapcombo.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.addWidget(self.mapcombo)

        # Edit Game
        style = self.style()
        self.edit_game = self.addAction(Constants.gfx_icon_gameedit,
            'Game/Map Settings', parent.action_game_settings)

    def toggle_readonly_actions(self):
        """
        Disable or enable our readonly-sensitive actions, depending on the current
        state of our readonly checkbox.
        """
        if self.readonly_toggle.isChecked():
            enabled = False
        else:
            enabled = True
        for action in self.readonly_actions:
            action.setEnabled(enabled)

class OKButton(QtWidgets.QPushButton):
    """
    Our own "standard" OK button.  A bit silly, but this way we can
    access one from anywhere.
    """

    def __init__(self, parent=None):
        super().__init__(Constants.gfx_icon_ok, 'OK', parent)

class YesButton(QtWidgets.QPushButton):
    """
    Our own "standard" Yes button.  A bit silly, but this way we can
    access one from anywhere.
    """

    def __init__(self, parent=None):
        super().__init__(Constants.gfx_icon_yes, 'Yes', parent)

class NoButton(QtWidgets.QPushButton):
    """
    Our own "standard" No button.  A bit silly, but this way we can
    access one from anywhere.
    """

    def __init__(self, parent=None):
        super().__init__(Constants.gfx_icon_no, 'No', parent)

class CancelButton(QtWidgets.QPushButton):
    """
    Our own "standard" Cancel button.  A bit silly, but this way we can
    access one from anywhere.
    """

    def __init__(self, parent=None):
        super().__init__(Constants.gfx_icon_cancel, 'Cancel', parent)

class CloseButton(QtWidgets.QPushButton):
    """
    Our own "standard" Close button.  A bit silly, but this way we can
    access one from anywhere.
    """

    def __init__(self, parent=None):
        super().__init__(Constants.gfx_icon_close, 'Close', parent)

class UndoAction(object):
    """
    Simple little object to hold some information about an undo state.
    This is basically just a glorified dict which holds the index of
    the map in question (as in from the main map selection combo box),
    and a duplicate of the map as it should be, should we revert to
    this state.
    """

    def __init__(self, index, mapobj, description):
        """
        Initialize given a map index and a map object.  Take care that
        the map object passed in is a duplicate of the "real" map the
        user is working on.
        """
        self.index = index
        self.mapobj = mapobj
        self.description = description

class GUI(QtWidgets.QMainWindow):
    """
    Main application window.
    """

    def __init__(self, initfile, readonly):
        super().__init__()
        self.initUI(initfile, readonly)

    def icon_scale(self, pixmap, size):
        """
        Scales an icon to our specified size.  Just a convenience function so
        we can do this stuff a little less wordily.
        """
        return pixmap.scaled(int(size), int(size),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation)

    def initUI(self, initfile, readonly):

        # Set up a scene object in case something is looking for it.  This'll
        # prevent AttributeErrors.
        self.scene = None

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
            if font_size == Constants.default_note_size:
                Constants.notes_min_height = m_rect.height()
        Constants.title_max_height = Constants.room_size_half - (Constants.room_text_padding*1) - m_rect.height()

        # Map list row height
        t = QtWidgets.QGraphicsTextItem('Map Name')
        t.setFont(QtGui.QFont())
        Constants.maplist_row_height = t.boundingRect().height()

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

        gfx_nudge_src_nw = QtGui.QPixmap(self.resfile('dir_nw.png'))
        gfx_nudge_src_n = QtGui.QPixmap(self.resfile('dir_n.png'))
        gfx_nudge_src_ne = QtGui.QPixmap(self.resfile('dir_ne.png'))
        gfx_nudge_src_e = QtGui.QPixmap(self.resfile('dir_e.png'))
        gfx_nudge_src_se = QtGui.QPixmap(self.resfile('dir_se.png'))
        gfx_nudge_src_s = QtGui.QPixmap(self.resfile('dir_s.png'))
        gfx_nudge_src_sw = QtGui.QPixmap(self.resfile('dir_sw.png'))
        gfx_nudge_src_w = QtGui.QPixmap(self.resfile('dir_w.png'))

        Constants.gfx_nudge_nw = self.icon_scale(gfx_nudge_src_nw, Constants.toolbar_icon_size)
        Constants.gfx_nudge_n = self.icon_scale(gfx_nudge_src_n, Constants.toolbar_icon_size)
        Constants.gfx_nudge_ne = self.icon_scale(gfx_nudge_src_ne, Constants.toolbar_icon_size)
        Constants.gfx_nudge_e = self.icon_scale(gfx_nudge_src_e, Constants.toolbar_icon_size)
        Constants.gfx_nudge_se = self.icon_scale(gfx_nudge_src_se, Constants.toolbar_icon_size)
        Constants.gfx_nudge_s = self.icon_scale(gfx_nudge_src_s, Constants.toolbar_icon_size)
        Constants.gfx_nudge_sw = self.icon_scale(gfx_nudge_src_sw, Constants.toolbar_icon_size)
        Constants.gfx_nudge_w = self.icon_scale(gfx_nudge_src_w, Constants.toolbar_icon_size)

        Constants.gfx_resize_up = self.icon_scale(QtGui.QPixmap(self.resfile('dir_exp_up.png')), Constants.toolbar_icon_size)
        Constants.gfx_resize_down = self.icon_scale(QtGui.QPixmap(self.resfile('dir_exp_down.png')), Constants.toolbar_icon_size)
        Constants.gfx_resize_left = self.icon_scale(QtGui.QPixmap(self.resfile('dir_exp_left.png')), Constants.toolbar_icon_size)
        Constants.gfx_resize_right = self.icon_scale(QtGui.QPixmap(self.resfile('dir_exp_right.png')), Constants.toolbar_icon_size)
        Constants.gfx_grid = self.icon_scale(QtGui.QPixmap(self.resfile('grid.png')), Constants.toolbar_icon_size)
        Constants.gfx_readonly = self.icon_scale(QtGui.QPixmap(self.resfile('lock.png')), Constants.toolbar_icon_size)
        Constants.gfx_nudge = self.icon_scale(QtGui.QPixmap(self.resfile('direction.png')), Constants.toolbar_icon_size)

        # Icons used by QMessageBox for the main dialog icon
        Constants.gfx_error_full = QtGui.QPixmap(self.resfile('smashicons-error.png'))
        Constants.gfx_error = self.icon_scale(Constants.gfx_error_full, Constants.messagebox_icon_size)
        Constants.gfx_question_full = QtGui.QPixmap(self.resfile('smashicons-info.png'))
        Constants.gfx_question = self.icon_scale(Constants.gfx_question_full, Constants.messagebox_icon_size)
        Constants.gfx_information_full = QtGui.QPixmap(self.resfile('smashicons-idea.png'))
        Constants.gfx_information = self.icon_scale(Constants.gfx_information_full, Constants.messagebox_icon_size)

        # Icons used primarily by menus and message dialog buttons
        Constants.gfx_icon_new = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-file-1.png')))
        Constants.gfx_icon_open = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-folder-6.png')))
        Constants.gfx_icon_revert = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-restart.png')))
        Constants.gfx_icon_save = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-save.png')))
        Constants.gfx_icon_save_as = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-archive-1.png')))
        Constants.gfx_icon_import = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-incoming.png')))
        Constants.gfx_icon_export = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-photo-camera.png')))
        Constants.gfx_icon_quit = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-exit-1.png')))
        Constants.gfx_icon_gameedit = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-layers-1.png')))
        Constants.gfx_icon_duplicate = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-add-3.png')))
        Constants.gfx_icon_notes_single = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-notepad.png')))
        Constants.gfx_icon_notes_all = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-notebook-4.png')))
        Constants.gfx_icon_about = QtGui.QIcon(Constants.gfx_question_full)
        Constants.gfx_icon_license = Constants.gfx_icon_notes_single
        plus_pixmap = QtGui.QPixmap(self.resfile('smashicons-plus.png'))
        Constants.gfx_icon_plus = QtGui.QIcon(plus_pixmap)
        Constants.gfx_icon_minus = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-minus.png')))
        Constants.gfx_icon_copy = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-upload.png')))
        Constants.gfx_icon_paste = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-download.png')))
        Constants.gfx_icon_undo = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-previous.png')))
        Constants.gfx_icon_redo = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-skip.png')))

        # Icons used in our "standard" dialogs
        Constants.gfx_icon_ok = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-success.png')))
        Constants.gfx_icon_yes = Constants.gfx_icon_ok
        Constants.gfx_icon_no = QtGui.QIcon(Constants.gfx_error_full)
        Constants.gfx_icon_cancel = Constants.gfx_icon_no
        Constants.gfx_icon_close = QtGui.QIcon(QtGui.QPixmap(self.resfile('smashicons-multiply-1.png')))

        # Graphics used by hovering over a connection point
        Constants.gfx_hover_add_conn = self.icon_scale(plus_pixmap, Constants.conn_hover_size_half)
        Constants.gfx_hover_edit_conn = self.icon_scale(QtGui.QPixmap(self.resfile('smashicons-edit.png')),
                Constants.conn_hover_size_half)

        # Graphics used by hovering over a room nudge point
        Constants.gfx_hover_nudge_nw = self.icon_scale(gfx_nudge_src_nw, Constants.conn_hover_size)
        Constants.gfx_hover_nudge_n = self.icon_scale(gfx_nudge_src_n, Constants.conn_hover_size)
        Constants.gfx_hover_nudge_ne = self.icon_scale(gfx_nudge_src_ne, Constants.conn_hover_size)
        Constants.gfx_hover_nudge_e = self.icon_scale(gfx_nudge_src_e, Constants.conn_hover_size)
        Constants.gfx_hover_nudge_se = self.icon_scale(gfx_nudge_src_se, Constants.conn_hover_size)
        Constants.gfx_hover_nudge_s = self.icon_scale(gfx_nudge_src_s, Constants.conn_hover_size)
        Constants.gfx_hover_nudge_sw = self.icon_scale(gfx_nudge_src_sw, Constants.conn_hover_size)
        Constants.gfx_hover_nudge_w = self.icon_scale(gfx_nudge_src_w, Constants.conn_hover_size)
        Constants.gfx_hover_icon_map = {
                DIR_N: Constants.gfx_hover_nudge_n,
                DIR_NE: Constants.gfx_hover_nudge_ne,
                DIR_E: Constants.gfx_hover_nudge_e,
                DIR_SE: Constants.gfx_hover_nudge_se,
                DIR_S: Constants.gfx_hover_nudge_s,
                DIR_SW: Constants.gfx_hover_nudge_sw,
                DIR_W: Constants.gfx_hover_nudge_w,
                DIR_NW: Constants.gfx_hover_nudge_nw,
                }

        # Making sure our view memory vars exist early
        self.clear_view_memory()

        # Set up a status bar
        self.statusbar = MainStatusBar(self)
        self.setStatusBar(self.statusbar)
        Constants.statusbar = self.statusbar

        # Set up our dock widget
        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

        # File Menu
        style = self.style()
        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(Constants.gfx_icon_new,
                '&New', self.action_new, 'Ctrl+N')
        filemenu.addAction(Constants.gfx_icon_open,
                '&Open', self.action_open, 'Ctrl+O')
        self.revert_menu_item = filemenu.addAction(Constants.gfx_icon_revert,
                '&Revert', self.action_revert, 'Ctrl+R')
        filemenu.addAction(Constants.gfx_icon_save,
                '&Save', self.action_save, 'Ctrl+S')
        filemenu.addAction(Constants.gfx_icon_save_as,
                'Save &As', self.action_save_as)
        filemenu.addSeparator()
        filemenu.addAction(Constants.gfx_icon_import,
                '&Import Maps', self.action_import, 'Ctrl+I')
        filemenu.addSeparator()
        filemenu.addAction(Constants.gfx_icon_export,
                '&Export Image', self.action_export, 'Ctrl+E')
        filemenu.addSeparator()
        filemenu.addAction(Constants.gfx_icon_quit,
                '&Quit', self.action_quit, 'Ctrl+Q')

        # Edit Menu
        editmenu = menubar.addMenu('&Edit')
        self.undo_menu_item = editmenu.addAction(Constants.gfx_icon_undo,
                '&Undo', self.action_undo, 'Ctrl+Z')
        self.undo_menu_item.setEnabled(False)
        self.redo_menu_item = editmenu.addAction(Constants.gfx_icon_redo,
                '&Redo', self.action_redo, 'Ctrl+Y')
        self.redo_menu_item.setEnabled(False)
        editmenu.addSeparator()
        editmenu.addAction(Constants.gfx_icon_save_as,
                'Select &All', self.action_select_all, 'Ctrl+A')
        self.copy_menu_item = editmenu.addAction(Constants.gfx_icon_copy,
                '&Copy', self.action_copy, 'Ctrl+C')
        self.copy_menu_item.setEnabled(False)
        self.paste_menu_item = editmenu.addAction(Constants.gfx_icon_paste,
                '&Paste', self.action_paste, 'Ctrl+V')
        self.paste_menu_item.setEnabled(False)
        editmenu.addSeparator()
        editmenu.addAction(Constants.gfx_icon_gameedit,
                '&Game/Map Settings', self.action_game_settings)
        editmenu.addSeparator()
        editmenu.addAction(Constants.gfx_icon_duplicate,
                '&Duplicate Map...', self.action_duplicate)

        # View Menu
        viewmenu = menubar.addMenu('&View')
        viewmenu.addAction(Constants.gfx_icon_notes_single,
                'Room Notes (for this map)', self.action_room_notes_map)
        viewmenu.addAction(Constants.gfx_icon_notes_all,
                'Room Notes (for all maps)', self.action_room_notes_all)

        # Help
        helpmenu = menubar.addMenu('&Help')
        helpmenu.addAction(Constants.gfx_icon_about,
                '&About', self.action_about)

        # Set up our main widgets
        self.maparea = MapArea(self)
        self.scene = self.maparea.scene
        self.setCentralWidget(self.maparea)
        self.maparea.statusbar[str].connect(self.statusbar.setNormalMessage)
        self.setMinimumSize(1000, 700)
        self.resize(1000, 700)
        self.setWindowTitle('Adventure Game Mapper')

        # Create an empty game/map to start out with, so that if we're loading
        # a file and it fails, the dialog can be properly modal.  It looks
        # like it probably won't actually center properly because the mainloop
        # hasn't started up, and the engine probably doesn't actually know
        # the location of the main window yet.  But still!  Better than before.
        self.curfile = None
        self.create_new_game()

        # Set our readonly state, if we've been told to
        if readonly:
            self.toolbar.readonly_toggle.setChecked(True)
            self.toggle_readonly()

        # Set up an empty clipboard object
        self.clipboard = Clipboard()

        # Set up a clean Undo stack
        self.clear_undo()

        # Show ourselves
        self.show()

        # Try to load a file, if we've been told to.
        if initfile:
            try:
                self.load_from_file(initfile)
            except Exception as e:
                self.dialog_error('Unable to load file', str(e))

    def dialog_user(self, message, infotext, pixmap,
            show_yes=False, show_no=False, show_ok=False,
            default_yes=False, parent=None):
        """
        Shows a dialog to the user with the specified information and
        returns its result.  Note that we use a QMessageBox for this, but
        don't actually make use of its informativeText attribute because
        I don't like how that ends up interacting with word wrapping.
        """
        if not parent:
            msgbox = QtWidgets.QMessageBox(self)
        else:
            msgbox = QtWidgets.QMessageBox(parent)
        msgbox.setWindowTitle(message)
        message = '<p><b>{}</b></p>'.format(message)
        if infotext and infotext != '':
            text = "{}\n\n{}".format(message, "\n".join(textwrap.wrap(infotext, width=100)))
        else:
            text = message
        msgbox.setText(text)

        # Show our custom buttons
        if show_ok:
            ok = OKButton(msgbox)
            msgbox.addButton(ok, msgbox.AcceptRole)
            msgbox.setDefaultButton(ok)
        if show_yes:
            yes = YesButton(msgbox)
            msgbox.addButton(yes, msgbox.YesRole)
            if default_yes:
                msgbox.setDefaultButton(yes)
        if show_no:
            no = NoButton(msgbox)
            msgbox.addButton(no, msgbox.NoRole)
            if not default_yes:
                msgbox.setDefaultButton(no)

        msgbox.setIconPixmap(pixmap)
        msgbox.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)

        # Rather than returning the exec() value, return the role of the
        # button which was chosen, so we can match on that (needed because
        # we're not using StandardButtons
        msgbox.exec()
        return msgbox.buttonRole(msgbox.clickedButton())

    def dialog_confirm(self, message, infotext=None, default_yes=False):
        """
        Asks the user to confirm an action.  Returns `True` or
        `False`.
        """
        res = self.dialog_user(message, infotext,
                Constants.gfx_question,
                show_yes=True, show_no=True, default_yes=default_yes)
        self.activateWindow()
        if res == QtWidgets.QMessageBox.YesRole:
            return True
        else:
            return False

    def dialog_error(self, message, infotext=None, parent=None):
        """
        Shows an error dialog to the user
        """
        self.dialog_user(message, infotext,
                Constants.gfx_error,
                show_ok=True,
                parent=parent)
        self.activateWindow()

    def dialog_info(self, message, infotext=None):
        """
        Shows an informational dialog to the user
        """
        self.dialog_user(message, infotext,
                Constants.gfx_information,
                show_ok=True)
        self.activateWindow()

    def set_status(self, status_str):
        """
        Sets our status
        """
        self.statusbar.setNormalMessage(status_str)

    def set_temporary_status(self, status_str, seconds=5):
        """
        Sets a temporary message on our statusbar.
        """
        self.statusbar.showMessage(status_str, seconds*1000)

    def load_from_file(self, filename):
        """
        Loads a game from a file.  Note that we always return
        true; if loading failed, the load() method should raise an
        exception, which should be caught by anything attempting
        the load.
        """
        # TODO: center on map
        game = Game.load(filename)
        self.clear_view_memory()
        self.game = game
        self.curfile = filename
        self.set_status('Editing %s' % filename)
        self.set_mapcombo()
        self.revert_menu_item.setEnabled(True)
        self.clear_undo()
        return True

    def set_mapcombo(self, keep_position=False):
        """
        Sets up our mapcombo.  Pass in `keep_position`=`True`
        in order to not update our selected index.
        """
        self.toolbar.mapcombo.set_maplist([(r.name, idx) for (idx, r) in enumerate(self.game.maps)],
                keep_position=keep_position)
        if not keep_position:
            self.set_current_map(0)

    def set_current_map(self, mapindex):
        """
        Sets the current map to the specified index
        """
        self.store_view_memory()
        self.mapobj = self.game.maps[mapindex]
        self.map_idx = mapindex
        self.scene.set_map(self.mapobj)
        self.setWindowTitle('Adventure Game Mapper | {} | {}'.format(self.game.name, self.mapobj.name))
        self.toolbar.game_label.setText('<b>{}</b>'.format(self.game.name))
        self.restore_view_memory()

    def replace_map(self, mapindex, mapobj):
        """
        Replaces the map at the given index with the specified
        object.
        """
        self.game.maps[mapindex] = mapobj
        self.set_current_map(mapindex)

    def clear_view_memory(self):
        """
        Clears our view memory, which stores where our scrollbars
        are for each map
        """
        self.view_memory = {}

    def store_view_memory(self):
        """
        Stores our view memory for the current map
        """
        if self.mapobj:
            vbar = self.maparea.verticalScrollBar()
            hbar = self.maparea.horizontalScrollBar()
            self.view_memory[self.mapobj] = (hbar.value(), vbar.value())

    def restore_view_memory(self):
        """
        Restores our view memory for the current map, if possible.  This
        will theoretically put our scrollbars back where they were, the
        last time we viewed this map.  If we don't have any known values
        here, center the view.
        """
        if self.mapobj and self.mapobj in self.view_memory:
            (hval, vval) = self.view_memory[self.mapobj]
            self.maparea.horizontalScrollBar().setValue(hval)
            self.maparea.verticalScrollBar().setValue(vval)
        else:
            # TODO: I wonder if it'd be nicer to center around the "average"
            # of all the rooms, rather than the center of the scene.  I also
            # wonder if it might be better to default to upper-left-corner
            # for existing maps, so long as rooms are visible, rather than
            # centering.
            hbar = self.maparea.horizontalScrollBar()
            vbar = self.maparea.verticalScrollBar()
            hmin = hbar.minimum()
            hmax = hbar.maximum()
            hbar.setValue(int((hmin+hmax)/2))
            vmin = vbar.minimum()
            vmax = vbar.maximum()
            vbar.setValue(int((vmin+vmax)/2))

    def create_new_game(self):
        """
        Starts a new Game file from scratch.
        """
        self.curfile = None
        self.toolbar.mapcombo.clear_maplist()
        self.game = Game('New Game')
        self.mapobj = self.create_new_map('Starting Map')
        self.map_idx = self.game.add_map_obj(self.mapobj)
        self.set_mapcombo()
        self.revert_menu_item.setEnabled(False)
        self.set_status('Editing a new game')
        self.clear_undo()
        self.clear_view_memory()
        self.restore_view_memory()

    def create_new_map(self, name):
        """
        Creates our default new map, with a single room in the center
        """
        # TODO: center
        mapobj = Map(name)
        room = mapobj.add_room_at(4, 4, 'Room')
        room.notes = 'Starting Room'
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

    def nudge_map(self, direction):
        """
        Attempts to nudge the current scene in the given direction
        """
        self.start_undo()
        if self.mapobj.nudge(direction):
            self.finish_undo('Nudge Map to {}'.format(DIR_2_TXT[direction]))
            self.scene.recreate()

    def resize_map(self, direction):
        """
        Attempts to resize the current scene in the given direction
        """
        self.start_undo()
        if self.mapobj.resize(direction):
            self.finish_undo('Resize Map to {}'.format(DIR_2_TXT[direction]))
            self.scene.recreate()

    def toggle_nudge(self):
        """
        Toggles whether room hovers will have separate "nudge" hovers as well.
        """
        self.scene.recreate()

    def toggle_grid(self):
        """
        Toggles whether our background grid will be drawn
        """
        self.scene.recreate()

    def is_readonly(self):
        """
        Returns `True` or `False` depending on if we're in readonly mode
        """
        return self.toolbar.readonly_toggle.isChecked()

    def toggle_readonly(self):
        """
        Toggles our readonly state
        """
        self.toolbar.toggle_readonly_actions()
        if self.is_readonly():
            self.scene.clear_selected()
            self.paste_menu_item.setEnabled(False)
        else:
            if self.clipboard.has_data:
                self.paste_menu_item.setEnabled(True)
        self.scene.recreate()

    def import_maps_from_file(self, filename):
        """
        Imports maps from another adventure file into this one.
        Returns the number of new maps added.
        """
        seen_names = set()
        for mapobj in self.game.maps:
            seen_names.add(mapobj.name)
        game = Game.load(filename)
        for mapobj in game.maps:
            base_mapname = mapobj.name
            mapname = base_mapname
            idx = 1
            while mapname in seen_names:
                idx += 1
                mapname = '%s (%d)' % (base_mapname, idx)
            mapobj.name = mapname
            self.game.add_map_obj(mapobj)
        return len(game.maps)

    def action_new(self):
        """
        Handle our "New" action.
        """
        proceed = self.dialog_confirm('Create New Map',
            'Starting a new game will erase any unsaved changes.  Really wipe the current map?')
        if proceed:
            self.create_new_game()

    def action_open(self):
        """
        Handle our "Open" action.
        """
        if self.curfile:
            path = os.path.dirname(os.path.realpath(self.curfile))
        else:
            path = self.reldir('data')

        rundialog = True
        while rundialog:
            rundialog = False
            (filename, filefilter) = QtWidgets.QFileDialog.getOpenFileName(self,
                    'Open Game Map File...',
                    path,
                    'Game Map Files (*.adv);;All Files (*.*)')

            if filename and filename != '':
                try:
                    self.load_from_file(filename)
                except Exception as e:
                    self.dialog_error('Error opening file', str(e))
                    path = os.path.dirname(filename)
                    rundialog = True

        # Re-focus the main window
        self.activateWindow()

    def action_revert(self):
        """
        Handle our "Revert" action.
        """
        if self.curfile:
            proceed = self.dialog_confirm('Revert to Saved',
                    'Reverting to the saved copy on disk will revert any changes you have made.  Continue?')
            if proceed:
                try:
                    self.load_from_file(self.curfile)
                    self.clear_undo()
                    self.dialog_info('Reverted to on-disk version of file')
                except Exception as e:
                    self.dialog_error('Unable to Revert file', str(e))
        else:
            self.dialog_error('Unable to Revert file', 'This map has never been saved to disk')

    def action_save(self):
        """
        Handle our "Save" action.
        """
        if self.curfile:
            self.game.save(self.curfile)
            self.set_temporary_status('Game saved to {}'.format(self.curfile))
        else:
            self.action_save_as()

    def action_save_as(self):
        """
        Handle our "Save As" action.
        """
        if self.curfile:
            path = os.path.dirname(os.path.realpath(self.curfile))
        else:
            path = self.reldir('data')
        (filename, filefilter) = QtWidgets.QFileDialog.getSaveFileName(self,
                'Save Game File...',
                path,
                'Game Map Files (*.adv);;All Files (*.*)')

        if filename and filename != '':
            if filename [-4:] != '.adv':
                filename = '{}.adv'.format(filename)
            self.curfile = filename
            self.game.save(self.curfile)
            self.set_status('Editing %s' % self.curfile)
            self.set_temporary_status('Game saved to {}'.format(self.curfile))
            self.revert_menu_item.setEnabled(True)

        # Re-focus the main window
        self.activateWindow()

    def action_import(self):
        """
        Handle our "Import" action.
        """
        if self.curfile:
            path = os.path.dirname(os.path.realpath(self.curfile))
        else:
            path = self.reldir('data')

        rundialog = True
        imported = 0
        while rundialog:
            rundialog = False
            (filename, filefilter) = QtWidgets.QFileDialog.getOpenFileName(self,
                    'Import Game Map File...',
                    path,
                    'Game Map Files (*.adv);;All Files (*.*)')
            if filename and filename != '':
                try:
                    imported = self.import_maps_from_file(filename)
                except Exception as e:
                    self.errordialog('Error importing maps', str(e))
                    rundialog = True

        # Report on any maps imported
        if imported > 0:
            self.set_mapcombo(keep_position=True)
            if imported == 1:
                plural = ''
            else:
                plural = 's'
            self.dialog_info('Imported Maps', '{} map{} imported'.format(imported, plural))

        # Re-focus the main window
        self.activateWindow()

    def action_export(self):
        """
        Handle our "Export" action.
        """
        extensions = []
        formats = QtGui.QImageWriter.supportedImageFormats()
        for ext in formats:
            extensions.append('.{}'.format(str(ext.data(), 'utf-8')))
        default_ext = '.png'

        # Get the filename to export to
        if self.curfile:
            path = os.path.dirname(os.path.realpath(self.curfile))
        else:
            path = None
        (filename, filefilter) = QtWidgets.QFileDialog.getSaveFileName(self,
                'Export Image...',
                path,
                'Image Files ({});;All Files (*.*)'.format(
                    ' '.join(['*{}'.format(ext) for ext in extensions]))
                )

        if filename and filename != '':

            # Make sure we have an extension we know about.
            found_ext = False
            for ext in extensions:
                if filename[-len(ext):] == ext:
                    found_ext = True
            if not found_ext:
                filename += default_ext

            # Write out the image
            painter = None
            try:
                image = QtGui.QImage(int(self.scene.width()), int(self.scene.height()), QtGui.QImage.Format_ARGB32)
                painter = QtGui.QPainter(image)
                painter.setRenderHints(QtGui.QPainter.Antialiasing)
                self.scene.render(painter)
                image.save(filename)
                self.dialog_info('Image exported', 'Image exported to {}'.format(filename))
            except Exception as e:
                self.dialog_error('Error exporting image', str(e))
            finally:
                if painter:
                    del painter

        # Re-focus the main window
        self.activateWindow()

    def action_quit(self):
        """
        Handle our "Quit" action.
        """
        proceed = self.dialog_confirm('Quit',
                'Any unsaved changes to the current file will be lost.  Continue?',
                default_yes=True)
        if proceed:
            self.close()

    def action_game_settings(self):
        """
        Handle our "Game Settings" action.
        """
        d = EditGameDialog(self, self.game)
        res = d.exec()
        self.activateWindow()

    def action_duplicate(self):
        """
        Handle our "Duplicate" action.
        """
        (newname, status) = QtWidgets.QInputDialog.getText(self,
                'Duplicate Map',
                'Map Name:',
                text='{} (copy)'.format(self.mapobj.name))
        if status:
            newmap = self.mapobj.duplicate(newname)
            self.game.add_map_obj(newmap)
            self.set_mapcombo(keep_position=True)
            self.set_temporary_status('Added new map "{}"'.format(newname))

    def action_room_notes_map(self):
        """
        Handle our "Room Notes" action for current map
        """
        d = NotesDialog(self, mapobj=self.mapobj)
        d.exec()
        self.activateWindow()

    def action_room_notes_all(self):
        """
        Handle our "Room Notes" action for all maps
        """
        d = NotesDialog(self, maplist=self.game.maps)
        d.exec()
        self.activateWindow()

    def action_about(self):
        """
        Handle our "About" action.
        """
        d = AboutDialog(self)
        d.exec()
        self.activateWindow()

    def action_select_all(self):
        """
        Handle our "Select All" action
        """
        self.scene.select_all()
        self.scene.recreate()

    def action_copy(self):
        """
        Handle our "copy" action
        """
        if len(self.scene.selected) > 0:
            self.clipboard.copy(self.scene.mapobj, self.scene.selected)
        elif (self.scene.hover_current and
                type(self.scene.hover_current) == GUIRoomHover):
            self.clipboard.copy(self.scene.mapobj, [self.scene.hover_current.gui_room.room])
        else:
            return
        if not self.is_readonly():
            self.paste_menu_item.setEnabled(True)
        count = self.clipboard.room_count()
        if count == 1:
            plural = ''
        else:
            plural = 's'
        self.set_temporary_status('Copied {} room{} to clipboard'.format(count, plural), 3)

    def action_paste(self):
        """
        Handle our "paste" action
        """
        if self.scene.hover_current and type(self.scene.hover_current) == GUINewRoomHover:
            x = self.scene.hover_current.x
            y = self.scene.hover_current.y
        else:
            x = None
            y = None
        self.start_undo()
        if self.clipboard.paste(self.mapobj, x, y):
            roomcount = self.clipboard.room_count()
            if roomcount == 1:
                plural = 's'
            else:
                plural = ''
            self.finish_undo('Paste {} Room{}'.format(roomcount, plural))
            self.scene.recreate()
            count = self.clipboard.room_count()
            if count == 1:
                plural = ''
            else:
                plural = 's'
            self.set_temporary_status('Pasted {} room{} into map'.format(count, plural), 3)
        else:
            self.set_temporary_status('Unable to find room on map to paste', 3)

    def update_copy_menu(self):
        """
        Updates our Copy menu actions depending on if it's supposed
        to be active or not.
        """
        if self.scene:
            if self.scene.has_selections():
                self.copy_menu_item.setEnabled(True)
            elif (self.scene.hover_current and
                    type(self.scene.hover_current) == GUIRoomHover):
                self.copy_menu_item.setEnabled(True)
            else:
                self.copy_menu_item.setEnabled(False)

    def start_undo(self, description=None):
        """
        Start an undo action.  If `description` is passed in, we will
        also commit the action right away.
        """
        self.cur_undo = self.scene.mapobj.duplicate()
        if description:
            self.finish_undo(description)

    def finish_undo(self, description):
        """
        Commits our previously-started undo action.
        """
        if self.cur_undo:
            self.undo.append(UndoAction(self.toolbar.mapcombo.currentIndex(),
                self.cur_undo,
                description))
            self.cur_undo = None
            self.update_undo_menus()
            self.clear_redo()

    def action_undo(self):
        """
        Handle our "undo" action
        """
        if len(self.undo) > 0:
            undo = self.undo.pop()
            self.toolbar.mapcombo.setCurrentIndex(undo.index)
            self.redo.append(UndoAction(undo.index,
                self.scene.mapobj.duplicate(),
                undo.description))
            self.replace_map(undo.index, undo.mapobj.duplicate())
            self.scene.recreate()
            self.update_undo_menus()

    def action_redo(self):
        """
        Handle our "redo" action
        """
        if len(self.redo) > 0:
            redo = self.redo.pop()
            self.toolbar.mapcombo.setCurrentIndex(redo.index)
            self.undo.append(UndoAction(redo.index,
                self.scene.mapobj.duplicate(),
                redo.description))
            self.replace_map(redo.index, redo.mapobj.duplicate())
            self.scene.recreate()
            self.update_undo_menus()

    def update_undo_menus(self):
        """
        Updates our undo/redo menu states
        """
        if len(self.undo) == 0:
            self.undo_menu_item.setEnabled(False)
            self.undo_menu_item.setText('&Undo')
        else:
            self.undo_menu_item.setEnabled(True)
            self.undo_menu_item.setText('&Undo "{}"'.format(self.undo[-1].description))
        if len(self.redo) == 0:
            self.redo_menu_item.setEnabled(False)
            self.redo_menu_item.setText('&Redo')
        else:
            self.redo_menu_item.setEnabled(True)
            self.redo_menu_item.setText('&Redo "{}"'.format(self.redo[-1].description))

    def clear_redo(self):
        """
        Clears our redo stacks
        """
        self.redo = collections.deque(maxlen=Constants.max_undo_len)
        self.update_undo_menus()

    def clear_undo(self):
        """
        Clears our undo/redo stacks
        """
        self.cur_undo = None
        self.undo = collections.deque(maxlen=Constants.max_undo_len)
        self.clear_redo()

class HoverArea(QtWidgets.QGraphicsRectItem):
    """
    Class to handle some generalized functions related to our hover areas.
    Namely, this is a way to consolidate what actions are available in
    one spot, rather than having to check them in multiple ways.
    """

    def __init__(self, parent, mainwindow, x=None, y=None, multi=False):
        super().__init__(parent)
        self.mainwindow = mainwindow
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsFocusable)
        self.key_actions_by_key = {}
        self.mouse_actions_by_button = {}
        self.actionlist = []
        self.x = x
        self.y = y
        if x is None or y is None:
            self.prefix = None
        else:
            self.prefix = '({}, {})'.format(x+1, y+1)
        self.actions_initialized = False
        self.multi = multi

    def add_label_action(self, report_keys, report_text):
        """
        Adds a "label" action which doesn't actually trigger any action from
        this framework.  Used for fancier actions (like the shift-clicking
        for room selection), click-and-drag notifications, and the multi-select
        room keys which operate outside our usual hover widget's purview.
        """
        self.actionlist.append((report_keys, report_text))

    def add_key_action(self, report_keys, report_text, keylist, action, action_args, undo_texts):
        """
        Adds a possible keyboard action that we can take.  `report_keys`
        is what the user will see as the available action, and `report_text`
        is how the action will be described.  `keylist` should be a list of
        keys which map to this action.  `action` is the function itself, to call.
        `action_args` should be a list corresponding to `keylist`, with the
        optional argument(s) to send to the function.  `undo_texts`, likewise,
        should be a list of the text to report in our undo/redo menus

        If our Scene has multi-selections enabled, those keys will always override
        keyboard controls otherwise usually available, so we will check for that
        and *not* add the keyboard action in that case.
        """
        scene = self.scene()
        if not self.multi and scene.has_selections():
            return
        self.actionlist.append((report_keys, report_text))
        if action is not None:
            for (key, args, undo) in zip(keylist, action_args, undo_texts):
                self.key_actions_by_key[key] = (action, args, undo)

    def add_mouse_action(self, report_button, report_text, button, action, action_args, undo_text):
        """
        Adds a possible keyboard action that we can take.  `report_button`
        is what the user will see as the available action, and `report_text`
        is how the action will be described.  `button` should be the mouse
        button which maps to this action.  `action` is the function itself, to call.
        `action_args` should be a list of optional argument(s) to send to the
        function.  `undo_text` should be the text to report in our undo/redo menus.
        """
        self.actionlist.append((report_button, report_text))
        if button is None or action is None or action_args is None or undo_text is None:
            return
        self.mouse_actions_by_button[button] = (action, action_args, undo_text)

    def show_actions(self, scene=None):
        """
        Update our statusbar with the actions that we'll take.  If our actions aren't
        initialized yet, do so now.  Will add in our scene's multi-select actions if
        those are enabled.
        """
        if not self.actions_initialized:
            self.set_up_actions()
            if not scene:
                scene = self.scene()
            if not self.multi and scene.has_selections():
                for (key, text) in scene.multi_select_actions.actionlist:
                    self.add_label_action(key, text)
            self.actions_initialized = True
        Constants.statusbar.set_hover_actions(actions=self.actionlist, prefix=self.prefix)

    def has_key_action(self, key):
        """
        Returns `True` or `False`, depending on if we have an action for the specified
        key
        """
        return (key in self.key_actions_by_key)

    def do_key_action(self, key):
        """
        Activates the given keyboard action
        """
        if self.has_key_action(key):
            (action, args, undo_text) = self.key_actions_by_key[key]
            self.mainwindow.start_undo()
            if action(*args):
                self.mainwindow.finish_undo(undo_text)

    def has_mouse_action(self, button):
        """
        Returns `True` or `False`, depending on if we have an action for the specified
        mouse button
        """
        return (button in self.mouse_actions_by_button)

    def do_mouse_action(self, button):
        """
        Activates the given mouse action
        """
        if self.has_mouse_action(button):
            (action, args, undo_text) = self.mouse_actions_by_button[button]
            self.mainwindow.start_undo()
            if action(*args):
                self.mainwindow.finish_undo(undo_text)

    def set_up_actions(self):
        """
        Sets up our available hover actions.  This should be overridden by the
        implementing class.
        """
        pass

    def keyPressEvent(self, event, scene=None):
        """
        Keyboard input
        """
        if not scene:
            scene = self.scene()
        scene.clear_two_step_actions()
        key = event.text().lower()
        self.do_key_action(key)

    def mousePressEvent(self, event):
        """
        Mouse input
        """
        self.scene().clear_two_step_actions()
        button = event.button()
        self.do_mouse_action(button)

class GUIRoomNudgeHover(HoverArea):

    def __init__(self, gui_room, direction):
        super().__init__(gui_room, gui_room.mainwindow, x=gui_room.room.x, y=gui_room.room.y)
        self.direction = direction
        self.gui_room = gui_room
        self.room = gui_room.room
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.setZValue(Constants.z_value_edge_hover)
        self.setRect(0, 0, Constants.conn_hover_size, Constants.conn_hover_size)
        offset_x = Constants.connection_offset[direction][0]
        offset_y = Constants.connection_offset[direction][1]
        if direction in [DIR_N, DIR_S]:
            offset_x -= Constants.conn_hover_size_half
        if direction in [DIR_NE, DIR_E, DIR_SE]:
            offset_x -= Constants.conn_hover_size
        if direction in [DIR_W, DIR_E]:
            offset_y -= Constants.conn_hover_size_half
        if direction in [DIR_SW, DIR_S, DIR_SE]:
            offset_y -= Constants.conn_hover_size
        self.setPos(offset_x, offset_y)

        # Add a hover icon
        self.hover_icon = QtWidgets.QGraphicsPixmapItem(Constants.gfx_hover_icon_map[self.direction], self)
        self.hover_icon.hide()

    def hoverEnterEvent(self, event=None):
        """
        We've entered hovering
        """
        scene = self.scene()
        scene.hover_start(self)
        self.hover_icon.show()
        self.setBrush(QtGui.QBrush(Constants.c_highlight_nudge))
        self.setPen(QtGui.QPen(Constants.c_highlight_nudge))
        self.setFocus()
        self.mainwindow.maparea.setFocus()
        self.show_actions()

    def hoverLeaveEvent(self, event=None):
        """
        We've left hovering
        """
        self.scene().hover_end()
        self.hover_icon.hide()
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.clearFocus()
        self.scene().default_actions()

    def set_up_actions(self):
        """
        Sets up the actions we can take at the moment.  We shouldn't ever
        actually exist if we're in readonly mode, so we're not going to
        bother checking for that.
        """
        self.add_mouse_action('LMB', 'nudge room', QtCore.Qt.LeftButton,
                self.nudge_room, [],
                'Nudge Room to {}'.format(DIR_2_TXT[self.direction]))

    def nudge_room(self):
        """
        Nudges ourselves, if possible
        """
        scene = self.scene()
        if scene.mapobj.move_room(self.room, self.direction):
            scene.recreate()
            return True
        else:
            return False

class GUIConnectionHover(HoverArea):

    def __init__(self, gui_room, direction):
        super().__init__(gui_room, gui_room.mainwindow, x=gui_room.room.x, y=gui_room.room.y)
        self.direction = direction
        self.gui_room = gui_room
        self.room = gui_room.room
        self.conn = self.room.get_conn(self.direction)
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.setZValue(Constants.z_value_connection_hover)
        self.setRect(0, 0, Constants.conn_hover_size, Constants.conn_hover_size)
        offset_x = Constants.connection_offset[direction][0]
        offset_y = Constants.connection_offset[direction][1]
        self.setPos(offset_x - Constants.conn_hover_size_half, offset_y - Constants.conn_hover_size_half)

        # Set up a hover icon
        if self.room.get_conn(self.direction) or self.room.get_loopback(self.direction):
            use_add_positioning = False
            pixmap = Constants.gfx_hover_edit_conn
        else:
            use_add_positioning = True
            pixmap = Constants.gfx_hover_add_conn
        self.hover_icon = QtWidgets.QGraphicsPixmapItem(pixmap, self)
        icon_size = self.hover_icon.pixmap().width()
        hover_x = 0
        hover_y = 0
        # Our icon positioning is different depending on the icon
        if use_add_positioning:
            if direction in [DIR_N, DIR_S]:
                hover_x += (Constants.conn_hover_size - icon_size) / 2
            elif direction in [DIR_NE, DIR_E, DIR_SE]:
                hover_x += Constants.conn_hover_size - icon_size
            if direction in [DIR_W, DIR_E]:
                hover_y += (Constants.conn_hover_size - icon_size) / 2
            elif direction in [DIR_SW, DIR_S, DIR_SE]:
                hover_y += Constants.conn_hover_size - icon_size
        else:
            if direction in [DIR_NW, DIR_W, DIR_SW]:
                hover_x += Constants.conn_hover_size - icon_size
            elif direction in [DIR_N, DIR_S]:
                hover_x += (Constants.conn_hover_size - icon_size) / 2
            if direction in [DIR_NW, DIR_N, DIR_NE]:
                hover_y += Constants.conn_hover_size - icon_size
            elif direction in [DIR_W, DIR_E]:
                hover_y += (Constants.conn_hover_size - icon_size) / 2
        self.hover_icon.setPos(hover_x, hover_y)
        self.hover_icon.hide()

    def hoverEnterEvent(self, event=None):
        """
        We've entered hovering
        """
        scene = self.scene()
        scene.hover_start(self)
        self.hover_icon.show()
        if self.room.get_conn(self.direction) or self.room.get_loopback(self.direction):
            self.setBrush(QtGui.QBrush(Constants.c_highlight_modify))
            self.setPen(QtGui.QPen(Constants.c_highlight_modify))
        else:
            self.setBrush(QtGui.QBrush(Constants.c_highlight_new))
            self.setPen(QtGui.QPen(Constants.c_highlight_new))
        self.setFocus()
        self.mainwindow.maparea.setFocus()
        self.show_actions()

    def hoverLeaveEvent(self, event=None):
        """
        We've left hovering
        """
        self.scene().hover_end()
        self.hover_icon.hide()
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.clearFocus()
        self.scene().default_actions()

    def set_up_actions(self):
        """
        Sets up the actions we can take at the moment.  We shouldn't ever
        actually exist if we're in readonly mode, so we're not going to
        bother checking for that.
        """
        scene = self.scene()
        if self.room.get_loopback(self.direction):
            self.add_key_action('C', 'remove loopback', ['c'], self.remove_connection,
                    [[]], ['Remove Loopback'])
        elif self.conn:
            self.add_mouse_action('RMB', 'move connection', QtCore.Qt.RightButton,
                    self.move_connection_step_one, [], '')
            self.add_key_action('C', 'remove connection', ['c'], self.remove_connection,
                    [[]], ['Remove Connection'])
            self.add_key_action('E', 'add extra', ['e'], self.add_extra_step_one,
                    [[]], ['Add Extra Connection End'])
            self.add_key_action('T', 'type', ['t'], self.cycle_type,
                    [[]], ['Change Conection Type'])
            self.add_key_action('P', 'path', ['p'], self.cycle_render_type,
                    [[]], ['Change Connection Path'])
            self.add_key_action('O', 'orientation', ['o'], self.cycle_passage,
                    [[]], ['Change Connection Orientation'])
            self.add_key_action('L', 'stub length', ['l'], self.cycle_stub_length,
                    [[]], ['Change Connection Stub Length'])
            if self.conn.symmetric:
                self.add_key_action('S','symmetric OFF', ['s'], self.toggle_symmetric,
                        [[]], ['Toggle Connection Symmetry Off'])
            else:
                self.add_key_action('S','symmetric ON', ['s'], self.toggle_symmetric,
                        [[]], ['Toggle Connection Symmetry On'])
            if not self.conn.is_primary(self.room, self.direction):
                self.add_key_action('R', 'set primary', ['r'], self.set_primary,
                        [[]], ['Set Primary Connection'])
        else:
            coords = scene.mapobj.dir_coord(self.room, self.direction)
            if coords:
                other_room = scene.mapobj.get_room_at(coords[0], coords[1])
                if not other_room:
                    self.add_mouse_action('LMB', 'new room', QtCore.Qt.LeftButton,
                            self.new_connection_room, [], 'Add new Room')
            self.add_mouse_action('RMB', 'new connection', QtCore.Qt.RightButton,
                    self.new_connection_step_one, [], '')
            self.add_mouse_action('MMB', 'new loopback', QtCore.Qt.MiddleButton,
                    self.new_loopback, [], 'Add new Loopback')

    def remove_connection(self):
        """
        Remove the connection (or loopback, it's the same API call)
        """
        scene = self.scene()
        scene.mapobj.detach(self.room, self.direction)
        scene.recreate()
        return True

    def move_connection_step_one(self):
        """
        We've selected a connection which we're looking to move
        """
        scene = self.scene()
        scene.two_step_move_connection = (self.room, self.direction)
        scene.start_two_step_action('Right-click to move connection')
        return False

    def add_extra_step_one(self):
        """
        We've selected a connection for which we're looking to add
        an extra end
        """
        scene = self.scene()
        scene.two_step_add_extra = (self.room, self.direction)
        scene.start_two_step_action('E again to add an extra connection to the same room')
        return False

    def cycle_type(self):
        """
        Cycles the type of our connection end
        """
        self.conn.cycle_conn_type(self.room, self.direction)
        self.scene().recreate((self.room, self.direction))
        return True

    def cycle_render_type(self):
        """
        Cycles the render type of our connection end
        """
        self.conn.cycle_render_type(self.room, self.direction)
        self.scene().recreate((self.room, self.direction))
        return True

    def cycle_passage(self):
        """
        Cycles the passage type of our connection end
        """
        self.conn.cycle_passage()
        self.scene().recreate((self.room, self.direction))
        return True

    def cycle_stub_length(self):
        """
        Cycles the stub length our connection end
        """
        self.conn.increment_stub_length(self.room, self.direction)
        self.scene().recreate((self.room, self.direction))
        return True

    def toggle_symmetric(self):
        """
        Toggles connection symmetry
        """
        self.conn.toggle_symmetric(self.room, self.direction)
        self.scene().recreate((self.room, self.direction))
        return True

    def set_primary(self):
        """
        Sets this end to be the primary end
        """
        self.conn.set_primary(self.room, self.direction)
        self.scene().recreate((self.room, self.direction))
        return True

    def new_connection_room(self):
        """
        Sets up a new connection to a new room
        """
        d = NewEditRoomDialog(self.gui_room.mainwindow, editing=False,
                room=self.room, from_direction=self.direction)
        res = d.exec()
        if res == d.Accepted:
            self.scene().recreate()
            rv = True
        else:
            rv = False
        self.gui_room.mainwindow.activateWindow()
        return rv

    def new_connection_step_one(self):
        """
        User has initiated setting up a new connection between arbitrary
        points.
        """
        scene = self.scene()
        scene.two_step_new_connection = (self.room, self.direction)
        scene.start_two_step_action('Right-click to link to existing room')
        return False

    def new_loopback(self):
        """
        Adds a new loopback
        """
        self.room.set_loopback(self.direction)
        self.scene().recreate((self.room, self.direction))
        return True

    def mousePressEvent(self, event):
        """
        Handle mouse press event - mostly just looking for the second part of
        any two-step processes before handing over to the base class.
        """
        scene = self.scene()
        if scene.two_step_move_connection:
            button = event.button()
            if button == QtCore.Qt.RightButton:
                new_room = self.room
                new_dir = self.direction
                (orig_room, orig_dir) = scene.two_step_move_connection
                scene.clear_two_step_actions()
                conn = orig_room.get_conn(orig_dir)
                self.gui_room.mainwindow.start_undo()
                if conn.move_end(orig_room, orig_dir, new_room, new_dir):
                    scene.recreate()
                    self.gui_room.mainwindow.finish_undo('Move Connection')
                return
        if scene.two_step_new_connection:
            button = event.button()
            if button == QtCore.Qt.RightButton:
                new_room = self.room
                new_dir = self.direction
                (orig_room, orig_dir) = scene.two_step_new_connection
                scene.clear_two_step_actions()
                self.gui_room.mainwindow.start_undo()
                if new_room != orig_room:
                    scene.mapobj.connect(orig_room, orig_dir, new_room, new_dir)
                    scene.recreate()
                    self.gui_room.mainwindow.finish_undo('Create New Connection')
                return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """
        Key press event - will generally pass this through, unless
        we happen to have a two-step action we're in the middle of
        """
        scene = self.scene()
        if scene.two_step_add_extra:
            key = event.text().lower()
            if key == 'e':
                (orig_room, orig_dir) = scene.two_step_add_extra
                conn = orig_room.get_conn(orig_dir)
                new_room = self.room
                new_dir = self.direction
                scene.clear_two_step_actions()
                try:
                    self.gui_room.mainwindow.start_undo()
                    conn.connect_extra(new_room, new_dir)
                    self.gui_room.mainwindow.finish_undo('Add Extra Connection')
                except Exception as e:
                    pass
                scene.recreate()
                return
        super().keyPressEvent(event)

class GUIRoomHover(HoverArea):

    def __init__(self, gui_room):
        super().__init__(gui_room, gui_room.mainwindow, x=gui_room.room.x, y=gui_room.room.y)
        self.gui_room = gui_room
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
        self.mainwindow.maparea.setFocus()
        self.show_actions()
        self.gui_room.mainwindow.update_copy_menu()

    def set_up_actions(self):
        """
        Sets up the actions we can take at the moment.
        """
        scene = self.scene()
        if self.mainwindow.is_readonly():
            self.add_mouse_action('LMB', 'view details', QtCore.Qt.LeftButton,
                    self.view_details, [], '')
        else:
            self.add_mouse_action('LMB', 'edit room', QtCore.Qt.LeftButton,
                    self.edit_room, [], 'Edit Room')
            if scene.is_selected(self.gui_room.room):
                self.add_label_action('shift-click', 'deselect')
            else:
                self.add_label_action('shift-click', 'select')
            self.add_key_action('WASD', 'nudge room', ['w', 'a', 's', 'd'],
                self.nudge_room, [[DIR_N], [DIR_W], [DIR_S], [DIR_E]],
                ['Nudge Room to N', 'Nudge Room to W', 'Nudge Room to S', 'Nudge Room to E'])
            self.add_key_action('X', 'delete', ['x'], self.delete_room,
                    [[]], ['Delete Room'])
            self.add_key_action('H/V', 'toggle horiz/vert offset', ['h', 'v'],
                self.toggle_offset, [[False], [True]],
                ['Toggle Room Horizontal Offset', 'Toggle Room Vertical Offset'])
            self.add_key_action('T', 'change type', ['t'], self.change_type,
                    [[]], ['Change Room Type'])
            self.add_key_action('R', 'change color', ['r'], self.change_color,
                    [[]], ['Change Room Color'])
            if self.gui_room.room.group:
                self.add_key_action('G', 'change group render', ['g'],
                        self.change_group_render, [[]], ['Change Group Render Color'])
                self.add_key_action('O', 'remove from group', ['o'],
                        self.remove_from_group, [[]], ['Remove Room from Group'])
            else:
                self.add_key_action('G', 'add to group', ['g'],
                        self.add_to_group_step_one, [[]], ['Add Room to Group'])

    def hoverLeaveEvent(self, event=None):
        """
        We've left hovering
        """
        self.scene().hover_end()
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.clearFocus()
        self.scene().default_actions()
        self.gui_room.mainwindow.update_copy_menu()

    def nudge_room(self, direction):
        """
        Nudges our room in the specified direction
        """
        scene = self.scene()
        room = self.gui_room.room
        scene.mapobj.move_room(room, direction)
        scene.recreate(room)
        return True

    def change_type(self):
        """
        Changes our room type
        """
        scene = self.scene()
        room = self.gui_room.room
        room.increment_type()
        scene.recreate(room)
        return True

    def change_color(self):
        """
        Changes our room color
        """
        scene = self.scene()
        room = self.gui_room.room
        room.increment_color()
        scene.recreate(room)
        return True

    def toggle_offset(self, vertical=False):
        """
        Toggles one of our x/y offset vars, depending on `vertical`
        """
        scene = self.scene()
        room = self.gui_room.room
        if vertical:
            room.offset_y = not room.offset_y
        else:
            room.offset_x = not room.offset_x
        scene.recreate(room)
        return True

    def delete_room(self):
        """
        Deletes our room
        """
        scene = self.scene()
        room = self.gui_room.room
        mapobj = scene.mapobj
        if len(mapobj.rooms) < 2:
            self.mainwindow.dialog_error('Unable to remove room',
                    'You cannot remove the last room from a map')
            return False
        mapobj.del_room(room)
        self.hoverLeaveEvent()
        scene.recreate()
        return True

    def change_group_render(self):
        """
        Changes the style of the group our room is in
        """
        scene = self.scene()
        room = self.gui_room.room
        room.group.increment_style()
        scene.recreate(room)
        return True

    def remove_from_group(self):
        """
        Removes ourself from any group we may be in.
        """
        scene = self.scene()
        room = self.gui_room.room
        if scene.mapobj.remove_room_from_group(room):
            scene.recreate(room)
            return True
        else:
            return False

    def add_to_group_step_one(self):
        """
        We've selected a room to add to a group.
        """
        scene = self.scene()
        scene.two_step_group_first = self.gui_room.room
        scene.start_two_step_action('G again to add to a group')
        return False

    def view_details(self):
        """
        Viewing room details (on account of being in readonly mode)
        """
        d = RoomDetailsDialog(self.gui_room.mainwindow, self.gui_room.room)
        d.exec()
        self.gui_room.mainwindow.activateWindow()
        return False

    def edit_room(self):
        """
        Editing the room
        """
        d = NewEditRoomDialog(self.gui_room.mainwindow, editing=True, room=self.gui_room.room)
        res = d.exec()
        if res == d.Accepted:
            self.scene().recreate()
            rv = True
        else:
            rv = False
        self.gui_room.mainwindow.activateWindow()
        return rv

    def keyPressEvent(self, event):
        """
        Key press event - will generally pass this through, unless
        we happen to have a two-step action we're in the middle of
        """
        scene = self.scene()
        if scene.two_step_group_first:
            key = event.text().lower()
            if key == 'g':
                room = self.gui_room.room
                other_room = scene.two_step_group_first
                scene.clear_two_step_actions()
                self.gui_room.mainwindow.start_undo()
                if scene.mapobj.group_rooms(room, other_room):
                    scene.recreate(room)
                    self.gui_room.mainwindow.finish_undo('Group Rooms')
                return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """
        What to do when the mouse is pressed - overriding a bit
        here to support our multi-select process.
        """
        if not self.gui_room.mainwindow.is_readonly():
            mods = event.modifiers()
            if (event.button() == QtCore.Qt.LeftButton and
                    (mods & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier):
                scene = self.scene()
                room = self.gui_room.room
                scene.select_room(room)
                scene.clear_two_step_actions()
                scene.recreate(room)
                return

        # If we didn't capture a special-case, just pass through to the
        # main handlers
        super().mousePressEvent(event)

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
    A text field used for showing room notes.  Note that unlike our
    room title/name, we don't automatically set our own positioning in
    here.  That's done outside in the main GUIRoom class, since it
    understands what kinds of other data exist in the room.
    """

    def __init__(self, parent, max_height):
        """
        Initialize inside the `parent` room.  Will have a maximum height
        of `max_height`.  We'll do multiline wrap if we can.
        """
        lines = parent.room.notes.splitlines()
        if len(lines) > 1:
            notes_to_show = '{} ...'.format(lines[0])
        elif len(lines) == 1:
            notes_to_show = lines[0]
        else:
            notes_to_show = ''
        super().__init__(notes_to_show, parent)
        self.setTextWidth(Constants.title_max_width)
        self.setFont(GUIRoom.get_notes_font(Constants.default_note_size))
        self.setDefaultTextColor(parent.color_text)
        doc = self.document()
        options = doc.defaultTextOption()
        options.setWrapMode(options.WordWrap)
        options.setAlignment(QtCore.Qt.AlignHCenter)
        doc.setDefaultTextOption(options)

        # Figure out our sizing information
        rect = self.boundingRect()
        if rect.width() > (Constants.title_max_width + (Constants.notes_padding_x[Constants.default_note_size]*2)):
            options.setWrapMode(options.WrapAtWordBoundaryOrAnywhere)
            doc.setDefaultTextOption(options)
            rect = self.boundingRect()

        # Make sure we don't exceed our specified max_height
        block = doc.begin()
        while rect.height() > (max_height + (Constants.notes_padding_y[Constants.default_note_size]*2)):
            layout = block.layout()
            if layout.lineCount() < 2:
                break
            last_line = layout.lineAt(layout.lineCount()-1)
            self.setPlainText('{}...'.format(notes_to_show[:last_line.textStart()-1]))
            rect = self.boundingRect()

    def height(self):
        """
        Retreives our height, for the purposes of placement within the GUIRoom
        """
        rect = self.boundingRect()
        return rect.height() - Constants.notes_padding_y[Constants.default_note_size]*2

    def set_position(self, y_coord):
        """
        Sets our position at the given y coordinate
        """
        rect = self.boundingRect()
        self.setPos(
                Constants.room_size_half - (rect.width()/2) + 1,
                y_coord
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
        exceeds_width = False
        for font_size in Constants.title_font_sizes:
            self.setFont(GUIRoom.get_title_font(font_size))
            rect = self.boundingRect()
            if rect.width() > (Constants.title_max_width + (Constants.title_padding_x[font_size]*2)):
                exceeds_width = True
            else:
                exceeds_width = False
            if (exceeds_width or rect.height() > (Constants.title_max_height + (Constants.title_padding_y[font_size]*2))):
                continue
            else:
                break
        self.font_size = font_size

        # If we got here and we still exceed our recommended width, switch word wrapping
        # mode so that we don't go out of the room boundaries.
        if exceeds_width:
            options.setWrapMode(options.WrapAtWordBoundaryOrAnywhere)
            doc.setDefaultTextOption(options)

        # Find out if we've exceeded three lines.  If so, truncate.
        block = doc.begin()
        layout = block.layout()
        while layout.lineCount() > 3:
            line = layout.lineAt(3)
            self.setPlainText('{}...'.format(parent.room.name[:line.textStart()-1]))
            layout = block.layout()

        # Re-aquire our bounding rect for positioning
        rect = self.boundingRect()

        # Set our position
        self.setPos(
                (Constants.room_size - rect.width())/2,
                Constants.room_text_padding - Constants.title_padding_y[font_size],
            )

    def offset_height(self):
        """
        Returns the offset height after which we can start adding more
        GUI elements.
        """
        return Constants.room_text_padding + self.boundingRect().height() - \
                Constants.title_padding_y[self.font_size]*2

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

class GUINewRoomHover(HoverArea):

    def __init__(self, gui_newroom):
        super().__init__(gui_newroom, gui_newroom.mainwindow)
        self.gui_newroom = gui_newroom
        self.x = gui_newroom.x
        self.y = gui_newroom.y
        self.setBrush(QtGui.QBrush(Constants.c_transparent))
        self.setPen(QtGui.QPen(Constants.c_transparent))
        self.setRect(0, 0, Constants.room_size, Constants.room_size)
        self.setZValue(Constants.z_value_new_room_hover)

    def hoverEnterEvent(self, event=None):
        """
        We've entered hovering
        """
        self.scene().hover_start(self)
        self.setBrush(QtGui.QBrush(Constants.c_highlight))
        self.setPen(QtGui.QPen(Constants.c_highlight))
        self.setFocus()
        self.mainwindow.maparea.setFocus()
        self.show_actions()

    def set_up_actions(self):
        """
        Sets up the actions we can take at the moment
        """
        scene = self.scene()
        self.add_label_action('LMB', 'click-and-drag')
        if not self.mainwindow.is_readonly():
            self.add_key_action('N', 'new room', ['n'], self.new_room,
                    [[]], ['Add new room'])

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

    def new_room(self):
        """
        Create a new room
        """
        d = NewEditRoomDialog(self.gui_newroom.mainwindow, editing=False, x=self.x, y=self.y)
        res = d.exec()
        if res == d.Accepted:
            self.scene().recreate()
            rv = True
        else:
            rv = False
        self.gui_newroom.mainwindow.activateWindow()
        return rv

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
        self.gfx_x = Constants.room_space + (Constants.room_size+Constants.room_space)*self.x
        self.gfx_y = Constants.room_space + (Constants.room_size+Constants.room_space)*self.y
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

            # Rendering our usual room contents - title, notes, and extra text labels.
            # This gets a bit ridiculous, actually, and I should probably look into
            # seeing if we can use some Qt classes to assist with all the positioning
            # in here. It's not totally straightforward because the positioning of
            # notes/extralabels depends on the contents of the other of the two.

            # Show our title
            self.title = GUIRoomTitleTextItem(self)
            room_data_height = Constants.room_size - self.title.offset_height() - \
                    Constants.room_text_padding*2
            cur_notes_y = self.title.offset_height() - Constants.room_text_padding

            # Set up some tooltip text
            tooltip_data = []

            # Find out how many in/out/up/down labels we may have, and figure out a
            # bit of label geometry based on that
            extra_labels = 0
            for (label, text) in [
                    (room.up, 'Up'),
                    (room.down, 'Down'),
                    (room.door_in, 'In'),
                    (room.door_out, 'Out'),
                    ]:
                if label and label != '':
                    extra_labels += 1
                    tooltip_data.append('<div><b>{}</b>: {}</div>'.format(text, label))
            if extra_labels == 0:
                reserved_for_extras = 0
            else:
                cur_extra_label_y = self.title.offset_height() + Constants.icon_space_between
                total_extra_label_size = (Constants.gfx_ladder_up.height()*extra_labels) + \
                        (Constants.icon_space_between*(extra_labels-1))
                reserved_for_extras = min(room_data_height, total_extra_label_size)

            # Set up our notes object, if we need to
            self.notes = None
            if self.room.notes and self.room.notes != '':

                # Figure out how much room to use for notes; grab as much as
                # possible given our extra label constraints.
                max_notes_height = max(Constants.notes_min_height,
                        room_data_height - reserved_for_extras)

                self.notes = GUIRoomNotesTextItem(self, max_notes_height)
                tooltip_data.append('<p><b>Notes:</b> {}</p>'.format(self.room.notes))

            # Set our tooltip, if we have one.
            if len(tooltip_data) > 0:
                self.setToolTip(''.join(tooltip_data))

            # Set up positioning vars for both notes and extra labels.  If there's
            # just one of the two, center it across the whole space.  Otherwise,
            # divide up the free space evenly (if we can).
            if extra_labels > 0 and self.notes:
                space_left_in_room = room_data_height - self.notes.height() - total_extra_label_size
                if space_left_in_room > 0:
                    padding = space_left_in_room / 3
                    cur_notes_y += padding
                    cur_extra_label_y += padding*2 + self.notes.height()
                else:
                    cur_extra_label_y += self.notes.height()
            elif self.notes:
                y_padding = (room_data_height - self.notes.height())/2
                cur_notes_y += y_padding
            elif extra_labels > 0:
                space_left_in_room = room_data_height - total_extra_label_size
                if space_left_in_room > 0:
                    cur_extra_label_y += (space_left_in_room/2)

            # Set notes positioning, if we have notes.
            if self.notes:
                self.notes.set_position(cur_notes_y)

            # Draw any in/out/up/down labels we might have
            if extra_labels > 0:
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
                        label = GUIRoomTextLabel(self, label, graphic, cur_extra_label_y)
                        cur_extra_label_y += graphic.height() + Constants.icon_space_between

        # Set our background/border coloration
        border_pen = QtGui.QPen(self.color_border)
        if self.mainwindow.scene.is_selected(self.room):
            border_pen.setWidth(3)
            if room.type == Room.TYPE_DARK:
                self.setBrush(QtGui.QBrush(self.color_bg.lighter(150)))
            else:
                self.setBrush(QtGui.QBrush(self.color_bg.darker(110)))
        else:
            border_pen.setWidthF(1.5)
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
                dash_pen = QtGui.QPen(border_pen)
                draw_dashed_line(0, 0, Constants.room_size, 0, 9, dash_pen, parent=self)
                draw_dashed_line(Constants.room_size, 0, Constants.room_size, Constants.room_size, 9, dash_pen, parent=self)
                draw_dashed_line(Constants.room_size, Constants.room_size, 0, Constants.room_size, 9, dash_pen, parent=self)
                draw_dashed_line(0, Constants.room_size, 0, 0, 9, dash_pen, parent=self)
                border_pen.setColor(QtGui.QColor(0, 0, 0, 0))
                # TODO: if Qt's dashPattern bugs ever get fixed, go back to doing this instead:
                #dash_len = 9/border_pen.width()
                #border_pen.setDashPattern([dash_len, dash_len])
            self.setPen(border_pen)
        
        # Also add a Hover object for ourselves
        self.hover_obj = GUIRoomHover(self)

        # And we'll need hovers for all our connection points.
        self.connhovers = {}
        if not self.mainwindow.is_readonly():
            for direction in DIR_LIST:
                self.connhovers[direction] = GUIConnectionHover(self, direction)

            # And finally (for now), Nudge hovers, if we've been told to
            if self.mainwindow.toolbar.nudge_toggle.isChecked():
                for direction in DIR_LIST:
                    nudgehover = GUIRoomNudgeHover(self, direction)

    def check_keep_hover_connections(self, keep_hover):
        """
        Checks our `keep_hover` to see if we should resume hovering on
        one of our GUIConnectionHover objects
        """
        if keep_hover:
            try:
                keep_room = keep_hover[0]
                keep_dir = keep_hover[1]
                if self.room == keep_room:
                    for direction in DIR_LIST:
                        if keep_dir == direction:
                            self.connhovers[direction].hoverEnterEvent()
                            break
            except TypeError as e:
                # keep_hover may not be a Tuple
                pass

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
        self.gfx_x = Constants.room_space + (Constants.room_size+Constants.room_space)*self.room.x
        self.gfx_y = Constants.room_space + (Constants.room_size+Constants.room_space)*self.room.y
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
    
    def __init__(self, x1, y1, x2, y2, scene, width=1, dashed=False):
        super().__init__(x1, y1, x2, y2)
        self.setZValue(Constants.z_value_connection)
        pen = QtGui.QPen(Constants.c_connection)
        # Width 1 lines actually benefit from being 1.1
        if width == 1:
            pen.setWidthF(1.1)
        else:
            pen.setWidthF(width)
        pen.setCapStyle(QtCore.Qt.FlatCap)
        if dashed:
            dash_pen = QtGui.QPen(pen)
            dash_pen.setWidthF(width+.5)
            draw_dashed_line(x1, y1, x2, y2, 3, dash_pen, scene=scene,
                    zvalue=Constants.z_value_connection)
            pen.setColor(QtGui.QColor(0, 0, 0, 0))
            # TODO: if Qt's dashPattern bugs ever get fixed, go back to doing this instead:
            #dash_len = 3/width
            #pen.setDashPattern([dash_len, dash_len])
        self.setPen(pen)

class GUIConnectionGenerator(object):
    """
    It's a bit stupid to have this as a class, but I'd like it to be contained
    as well as possible.  Basically this is just used to generate the various graphical
    elements which make up our connection lines.
    """

    def __init__(self, scene):
        self.scene = scene

    def line(self, x1, y1, x2, y2, width=1, dashed=False):
        """
        Draws a line from `(x1, y1)` to `(x2, y2)`
        """
        # TODO: If Qt's dashPattern bugs ever get fixed, we don't need to pass scene.
        line_obj = GUIConnLine(x1, y1, x2, y2, self.scene, width=width, dashed=dashed)
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

    def arrow_coords(self, x1, y1, x2, y2, adjust=True, ladder=False):
        """
        Given two points (x1, y1) and (x2, y2), this will provide
        coordinates necessary to draw an arrowhead centered on (x1, y1)
        It'll return a list with two 2-element tuples, describing the
        extra (x, y) coordinates you'll need to draw from (x1, y1) in
        order to draw the arrowhead.

        If `ladder` is `True`, the geometry will be slightly altered
        to account for ladder width.

        When `adjust` is `True` (the default), (x2, y2) is only used
        to provide a direction; the arrowhead will always be rendered
        at a fixed size.  If it is `False`, the length of the arrowhead
        will be determined by the length of (x1, y1) to (x2, y2).  Note
        that `adjust` will always be set to `True` if `ladder` is `True`.
        """

        # A couple of vars which differ when we're dealing with ladders
        if ladder:
            adjust = True
            spacing_ratio = .7
            width_h = Constants.arrow_head_width + (Constants.ladder_width/2)
        else:
            spacing_ratio = .5
            width_h = Constants.arrow_head_width

        # Check to see if we should adjust for our "base" line that we
        # compute off of
        if adjust:
            dx_orig = x2-x1
            dy_orig = y2-y1
            dist = math.sqrt(dx_orig**2 + dy_orig**2)
            x2 = x1 + ((Constants.arrow_head_length*dx_orig)/dist)
            y2 = y1 + ((Constants.arrow_head_length*dy_orig)/dist)

        # And now proceed with the computation.
        dx_orig = x2-x1
        dy_orig = y2-y1
        dist = math.sqrt(dx_orig**2 + dy_orig**2)

        dx = dx_orig / dist
        dy = dy_orig / dist
        coord_list = []

        x_spacing = dx_orig * spacing_ratio
        y_spacing = dy_orig * spacing_ratio
        cur_x = x1 + (x_spacing/2)
        cur_y = y1 + (y_spacing/2)

        coord_list.append( (cur_x+(width_h*dy), cur_y-(width_h*dx)) )
        coord_list.append( (cur_x-(width_h*dy), cur_y+(width_h*dx)) )

        return coord_list

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

    def resize_line(self, x1, y1, x2, y2, length_change=None, to_length=None):
        """
        Given a pair of coordinates (x1, y1) and (x2, y2), returns
        an alternate set of (x2, y2) which change the length of
        the line.

        If you specify `length_change`, the current length of the line
        will be changed by that amount.  If you specify `to_length`
        instead, the line will be set to that length exactly.  If you're
        foolish enough to specify both, `to_length` will override
        `length_change`.
        """

        # TODO: Currently we're only using this function during one-way arrowhead
        # rendering.  I expect we could be using it elsewhere as well.

        dx = x2-x1
        dy = y2-y1
        cur_length = math.sqrt(dx**2 + dy**2)

        if not to_length:
            to_length = cur_length + length_change

        length_diff = to_length/cur_length
        new_dx = length_diff*dx
        new_dy = length_diff*dy

        return (x1 + new_dx, y1 + new_dy)

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

        # aaaand we actually only want to render a line half this long.
        dst_x = (src_x+dst_x)/2
        dst_y = (src_y+dst_y)/2

        # If we're a connhelper connection, the source endpoint will
        # actually be in the very center of the room.
        if room.type == Room.TYPE_CONNHELPER:
            src_x = gui_room.gfx_x + Constants.room_size_half
            src_y = gui_room.gfx_y + Constants.room_size_half

        # Mark down whether we're a ladder stub or not.
        is_ladder = end.is_ladder()

        # See if we're a one-way connection or not
        stub_src_x = src_x
        stub_src_y = src_y
        if (conn.is_oneway_a() and room == conn.r1) or (conn.is_oneway_b() and room == conn.r2):
            is_oneway = True

            # If we're *also* a ladder, alter our main connection geometry a bit.
            if is_ladder:
                (stub_src_x, stub_src_y) = self.resize_line(
                        dst_x, dst_y, src_x, src_y,
                        length_change=-(Constants.conn_hover_size_half*.5))
        else:
            is_oneway = False

        # Draw the actual stub
        self.draw_conn_segment(stub_src_x, stub_src_y, dst_x, dst_y, end)

        # draw one-way connections.
        if is_oneway:
            for coords in self.arrow_coords(src_x, src_y, dst_x, dst_y, ladder=is_ladder):
                self.draw_conn_segment(coords[0], coords[1], src_x, src_y, end, ladder_arrow=is_ladder)

        # ... and return the destination point
        return (dst_x, dst_y)

    def draw_conn_segment(self, x1, y1, x2, y2, end, ladder_arrow=False):
        """
        Draws a connection segment from `(x1, y1)` to `(x2, y2)`, using the
        style provided by the passed-in ConnectionEnd `end`.  Ordinarily
        this is just a single line, but if `is_ladder` is True, then it'll
        build a Ladder graphic between the two, instead.

        If `ladder_arrow` is `True`, and our end type is a ladder, we'll
        draw an ordinary line (but with ladder thickness) rather than the
        full ladder structure.  This is used for drawing one-way arrows
        on ladder connections.
        """
        if end.is_ladder():
            if ladder_arrow:
                self.line(x1, y1, x2, y2, dashed=end.is_dotted(),
                        width=Constants.ladder_line_width)
            else:
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

            # Do some massaging of data if either side is both a ladder and
            # one-way, since we have to render that a bit differently than
            # everything else.
            main_x1 = x1
            main_y1 = y1
            main_x2 = x2
            main_y2 = y2
            if end_close.is_ladder() and conn.is_oneway_a():
                (main_x1, main_y1) = self.resize_line(
                        x2, y2, x1, y1,
                        length_change=-(Constants.conn_hover_size_half*.5))
            if end_far.is_ladder() and conn.is_oneway_b():
                (main_x2, main_y2) = self.resize_line(
                        x1, y1, x2, y2,
                        length_change=-(Constants.conn_hover_size_half*.5))

            if end_close.conn_type == end_far.conn_type:
                self.draw_conn_segment(main_x1, main_y1, main_x2, main_y2, end_close)
            else:
                midpoint_x = (x1 + x2) / 2
                midpoint_y = (y1 + y2) / 2
                self.draw_conn_segment(main_x1, main_y1, midpoint_x, midpoint_y, end_close)
                self.draw_conn_segment(midpoint_x, midpoint_y, main_x2, main_y2, end_far)
            if conn.is_oneway_a():
                is_ladder = end_close.is_ladder()
                for coords in self.arrow_coords(x1, y1, x2, y2, ladder=is_ladder):
                    self.draw_conn_segment(coords[0], coords[1], x1, y1, end_close, ladder_arrow=is_ladder)
            elif conn.is_oneway_b():
                is_ladder = end_far.is_ladder()
                for coords in self.arrow_coords(x2, y2, x1, y1, ladder=is_ladder):
                    self.draw_conn_segment(coords[0], coords[1], x2, y2, end_far, ladder_arrow=is_ladder)

        else:

            # Drawing our primary connection with stubs coming off the rooms and then
            # based on its render_type
            stub1 = self.draw_stub_conn(room1, dir1, conn)
            stub2 = self.draw_stub_conn(room2, dir2, conn)
            if stub1 and stub2:
                if end_close.is_render_midpoint_a():
                    secondary_midpoints[room1] = self.get_point_along_line(stub1[0], stub1[1],
                            stub1[0], stub2[1],
                            Constants.conn_secondary_connect_midpoint)
                    secondary_midpoints[room2] = self.get_point_along_line(stub2[0], stub2[1],
                            stub1[0], stub2[1],
                            Constants.conn_secondary_connect_midpoint)
                    self.draw_conn_segment(stub1[0], stub2[1], stub1[0], stub1[1], end_close)
                    self.draw_conn_segment(stub1[0], stub2[1], stub2[0], stub2[1], end_far)
                elif end_close.is_render_midpoint_b():
                    secondary_midpoints[room1] = self.get_point_along_line(stub1[0], stub1[1],
                            stub2[0], stub1[1],
                            Constants.conn_secondary_connect_midpoint)
                    secondary_midpoints[room2] = self.get_point_along_line(stub2[0], stub2[1],
                            stub2[0], stub1[1],
                            Constants.conn_secondary_connect_midpoint)
                    self.draw_conn_segment(stub2[0], stub1[1], stub1[0], stub1[1], end_close)
                    self.draw_conn_segment(stub2[0], stub1[1], stub2[0], stub2[1], end_far)
                else:
                    secondary_midpoints[room1] = self.get_point_along_line(stub1[0], stub1[1],
                            stub2[0], stub2[1],
                            Constants.conn_secondary_connect_regular)
                    secondary_midpoints[room2] = self.get_point_along_line(stub2[0], stub2[1],
                            stub1[0], stub1[1],
                            Constants.conn_secondary_connect_regular)
                    if end_close.conn_type == end_far.conn_type:
                        self.draw_conn_segment(stub1[0], stub1[1], stub2[0], stub2[1], end_close)
                    else:
                        midpoint_x = (stub1[0] + stub2[0]) / 2
                        midpoint_y = (stub1[1] + stub2[1]) / 2
                        self.draw_conn_segment(stub1[0], stub1[1], midpoint_x, midpoint_y, end_close)
                        self.draw_conn_segment(midpoint_x, midpoint_y, stub2[0], stub2[1], end_far)

        # And now draw any additional ends which may exist.  These will
        # always have stubs coming off of them, and will have their own
        # render_type describing how to connect to the main connection
        for end in conn.get_all_extra_ends():

            # First the stub
            stub = self.draw_stub_conn(end.room, end.direction, conn)

            # And then the rest of the connection
            if end.room in secondary_midpoints:
                (mid_x, mid_y) = secondary_midpoints[end.room]
                if end.is_render_midpoint_a():
                    self.draw_conn_segment(stub[0], mid_y, stub[0], stub[1], end)
                    self.draw_conn_segment(stub[0], mid_y, mid_x, mid_y, end)
                elif end.is_render_midpoint_b():
                    self.draw_conn_segment(mid_x, stub[1], stub[0], stub[1], end)
                    self.draw_conn_segment(mid_x, stub[1], mid_x, mid_y, end)
                else:
                    self.draw_conn_segment(stub[0], stub[1], mid_x, mid_y, end)

    def draw_loopback(self, gui_room, direction):
        """
        Draws a loopback onto a QGraphicsScene
        """
        coord = gui_room.get_global_connection_xy(direction)
        (orig_x2, orig_y2) = gui_room.get_opposite_room_conn_point(direction)
        fakeend = ConnectionEnd(None, None)

        if direction == DIR_NW or direction == DIR_NE or direction == DIR_SE or direction == DIR_SW:
            x2 = int((coord[0]*2+orig_x2)/3)
            y2 = int((coord[1]*2+orig_y2)/3)
        else:
            x2 = int((coord[0]*3+orig_x2*2)/5)
            y2 = int((coord[1]*3+orig_y2*2)/5)
        self.draw_conn_segment(coord[0], coord[1], x2, y2, fakeend)

        dx_orig = x2-coord[0]
        dy_orig = y2-coord[1]
        dist = math.sqrt(dx_orig**2 + dy_orig**2)
        dx = dx_orig / dist
        dy = dy_orig / dist

        x3 = x2 + (dist*dy)
        y3 = y2 - (dist*dx)
        self.draw_conn_segment(x2, y2, x3, y3, fakeend)

        x4 = coord[0] + (dist*dy)
        y4 = coord[1] - (dist*dx)
        self.draw_conn_segment(x4, y4, x3, y3, fakeend)
        for coord_arrow in self.arrow_coords(x3, y3, x4, y4, adjust=False):
            self.draw_conn_segment(coord_arrow[0], coord_arrow[1], x4, y4, fakeend)

class GUIGroup(QtWidgets.QGraphicsRectItem):
    """
    GUI representation of one of our room groups.
    """

    def __init__(self, group, scene):
        super().__init__()
        self.group = group
        self.scene = scene

        # Figure out the group geometry
        max_x = 0
        max_y = 0
        min_x = 9999
        min_y = 9999
        for room in group.get_rooms():
            gui_room = scene.room_to_gui[room]
            x = gui_room.gfx_x
            y = gui_room.gfx_y
            if (x < min_x):
                min_x = x
            if (x > max_x):
                max_x = x
            if (y < min_y):
                min_y = y
            if (y > max_y):
                max_y = y
        min_x -= Constants.group_padding
        min_y -= Constants.group_padding
        max_x += Constants.group_padding + Constants.room_size
        max_y += Constants.group_padding + Constants.room_size

        # And set our attributes
        if group.style in Constants.c_group_map:
            color = Constants.c_group_map[group.style]
        else:
            color = Constants.c_group_map[Group.STYLE_NORMAL]
        self.setRect(0, 0, max_x-min_x, max_y-min_y)
        self.setPos(min_x, min_y)
        self.setBrush(QtGui.QBrush(color))
        self.setPen(QtGui.QPen(color))
        self.setZValue(Constants.z_value_group)

class AboutDialog(QtWidgets.QDialog):
    """
    Dialog for showing an "About" style dialog.  Modelled after the one
    provided by Gtk; apparently I care?  Odd.
    """

    url = 'https://github.com/apocalyptech/advmap/'

    def __init__(self, parent, mapobj=None, maplist=None):
        super().__init__(parent)
        self.setModal(True)
        self.setSizeGripEnabled(True)
        # This attribute seems to be needed before we can return focus to the main
        # window...
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(400, 230)
        self.setWindowTitle('About Adventure Game Mapper')

        # Layout info
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Dialog Title
        title_label = QtWidgets.QLabel('Adventure Game Mapper v{}'.format(version), self)
        title_label.setStyleSheet('font-weight: bold; font-size: 12pt;')
        layout.addWidget(title_label, 0, QtCore.Qt.AlignCenter)

        # Link to project website (eventually)
        url_label = QtWidgets.QLabel('<a href="{}">{}</a>'.format(self.url, self.url))
        url_label.setOpenExternalLinks(True)
        layout.addWidget(url_label, 0, QtCore.Qt.AlignCenter)

        # Frame to contain icon credits
        frame = QtWidgets.QFrame()
        frame.setFrameShadow(frame.Sunken)
        frame.setFrameShape(frame.Panel)
        frame.setLineWidth(2)
        frame.setAutoFillBackground(True)
        layout.addWidget(frame)
        framelayout = QtWidgets.QVBoxLayout()
        frame.setLayout(framelayout)

        # Lighten up the background
        # TODO: should really figure out how to do the "appropriate" thing
        # given the style, rather than blindly ligtening
        pal = frame.palette()
        bgcolor = pal.color(pal.Window)
        pal.setColor(pal.Window, bgcolor.lighter())
        frame.setPalette(pal)

        # Icon credits
        icon_label = QtWidgets.QLabel("""<span>The monochome icons in the main toolbar are copyright
            <a href="http://www.axialis.com/free/icons/">Axialis Team</a>, available
            under <a href="http://creativecommons.org/licenses/by/2.5/">Creative
            Commons Attribution 2.5 Generic</a>.</span>""")
        icon_label.setOpenExternalLinks(True)
        icon_label.setWordWrap(True)
        icon_label.setFixedWidth(300)
        framelayout.addWidget(icon_label, 0, QtCore.Qt.AlignCenter)

        # More icon credits
        icon_label_2 = QtWidgets.QLabel("""<span>The other icons are designed by
            <a href="https://smashicons.com/">Smashicons</a>, from
            <a href="https://www.flaticon.com/authors/smashicons">Flaticon</a>, and
            are available via the Flaticon free license.</span>""")
        icon_label_2.setOpenExternalLinks(True)
        icon_label_2.setWordWrap(True)
        icon_label_2.setFixedWidth(300)
        framelayout.addWidget(icon_label_2, 1, QtCore.Qt.AlignCenter)

        # An HBox to contain two separate buttonboxes
        w = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        w.setLayout(hbox)
        layout.addWidget(w, 0)

        # Our custom button box
        style = self.style()
        self.custombb = QtWidgets.QDialogButtonBox(self)
        hbox.addWidget(self.custombb, 0, QtCore.Qt.AlignLeft)

        # License
        self.license = QtWidgets.QPushButton(Constants.gfx_icon_license, 'License')
        self.license.clicked.connect(self.open_license)
        self.custombb.addButton(self.license, self.custombb.ActionRole)

        # "Standard" Button box
        self.buttonbox = QtWidgets.QDialogButtonBox(parent=self)
        self.buttonbox.addButton(CloseButton(self), self.buttonbox.RejectRole)
        self.buttonbox.rejected.connect(self.reject)
        hbox.addWidget(self.buttonbox, 0, QtCore.Qt.AlignRight)

    def open_license(self, event):
        """
        User requested to open the license
        """
        d = LicenseDialog(self)
        d.exec()
        self.activateWindow()

class LicenseDialog(QtWidgets.QDialog):
    """
    Custom dialog class for showing our software license
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setModal(True)
        self.setSizeGripEnabled(True)
        # This attribute seems to be needed before we can return focus to the main
        # window...
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(600, 440)
        self.setWindowTitle('Adventure Game Mapper License')

        # Layout info
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Main place where we're showing the info
        self.browser = QtWidgets.QTextBrowser(self)
        layout.addWidget(self.browser, 1)
        cursor = self.browser.textCursor()
        self.set_scroll = False

        # Read in our license
        licensepath = self.parent().parent().reldir('COPYING.txt')
        license_text = 'ERROR: License data not found'
        if os.path.isfile(licensepath):
            try:
                with open(licensepath, 'r') as df:
                    license_text = df.read()
            except:
                pass
        self.browser.insertPlainText(license_text)

        # Button box
        self.buttonbox = QtWidgets.QDialogButtonBox(parent=self)
        self.buttonbox.addButton(CloseButton(self), self.buttonbox.RejectRole)
        self.buttonbox.rejected.connect(self.reject)
        layout.addWidget(self.buttonbox, 0, QtCore.Qt.AlignRight)

    def showEvent(self, event):
        """
        Events when the dialog is shown.  This is just here so that we can
        initially put our main text scrollbar at the top - setting the cursor
        position doesn't seem to do the trick, and the scrollbars don't have
        any size parameters yet when we initialize 'em.  I don't think it's
        possible for this to get triggered more than once per instantiation,
        since we're modal, but I'm guarding against setting it more than
        once anyway.
        """
        if not self.set_scroll:
            self.browser.verticalScrollBar().setValue(0)
            self.set_scroll = True
        super().showEvent(event)

class NotesDialog(QtWidgets.QDialog):
    """
    Custom dialog class for displaying room notes, either for
    the current map or for the aggregate of all maps
    """

    def __init__(self, parent, mapobj=None, maplist=None):
        super().__init__(parent)
        self.setModal(True)
        self.setSizeGripEnabled(True)
        # This attribute seems to be needed before we can return focus to the main
        # window...
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(420, 440)
        if mapobj is None:
            title = 'Room Notes (for all maps)'
        else:
            title = 'Room Notes (for {})'.format(mapobj.name)
        self.setWindowTitle(title)

        # Layout info
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Dialog Title
        title_label = QtWidgets.QLabel(title, self)
        title_label.setStyleSheet('font-weight: bold; font-size: 12pt;')
        layout.addWidget(title_label, 0, QtCore.Qt.AlignCenter)

        # Main place where we're showing the info
        self.browser = QtWidgets.QTextBrowser(self)
        self.browser.document().setDefaultStyleSheet("""
            .mapheader {
                font-weight: bold;
                text-align: center;
                font-size: large;
            }
            .roomheader {
            }
            .roomname {
                font-weight: bold;
            }
            .roomcoords {
                font-style: italic;
            }
            .roomnotes {
            }
            .nonotes {
                text-align: center;
                font-style: italic;
            }
        """)
        layout.addWidget(self.browser, 1)
        cursor = self.browser.textCursor()

        # Add info to the map
        if mapobj is not None:
            show_maps = [mapobj]
        elif maplist is None:
            show_maps = []
        else:
            show_maps = maplist

        # For some reason, I can't seem to usefully set <div> alignment using
        # stylesheets themselves.  The text always just uses the alignment of the
        # very first textblock, regardless of what I've set in CSS.  So, what we're
        # doing is setting a custom QTextBlockFormat when creating each block.
        # This actually is the only way I've found to set margins, too.  I think
        # the CSS processing there isn't as powerful as I'd hope?
        format_center = QtGui.QTextBlockFormat()
        format_center.setAlignment(QtCore.Qt.AlignHCenter)
        format_center.setBottomMargin(15)
        format_left = QtGui.QTextBlockFormat()
        format_left.setAlignment(QtCore.Qt.AlignLeft)
        format_indent = QtGui.QTextBlockFormat()
        format_indent.setAlignment(QtCore.Qt.AlignLeft)
        format_indent.setLeftMargin(20)
        format_indent.setBottomMargin(15)
        have_notes = False
        notes = {}
        for (idx, mapobj) in enumerate(show_maps):
            shown_header = False
            for room in sorted(mapobj.roomlist(), key=operator.methodcaller('name_sort_key')):
                if room and room.notes and room.notes != '':
                    have_notes = True
                    if not shown_header:
                        cursor.insertBlock(format_center)
                        self.browser.insertHtml('<div class="mapheader">Notes for {}</div>'.format(mapobj.name))
                        shown_header = True
                    cursor.insertBlock(format_left)
                    self.browser.insertHtml("""
                        <div class="roomheader">
                            <span class="roomname">{}</span>
                            <span class="roomcoords">at ({}, {})</span>
                        </div>""".format(
                        room.name, room.x+1, room.y+1,
                        ))
                    cursor.insertBlock(format_indent)
                    self.browser.insertHtml('<div class="roomnotes">{}</div>'.format(room.notes))
        if not have_notes:
            self.browser.insertHtml('<div class="nonotes"><br><br><br><br>(no notes)</div>')
        self.set_scroll = False

        # Button box
        self.buttonbox = QtWidgets.QDialogButtonBox(parent=self)
        self.buttonbox.addButton(CloseButton(self), self.buttonbox.RejectRole)
        self.buttonbox.rejected.connect(self.reject)
        layout.addWidget(self.buttonbox, 0, QtCore.Qt.AlignRight)

    def showEvent(self, event):
        """
        Events when the dialog is shown.  This is just here so that we can
        initially put our main text scrollbar at the top - setting the cursor
        position doesn't seem to do the trick, and the scrollbars don't have
        any size parameters yet when we initialize 'em.  I don't think it's
        possible for this to get triggered more than once per instantiation,
        since we're modal, but I'm guarding against setting it more than
        once anyway.
        """
        if not self.set_scroll:
            self.browser.verticalScrollBar().setValue(0)
            self.set_scroll = True
        super().showEvent(event)

class AppDialog(QtWidgets.QDialog):
    """
    Custom dialog class which provides a uniform look for all our popups
    """

    def __init__(self, parent, title, size_x, size_y, scrollable=False, use_cancel=True):
        super().__init__(parent)

        # Workaround for https://bugreports.qt.io/browse/QTBUG-63846
        # Rather than being fully modal (w/ ApplicationModal), use WindowModal
        #self.setModal(True)
        self.setWindowModality(QtCore.Qt.WindowModal)

        self.setSizeGripEnabled(True)
        # This attribute seems to be needed before we can return focus to the main
        # window...
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(size_x, size_y)
        self.setWindowTitle(title)
        self.cur_row = -1

        # Layout info
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Dialog Title
        title_label = QtWidgets.QLabel('{}'.format(title), self)
        title_label.setStyleSheet('font-weight: bold; font-size: 12pt;')
        layout.addWidget(title_label, 0, QtCore.Qt.AlignCenter)

        # Scrollable, if we've been told to
        if scrollable:

            scrollarea = QtWidgets.QScrollArea(self)
            scrollarea.setFrameShadow(scrollarea.Sunken)
            scrollarea.setFrameShape(scrollarea.Panel)
            scrollarea.setLineWidth(2)
            scrollarea.setMidLineWidth(2)
            scrollarea.setWidgetResizable(True)
            layout.addWidget(scrollarea, 1)

            # Main grid inside the scrollarea
            self.gridlayout = QtWidgets.QGridLayout(scrollarea)
            grid = QtWidgets.QWidget(scrollarea)
            grid.setLayout(self.gridlayout)
            scrollarea.setWidget(grid)

        else:

            # Main grid inside the vbox
            self.gridlayout = QtWidgets.QGridLayout()
            grid = QtWidgets.QWidget(self)
            grid.setLayout(self.gridlayout)
            layout.addWidget(grid, 1)

        # Button box
        self.buttonbox = QtWidgets.QDialogButtonBox(self)
        self.buttonbox.addButton(OKButton(self.buttonbox), self.buttonbox.AcceptRole)
        if use_cancel:
            self.buttonbox.addButton(CancelButton(self.buttonbox), self.buttonbox.RejectRole)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)
        layout.addWidget(self.buttonbox, 0, QtCore.Qt.AlignRight)

        # Construct the actual dialog contents
        self.create_contents()

        # Fix some grid sizing parameters
        self.gridlayout.setColumnStretch(1, 1)
        self.gridlayout.setRowStretch(self.cur_row, 1)

        # Set any defaults
        self.set_defaults()

    def create_contents(self):
        """
        Creating any contents we need.  Intended to be implemented in another
        class.
        """
        pass

    def set_defaults(self):
        """
        Setting any defaults we need.  Intended to be implemented in another
        class.
        """
        pass

    def add_label(self, text):
        """
        Adds a label to the lefthand side of our grid
        """
        self.cur_row += 1
        label = QtWidgets.QLabel('{}:'.format(text), self)
        label.setMargin(3)
        self.gridlayout.addWidget(label, self.cur_row, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        return label

    def add_text(self, text):
        """
        Adds textual (readonly) data, as a QLabel.  Returns the QLabel
        in case you'd like to apply extra formatting to it.
        """
        label = QtWidgets.QLabel(text)
        self.gridlayout.addWidget(label, self.cur_row, 1, QtCore.Qt.AlignLeft)
        return label

    def add_textbox(self, width=None):
        """
        Adds a textbox at the current row
        """
        edit = FirstLineEdit(self)
        # Our actual max length for strings in our file format is 65536
        edit.setMaxLength(200)
        if width:
            edit.setFixedWidth(width)
        self.gridlayout.addWidget(edit, self.cur_row, 1, QtCore.Qt.AlignLeft)
        return edit

    def add_checkbox(self, text):
        """
        Adds a checkbox at the current row
        """
        cb = HTMLCheckBox(text, self)
        self.gridlayout.addWidget(cb, self.cur_row, 1, QtCore.Qt.AlignLeft)
        return cb

    def add_plaintext_edit(self, width, height):
        """
        Adds a plaintext edit box
        """
        edit = QtWidgets.QPlainTextEdit(self)
        edit.setMinimumSize(QtCore.QSize(width, height))
        self.gridlayout.addWidget(edit, self.cur_row, 1, QtCore.Qt.AlignLeft)
        return edit

class MapListModel(QtGui.QStandardItemModel):
    """
    Custom Model for use with MapListTable.  The only reason why
    we're subclassing is to "fix" dragging and dropping to reorder
    rows.  Using the base class alone would allow the user to
    drag a row into the second cell, creating a new column and
    generally screwing up the data.
    """

    def dropMimeData(self, data, action, row, col, parent):
        """
        Override of `dropMimeData` which will force the `col` parameter
        to always be zero, so all drop actions will insert a new row
        the way we want, preventing any column expansion, etc.
        """
        return super().dropMimeData(data, action, row, 0, parent)

class MapListStyle(QtWidgets.QProxyStyle):
    """
    Custom style for our MapListTable to draw the between-row drop
    indicator across the entire row, instead of just across the single
    cell the user happens to be hovering over.
    """

    def drawPrimitive(self, element, option, painter, widget=None):
        if element == self.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
            option_new = QtWidgets.QStyleOption(option)
            option_new.rect.setLeft(0)
            if widget:
                option_new.rect.setRight(widget.width())
            option = option_new
        super().drawPrimitive(element, option, painter, widget)

class MapListTable(QtWidgets.QTableView):
    """
    Table which holds information about our list of maps.  We store
    two bits of data along with the map name colum: the map object
    itself, and that map object's current index in the main `maps`
    list.  We do this because as items get reordered by the user in
    the list, the QStandardItemModel makes copies of the objects,
    rather than keeping the reference the way it is (this probably
    means that the copies aren't "complete" - I bet they're just
    shallow copies.  See the Qt docs for `QStandardItem.clone` and
    related).  Anyway, we could certainly provide our own classes
    for the model, to take care of that stuff and provide real
    copies (either hooking into our `clone` function, or doing some
    finagling to just return the same object back), but it's easier
    to just contine checking by index, as we'd been doing on the
    Gtk+ version.
    """

    object_role = QtCore.Qt.UserRole + 1
    cur_idx_role = QtCore.Qt.UserRole + 2

    def __init__(self, parent, game):
        """
        Initialize
        """
        super().__init__(parent)
        self.game = game
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.setShowGrid(False)

        # Would be nice to figure out a way to do this without stylesheets,
        # I always feel as though I've lost when using CSS for this kind of
        # thing.  Anyway, this style is just to make sure that our room
        # count column doesn't bump up against the righthand side.
        self.setStyleSheet('QTableView::item { padding-right: .5em; }')

        # These vars are what enables our basic drag-n-drop reordering
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(self.InternalMove)
        self.setDragDropOverwriteMode(False)

        # Set up our style (this fixes the between-row drop indicator)
        self.setStyle(MapListStyle())

        # Set up our model (our custom model here enforces basic row moves only)
        self.model = MapListModel()
        self.setModel(self.model)

        # Add all our maps.  setDropEnabled(False) is important!
        for (idx, mapobj) in enumerate(self.game.maps):
            item_name = QtGui.QStandardItem(mapobj.name)
            item_name.setData(mapobj, self.object_role)
            item_name.setData(idx, self.cur_idx_role)
            item_name.setEditable(True)
            item_name.setDropEnabled(False)

            if len(mapobj.rooms) == 1:
                plural = ''
            else:
                plural = 's'
            item_rooms = QtGui.QStandardItem('{} room{}'.format(len(mapobj.rooms), plural))
            item_rooms.setEditable(False)
            item_rooms.setDropEnabled(False)

            self.model.appendRow([item_name, item_rooms])

        # Set up our column stretching parameters; this has to be done
        # after the columns already exist.
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        # For the vertical header, ResizeToContents nearly does what I want, but
        # make it so the rows word-wrap rather than getting truncated with ellipses.
        # If I use anything other than ResizeToContents, though, I can't style
        # the padding at all with CSS.  Lame.  So, instead, I'm setting a fixed
        # height based on some calculations done on GUI startup.
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(int(Constants.maplist_row_height))

class EditGameDialog(AppDialog):
    """
    Dialog for editing the main game properties (game name, map list, etc)
    """

    def __init__(self, parent, game):
        self.game = game
        super().__init__(parent, 'Game Editor', 400, 400)

    def create_contents(self):
        """
        Dialog contents
        """
        # Game Name
        self.add_label('Game Name')
        self.input_gamename = self.add_textbox(200)

        # Maps
        self.add_label('Maps')
        self.add_map_edit_vbox()

    def set_defaults(self):
        """
        Sets our defaults
        """
        self.input_gamename.setText(self.game.name)

    def add_map_edit_vbox(self):
        """
        Adds the vbox which contains the majority of this dialog's content
        """

        # First the vbox itself
        vbox = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        vbox.setLayout(layout)
        self.gridlayout.addWidget(vbox, self.cur_row, 1)

        # Then a label
        label = QtWidgets.QLabel('<i>Doubleclick to edit names, drag to reorder.</i>')
        layout.addWidget(label)

        # Now the actual QTableView
        self.table = MapListTable(self, self.game)
        layout.addWidget(self.table, 1)

        # Now an HBox to hold a couple of control buttons
        hbox = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        hbox.setLayout(hbox_layout)
        layout.addWidget(hbox)

        # Add Map button
        button = QtWidgets.QPushButton(Constants.gfx_icon_plus, 'Add Map')
        button.clicked.connect(self.add_map)
        hbox_layout.addWidget(button)
        button = QtWidgets.QPushButton(Constants.gfx_icon_minus, 'Remove Map')
        button.clicked.connect(self.remove_map)
        hbox_layout.addWidget(button)

        # Note about Undo/Redo
        undolabel = QtWidgets.QLabel("""<b>Note:</b> Hitting "OK" on this dialog will
            reset the undo/redo state.""")
        undolabel.setWordWrap(True)
        layout.addWidget(undolabel)

    def accept(self):
        """
        User hit "OK" on the dialog
        """

        # First update our game name
        mainwindow = self.parent()
        mainwindow.game.name = self.input_gamename.text()

        # Next, loop through our model to figure out any changes
        newmaps = []
        new_map_idx = 0
        found_cur_map = False
        model = self.table.model
        rowcount = model.rowCount()
        for rownum in range(rowcount):
            name_col = model.item(rownum, 0)
            map_name = name_col.text()
            map_obj = name_col.data(self.table.object_role)
            map_cur_idx = name_col.data(self.table.cur_idx_role)
            if map_obj is None:
                newmaps.append(mainwindow.create_new_map(map_name))
            else:
                if map_cur_idx == mainwindow.map_idx:
                    new_map_idx = rownum
                    found_cur_map = True
                mainwindow.game.maps[map_cur_idx].name = map_name
                newmaps.append(mainwindow.game.maps[map_cur_idx])
        mainwindow.game.replace_maps(newmaps)

        # Update our main map dropdown
        mainwindow.set_mapcombo()

        # Set our currently-selected map
        mainwindow.toolbar.mapcombo.setCurrentIndex(new_map_idx)

        # Clear out our undo/redo states
        mainwindow.clear_undo()

        # And finally, trigger a recreate
        mainwindow.scene.recreate()

        # Pass through so that our dialog returns properly
        super().accept()

    def add_map(self):
        """
        User would like to add a map
        """
        (mapname, status) = QtWidgets.QInputDialog.getText(self,
                'Create New Map',
                'Map Name:',
                text='New Map')
        if status:
            if mapname and mapname != '':
                item_name = QtGui.QStandardItem(mapname)
                item_name.setData(None, self.table.object_role)
                item_name.setEditable(True)
                item_name.setFlags(item_name.flags() ^ QtCore.Qt.ItemIsDropEnabled)

                item_rooms = QtGui.QStandardItem('0 rooms')
                item_rooms.setEditable(False)
                item_rooms.setFlags(item_rooms.flags() ^ QtCore.Qt.ItemIsDropEnabled)

                self.table.model.appendRow([item_name, item_rooms])

    def remove_map(self):
        """
        Removes a map
        """
        indexes = self.table.selectedIndexes()
        if len(indexes) > 0:
            mapcount = self.table.model.rowCount()
            if mapcount < 2:
                self.parent().dialog_error('Cannot delete map',
                        'You cannot delete the last map in a game',
                        parent=self)
            else:
                row = indexes[0].row()
                self.table.model.takeRow(row)

class RoomDetailsDialog(AppDialog):
    """
    Dialog for showing text information about a room (for readonly mode)
    """

    def __init__(self, parent, room):
        self.room = room
        super().__init__(parent, 'Room Details', 360, 270,
                scrollable=True, use_cancel=False)

    def create_contents(self):
        """
        Creates our contents
        """

        # Contents - Room Name
        self.add_label('Room Name')
        label = self.add_text(self.room.name)
        label.setText('<b>{}</b>'.format(self.room.name))

        # Room Type
        self.add_label('Room Type')
        self.add_text(self.room.TYPE_TXT[self.room.type])

        # Room Color
        self.add_label('Room Color')
        self.add_text(self.room.COLOR_TXT[self.room.color])

        # Directions
        for (data, eng) in [(self.room.up, 'Up'),
                (self.room.down, 'Down'),
                (self.room.door_in, 'In'),
                (self.room.door_out, 'Out'),
                ]:
            if data and data != '':
                self.add_label('"{}" Direction'.format(eng))
                self.add_text(data)

        # Notes
        self.set_notes_scroll = False
        if self.room.notes and self.room.notes != '':
            self.has_notes = True
            self.add_label('Notes')
            self.input_notes = self.add_plaintext_edit(210, 150)
            self.input_notes.setReadOnly(True)
            self.input_notes.setPlainText(self.room.notes)
        else:
            # If we don't have notes, we'll want a "dummy" row for
            # our auto-stretch configuration
            self.has_notes = False
            self.cur_row += 1
            self.add_text('')

    def showEvent(self, event):
        """
        Events when the dialog is shown.  This is just here so that we can
        initially put our notes scrollbar at the top - setting the cursor
        position doesn't seem to do the trick, and the scrollbars don't have
        any size parameters yet when we initialize 'em.  I don't think it's
        possible for this to get triggered more than once per instantiation,
        since we're modal, but I'm guarding against setting it more than
        once anyway.
        """
        if not self.set_notes_scroll and self.has_notes:
            self.input_notes.verticalScrollBar().setValue(0)
            self.set_notes_scroll = True
        super().showEvent(event)


class NewEditRoomDialog(AppDialog):
    """
    Main dialog for either adding a new room or editing an existing room.  Some
    fields in here depend on what "mode" we're in, though the majority of them
    are the same regardless.
    """

    def __init__(self, parent, editing=False, room=None,
            from_direction=None, x=None, y=None):
        """
        Initialize our dialog.  The various options here have multiple valid
        states, and we don't really enforce them - it'd be possible to call
        this in ways which result in weird behavior.  There's three basic
        functional ways to call it:
            1) Define `editing=False` (the default), and send in `room` and
               `from_direction`.  This is the action to add a new room,
               connected to an existing room on the map.
            2) Define `editing=False` (the default), and send in `x` and `y`.
               This is adding a new room at an arbitrary point on the map.
            3) Define `editing=True`, and set `room`.  This will be to edit
               an already-existing room.
        """
        if editing:
            title = 'Edit Room'
        else:
            title = 'New Room'
        self.editing = editing
        self.room = room
        self.from_direction = from_direction
        self.x = x
        self.y = y
        super().__init__(parent, title, 560, 670, scrollable=True)

    def create_contents(self):
        """
        Creates our contents
        """

        # Contents - Room Name
        self.add_label('Room Name')
        self.input_roomname = self.add_textbox(200)

        # Room Type
        self.add_label('Room Type')
        self.add_type_radios()

        # Room Color
        self.add_label('Room Color')
        self.add_color_radios()

        # Some connection-related data we'll only render when linking from an
        # existing room.
        if not self.editing and self.from_direction is not None:

            # Connect to direction
            self.add_label('Connect to Direction')
            self.input_connect_to_direction = self.add_connect_to_direction()

            # Connection Type
            self.add_label('Connection Type')
            self.add_conntype_radios()

            # Passage
            self.add_label('Passage')
            self.add_passage_radios()

        # Width options
        self.add_label('Width Options')
        self.input_offset_x = self.add_checkbox('Offset <i>(shift to the right)</i>')

        # Height options
        self.add_label('Height Options')
        self.input_offset_y = self.add_checkbox('Offset <i>(shift down)</i>')

        # Grouping widget choice depends on what exactly we're doing
        if not self.editing and self.from_direction is not None:

            # Group with previous
            self.add_label('Grouping')
            self.input_group_with_previous = self.add_checkbox('Group with previous room?')

        else:

            # Group dropdown
            self.add_label('Group With')
            self.input_group_with_dropdown = self.add_group_with_dropdown()

        # Up
        self.add_label('"Up" Direction')
        self.input_up = self.add_textbox(150)

        # Down
        self.add_label('"Down" Direction')
        self.input_down = self.add_textbox(150)

        # In
        self.add_label('"In" Direction')
        self.input_in = self.add_textbox(150)

        # Out
        self.add_label('"Out" Direction')
        self.input_out = self.add_textbox(150)

        # Notes
        self.add_label('Notes')
        self.input_notes = self.add_plaintext_edit(310, 150)

    def set_defaults(self):
        """
        Sets defaults for the dialog
        """

        room = self.room

        # Set defaults
        if self.editing:

            self.input_roomname.setText(room.name)

            # Room Type
            if room.type == Room.TYPE_FAINT:
                self.input_roomtype_faint.setChecked(True)
            elif room.type == Room.TYPE_DARK:
                self.input_roomtype_dark.setChecked(True)
            elif room.type == Room.TYPE_LABEL:
                self.input_roomtype_label.setChecked(True)
            elif room.type == Room.TYPE_CONNHELPER:
                self.input_roomtype_connhelper.setChecked(True)
            else:
                self.input_roomtype_normal.setChecked(True)

            # Room Color
            if room.color == Room.COLOR_GREEN:
                self.input_roomcolor_green.setChecked(True)
            elif room.color == Room.COLOR_BLUE:
                self.input_roomcolor_blue.setChecked(True)
            elif room.color == Room.COLOR_RED:
                self.input_roomcolor_red.setChecked(True)
            elif room.color == Room.COLOR_YELLOW:
                self.input_roomcolor_yellow.setChecked(True)
            elif room.color == Room.COLOR_PURPLE:
                self.input_roomcolor_purple.setChecked(True)
            elif room.color == Room.COLOR_CYAN:
                self.input_roomcolor_cyan.setChecked(True)
            elif room.color == Room.COLOR_ORANGE:
                self.input_roomcolor_orange.setChecked(True)
            else:
                self.input_roomcolor_bw.setChecked(True)

            # Offsets
            if room.offset_x:
                self.input_offset_x.setChecked(True)
            if room.offset_y:
                self.input_offset_y.setChecked(True)

            # Group membership
            if room.group:
                for group_room in room.group.get_rooms():
                    if group_room != room:
                        break
                idx = self.input_group_with_dropdown.findData(group_room)
                self.input_group_with_dropdown.setCurrentIndex(idx)

            # Text labels
            self.input_up.setText(room.up)
            self.input_down.setText(room.down)
            self.input_in.setText(room.door_in)
            self.input_out.setText(room.door_out)
            self.input_notes.setPlainText(room.notes)

            # Default focus to room name if it's still '(unexplored)', or
            # the notes field, otherwise.
            if room.unexplored():
                self.input_roomname.setFocus()
            else:
                self.input_notes.setFocus()
                curs = self.input_notes.textCursor()
                curs.movePosition(curs.End, curs.MoveAnchor)
                self.input_notes.setTextCursor(curs)

        else:
            self.input_roomname.setFocus()
            self.input_roomname.setText(Room.unexplored_text)
            self.input_roomtype_normal.setChecked(True)
            self.input_roomcolor_bw.setChecked(True)
            if self.from_direction is not None:
                self.input_connect_to_direction.setCurrentIndex(DIR_OPP[self.from_direction])
                self.input_conntype_regular.setChecked(True)
                self.input_passage_twoway.setChecked(True)
            if room is not None:
                if room.offset_x:
                    self.input_offset_x.setChecked(True)
                if room.offset_y:
                    self.input_offset_y.setChecked(True)
                if room.group:
                    self.input_group_with_previous.setChecked(True)

    def add_type_radios(self):
        """
        Adds our Room Type radio buttons
        """
        w = QtWidgets.QWidget(self)
        l = QtWidgets.QGridLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        w.setLayout(l)
        self.gridlayout.addWidget(w, self.cur_row, 1, QtCore.Qt.AlignLeft)

        self.input_roomtype_normal = QtWidgets.QRadioButton('Normal', w)
        l.addWidget(self.input_roomtype_normal, 0, 0)

        self.input_roomtype_faint = QtWidgets.QRadioButton('Faint', w)
        l.addWidget(self.input_roomtype_faint, 0, 1)

        self.input_roomtype_dark = QtWidgets.QRadioButton('Dark', w)
        l.addWidget(self.input_roomtype_dark, 0, 2)

        self.input_roomtype_label = HTMLRadioButton('Label <i>(Only Room Name is shown)</i>', w)
        l.addWidget(self.input_roomtype_label, 1, 0, 1, 3)

        self.input_roomtype_connhelper = HTMLRadioButton('Connection Helper <i>(no text is shown)</i>', w)
        l.addWidget(self.input_roomtype_connhelper, 2, 0, 1, 3)

    def add_color_radios(self):
        """
        Adds our Room Color radio buttons
        """
        w = QtWidgets.QWidget(self)
        l = QtWidgets.QGridLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        w.setLayout(l)
        self.gridlayout.addWidget(w, self.cur_row, 1, QtCore.Qt.AlignLeft)

        self.input_roomcolor_bw = QtWidgets.QRadioButton('B/W', w)
        l.addWidget(self.input_roomcolor_bw, 0, 0)

        self.input_roomcolor_green = QtWidgets.QRadioButton('Green', w)
        l.addWidget(self.input_roomcolor_green, 0, 1)

        self.input_roomcolor_blue = QtWidgets.QRadioButton('Blue', w)
        l.addWidget(self.input_roomcolor_blue, 0, 2)

        self.input_roomcolor_red = QtWidgets.QRadioButton('Red', w)
        l.addWidget(self.input_roomcolor_red, 0, 3)

        self.input_roomcolor_yellow = QtWidgets.QRadioButton('Yellow', w)
        l.addWidget(self.input_roomcolor_yellow, 1, 0)

        self.input_roomcolor_purple = QtWidgets.QRadioButton('Purple', w)
        l.addWidget(self.input_roomcolor_purple, 1, 1)

        self.input_roomcolor_cyan = QtWidgets.QRadioButton('Cyan', w)
        l.addWidget(self.input_roomcolor_cyan, 1, 2)

        self.input_roomcolor_orange = QtWidgets.QRadioButton('Orange', w)
        l.addWidget(self.input_roomcolor_orange, 1, 3)

    def add_connect_to_direction(self):
        """
        Adds our connect-to-direction dropdown.  This is used when we've clicked
        on an empty connection on the side of a room, and will end up defaulting
        to the opposite direction.
        """
        cb = QtWidgets.QComboBox(self)
        for direction in DIR_LIST:
            cb.addItem(DIR_2_TXT[direction], direction)
        self.gridlayout.addWidget(cb, self.cur_row, 1, QtCore.Qt.AlignLeft)
        return cb

    def add_conntype_radios(self):
        """
        Adds our Connection Type radio buttons
        """
        w = QtWidgets.QWidget(self)
        l = QtWidgets.QGridLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        w.setLayout(l)
        self.gridlayout.addWidget(w, self.cur_row, 1, QtCore.Qt.AlignLeft)

        self.input_conntype_regular = QtWidgets.QRadioButton('Regular', w)
        l.addWidget(self.input_conntype_regular, 0, 0)

        self.input_conntype_ladder = QtWidgets.QRadioButton('Ladder', w)
        l.addWidget(self.input_conntype_ladder, 0, 1)

        self.input_conntype_dotted = QtWidgets.QRadioButton('Dotted', w)
        l.addWidget(self.input_conntype_dotted, 0, 2)

        self.input_conntype_none = QtWidgets.QRadioButton('None', w)
        l.addWidget(self.input_conntype_none, 0, 3)

    def add_passage_radios(self):
        """
        Adds our Passage radio buttons
        """
        w = QtWidgets.QWidget(self)
        l = QtWidgets.QGridLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        w.setLayout(l)
        self.gridlayout.addWidget(w, self.cur_row, 1, QtCore.Qt.AlignLeft)

        self.input_passage_twoway = QtWidgets.QRadioButton('Two-Way', w)
        l.addWidget(self.input_passage_twoway, 0, 0)

        self.input_passage_oneway_in = QtWidgets.QRadioButton('One-Way Into New Room', w)
        l.addWidget(self.input_passage_oneway_in, 0, 1)

        self.input_passage_oneway_out = QtWidgets.QRadioButton('One-Way Out', w)
        l.addWidget(self.input_passage_oneway_out, 0, 2)

    def add_group_with_dropdown(self):
        """
        Adds a group-with dropdown.  This will omit any rooms already in
        a different group than us.
        """
        scene = self.parent().scene
        cb = HTMLComboBox(self)
        cb.addItem('-', None)
        cur_group = None
        if self.room:
            cur_group = self.room.group
        for room in sorted(scene.mapobj.roomlist(), key=operator.methodcaller('name_sort_key')):
            if room == self.room:
                continue
            if room.group and cur_group and room.group != cur_group:
                continue
            cb.addItem('<b>{}</b><i> at ({}, {})</i>'.format(room.name, room.x+1, room.y+1), room)
        self.gridlayout.addWidget(cb, self.cur_row, 1, QtCore.Qt.AlignLeft)
        return cb

    def accept(self):
        """
        User hit "OK", so go ahead and change whatever needs changing.
        """
        scene = self.parent().scene
        if self.editing:
            oper_room = self.room
            oper_room.name = self.input_roomname.text()
        else:
            if self.room:
                (self.x, self.y) = scene.mapobj.dir_coord(self.room, self.from_direction)

            # Create the new room
            try:
                oper_room = scene.mapobj.add_room_at(self.x, self.y, self.input_roomname.text())
            except Exception as e:
                self.parent().dialog_error('Unable to add new room', str(e), parent=self)
                return self.reject()

            # If we started with a room, link the two (if told to)
            if self.room:
                if not self.input_conntype_none.isChecked():
                    new_dir = self.input_connect_to_direction.currentData()
                    newconn = scene.mapobj.connect(self.room, self.from_direction, oper_room, new_dir)

                    # Connection type
                    if self.input_conntype_ladder.isChecked():
                        newconn.set_ladder(oper_room, new_dir)
                    elif self.input_conntype_dotted.isChecked():
                        newconn.set_dotted(oper_room, new_dir)

                    # Passage
                    if self.input_passage_oneway_in.isChecked():
                        newconn.set_oneway_b()
                    elif self.input_passage_oneway_out.isChecked():
                        newconn.set_oneway_a()

        # Room Type
        if self.input_roomtype_faint.isChecked():
            oper_room.type = Room.TYPE_FAINT
        elif self.input_roomtype_dark.isChecked():
            oper_room.type = Room.TYPE_DARK
        elif self.input_roomtype_label.isChecked():
            oper_room.type = Room.TYPE_LABEL
        elif self.input_roomtype_connhelper.isChecked():
            oper_room.type = Room.TYPE_CONNHELPER
        else:
            oper_room.type = Room.TYPE_NORMAL

        # Room Color
        if self.input_roomcolor_green.isChecked():
            oper_room.color = Room.COLOR_GREEN
        elif self.input_roomcolor_blue.isChecked():
            oper_room.color = Room.COLOR_BLUE
        elif self.input_roomcolor_red.isChecked():
            oper_room.color = Room.COLOR_RED
        elif self.input_roomcolor_yellow.isChecked():
            oper_room.color = Room.COLOR_YELLOW
        elif self.input_roomcolor_purple.isChecked():
            oper_room.color = Room.COLOR_PURPLE
        elif self.input_roomcolor_cyan.isChecked():
            oper_room.color = Room.COLOR_CYAN
        elif self.input_roomcolor_orange.isChecked():
            oper_room.color = Room.COLOR_ORANGE
        else:
            oper_room.color = Room.COLOR_BW

        # Offsets
        oper_room.offset_x = self.input_offset_x.isChecked()
        oper_room.offset_y = self.input_offset_y.isChecked()

        # Assign group membership
        if self.editing:
            # Previously-existing room.
            group_room = self.input_group_with_dropdown.currentData()
            if group_room:
                # Room specified - do the grouping
                scene.mapobj.group_rooms(oper_room, group_room)
            else:
                # No room selected in dropdown - remove group if one exists
                scene.mapobj.remove_room_from_group(oper_room)
        else:
            if self.room is None:
                # Completely new room grouping to another room - just go ahead and do it
                group_room = self.input_group_with_dropdown.currentData()
                if group_room:
                    scene.mapobj.group_rooms(oper_room, group_room)
            else:
                # Grouping a new room to the previous room's group - just go ahead and do it
                if self.input_group_with_previous.isChecked():
                    scene.mapobj.group_rooms(self.room, oper_room)

        # Text Labels
        oper_room.up = self.input_up.text()
        oper_room.down = self.input_down.text()
        oper_room.door_in = self.input_in.text()
        oper_room.door_out = self.input_out.text()
        oper_room.notes = self.input_notes.toPlainText()

        super().accept()

class MapScene(QtWidgets.QGraphicsScene):
    """
    Our main scene which contains all our graphic elements.  Also
    keeps track of rooms we've selected, and the state of any
    two-step operation we're doing.
    """

    def __init__(self, parent, mainwindow):

        super().__init__(parent)

        self.mapobj = None
        self.mainwindow = mainwindow

        # Keep track of what's currently hovering in the scene
        self.hover_current = None

        # Keep track of whether we're currently dragging
        self.dragging = False
        self.dragged = False

        # Keep track of current room selection
        self.clear_selected()

        # Vars to keep track of two-step actions
        self.clear_two_step_actions()

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

    def clear_selected(self):
        """
        Deselects everything we may have selected.  Does NOT trigger a
        redraw/recreate itself
        """
        self.selected = set()
        self.mainwindow.update_copy_menu()

    def set_map(self, mapobj):
        """
        Sets the current map in use
        """
        self.clear_selected()
        self.mapobj = mapobj
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
        self.parent().viewport().update()
        self.hover_end()

        # Recreate our available multi-select options, if we have any
        self.populate_multi_select_actions()

        # Set our scene size
        total_w = (Constants.room_space + Constants.room_size)*self.mapobj.w + Constants.room_space
        total_h = (Constants.room_space + Constants.room_size)*self.mapobj.h + Constants.room_space
        self.setSceneRect(QtCore.QRectF(0, 0, total_w, total_h))

        # First draw a white background
        rect = self.addRect(0, 0, self.width(), self.height(),
            QtGui.QPen(Constants.c_background),
            QtGui.QBrush(Constants.c_background),
            )
        rect.setZValue(Constants.z_value_background)

        # Now grid lines, if we've been told to
        if self.mainwindow.toolbar.grid_toggle.isChecked():
            for x in [Constants.room_space_half + i*(Constants.room_size + Constants.room_space) for i in range(self.mapobj.w+1)]:
                l = self.addLine(x, 0, x, total_h, QtGui.QPen(Constants.c_grid))
                l.setZValue(Constants.z_value_background)
            for y in [Constants.room_space_half + i*(Constants.room_size + Constants.room_space) for i in range(self.mapobj.h+1)]:
                l = self.addLine(0, y, total_w, y, QtGui.QPen(Constants.c_grid))
                l.setZValue(Constants.z_value_background)

        # Create a GUIConnectionGenerator, used to draw connections and
        # loopbacks
        cf = GUIConnectionGenerator(self)

        # TODO: It shouldn't be possible to have selected rooms disappear
        # on us during a recreate, but it wouldn't hurt to check for it
        # First render our rooms
        self.room_to_gui = {}
        for x in range(self.mapobj.w):
            for y in range(self.mapobj.h):
                room = self.mapobj.get_room_at(x, y)
                if room:
                    guiroom = GUIRoom(room, self.parent().mainwindow)
                    self.addItem(guiroom)
                    guiroom.check_keep_hover_connections(keep_hover)
                    self.room_to_gui[room] = guiroom
                    if keep_hover == room:
                        guiroom.hover_obj.hoverEnterEvent()
                    for direction in DIR_LIST:
                        if room.get_loopback(direction):
                            cf.draw_loopback(guiroom, direction)
                else:
                    if not self.mainwindow.is_readonly():
                        newroom = GUINewRoom(x, y, self.parent().mainwindow)
                        self.addItem(newroom)
                        if keep_hover == (x, y):
                            newroom.hover_obj.hoverEnterEvent()

        # Next all the connections
        for conn in self.mapobj.conns:
            cf.draw_connection(conn)

        # Draw in our room groups
        for group in self.mapobj.groups:
            guigroup = GUIGroup(group, self)
            self.addItem(guigroup)

        # If we haven't re-hovered anything, revert to our default hover text
        if not self.hover_current:
            self.default_actions()

    def default_actions(self):
        """
        Actions to show when we're not hovering on anything.
        """
        # Abusing our HoverArea class to do this; it'll pull in multi-select
        # options automatically
        actions = HoverArea(None, self.mainwindow)
        actions.add_label_action('LMB', 'click-and-drag')
        actions.show_actions(self)

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
            self.clear_selected()
            self.recreate()
            if not self.hover_current:
                self.default_actions()
        self.dragged = False

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

    def get_group_info(self, roomset):
        """
        Given a set of rooms, return some information about the aggregate group
        membership of the rooms.  Specifically, we will return a tuple with the
        following:

            1) Number of rooms with no group
            2) Number of unique groups seen
            3) One of the groups seen, if possible
        """
        seen_groups = set()
        no_groups = 0
        group = None
        for room in roomset:
            if room.group:
                seen_groups.add(room.group)
                group = room.group
            else:
                no_groups += 1
        return (no_groups, len(seen_groups), group)

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
        self.mainwindow.update_copy_menu()

    def select_all(self):
        """
        Select all rooms in the map
        """
        self.selected = set()
        for room in self.mapobj.roomlist():
            self.selected.add(room)
        self.mainwindow.update_copy_menu()

    def is_selected(self, room):
        """
        Checks to see if the given Room is selected
        """
        if room in self.selected:
            return True
        else:
            return False

    def start_two_step_action(self, text):
        """
        Global things to do when we start a two-step action.  At the moment
        this is just setting the application cursor so there's a bit more visual
        feedback that something's going on, and setting our status text.
        """
        # PointingHandCursor is also all right, though I think I prefer CrossCursor
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mainwindow.statusbar.set_two_step_text(text)

    def clear_two_step_actions(self):
        """
        Clears the vars used to store our two-step process state
        """
        self.two_step_group_first = None
        self.two_step_move_connection = None
        self.two_step_add_extra = None
        self.two_step_new_connection = None
        self.mainwindow.statusbar.clear_two_step_text()
        QtWidgets.QApplication.restoreOverrideCursor()

    def have_two_step_action(self):
        """
        Returns a boolean to indicate whether we're in the middle of
        a two-step operation or not.
        """
        return (self.two_step_group_first is not None
                or self.two_step_move_connection is not None
                or self.two_step_add_extra is not None
                or self.two_step_new_connection is not None
                )

    def populate_multi_select_actions(self):
        """
        Populates our list of multi-select actions, if appropriate.  We're
        abusing our HoverArea object a little bit to do this
        """
        self.multi_select_actions = HoverArea(None, self.mainwindow, multi=True)
        if self.has_selections() and not self.mainwindow.is_readonly():
            self.multi_select_actions.add_key_action('WASD', 'nudge rooms',
                    ['w', 'a', 's', 'd'], self.multi_nudge_rooms,
                    [[DIR_N], [DIR_W], [DIR_S], [DIR_E]],
                    ['Nudge Rooms to N', 'Nudge Rooms to W',
                        'Nudge Rooms to S', 'Nudge Rooms to E'])
            self.multi_select_actions.add_key_action('H/V', 'toggle horiz/vert offsets',
                    ['h', 'v'], self.multi_toggle_offsets, [[False], [True]],
                    ['Toggle Rooms Horizontal Offset', 'Toggle Rooms Vertical Offset'])
            self.multi_select_actions.add_key_action('T', 'change types',
                    ['t'], self.multi_change_types, [[]], ['Change Room Types'])
            self.multi_select_actions.add_key_action('R', 'change colors',
                    ['r'], self.multi_change_colors, [[]], ['Change Room Colors'])
            if len(self.selected) > 1:
                (num_nogroup, num_unique_groups, group) = self.get_group_info(self.selected)
                if num_nogroup == 0:
                    if num_unique_groups == 1:
                        self.multi_select_actions.add_key_action('G', 'change group render',
                                ['g'], self.multi_change_group_render, [[group]],
                                ['Change Group Render Color'])
                else:
                    if num_unique_groups < 2:
                        self.multi_select_actions.add_key_action('G', 'group selected',
                                ['g'], self.multi_group_selected, [[group]],
                                ['Group Selected Rooms'])

                if num_unique_groups > 0:
                    self.multi_select_actions.add_key_action('O', 'ungroup selected',
                            ['o'], self.multi_ungroup_selected, [[]], ['Ungroup Rooms'])
            else:
                selected_room = next(iter(self.selected))
                if selected_room.group:
                    self.multi_select_actions.add_key_action('G', 'change group render',
                            ['g'], self.multi_change_group_render, [[selected_room.group]],
                            ['Change Group Render Color'])
                    self.multi_select_actions.add_key_action('O', 'ungroup selected',
                            ['o'], self.multi_ungroup_selected, [[]], ['Ungroup Rooms'])

    def keyPressEvent(self, event):
        """
        Keyboard input
        """
        doing_two_step = self.have_two_step_action()
        if self.has_selections():
            self.multi_select_actions.keyPressEvent(event, self)
        else:
            super().keyPressEvent(event)
            # If we got here and we were previously doing a two-step
            # action, we shouldn't be doing it anymore.
            if doing_two_step:
                self.clear_two_step_actions()


    def multi_nudge_rooms(self, direction):
        """
        Nudge our selected rooms in the specified direction
        """
        if self.mapobj.nudge(direction, self.selected):
            self.recreate()
            return True
        else:
            return False

    def multi_toggle_offsets(self, vertical=False):
        """
        Toggles x/y offsets on selected rooms, defaulting to horizontal
        unless `vertical` is passed in as `True`.
        """
        num_offset = 0
        num_not_offset = 0
        for room in self.selected:
            if vertical:
                if room.offset_y:
                    num_offset += 1
                else:
                    num_not_offset += 1
            else:
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
            if vertical:
                room.offset_y = set_value
            else:
                room.offset_x = set_value
        self.recreate()
        return True

    def multi_change_types(self):
        """
        Change the room type of all our selected rooms
        """
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
        self.recreate()
        return True

    def multi_change_colors(self):
        """
        Change the room color of all our selected rooms
        """
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
        self.recreate()
        return True

    def multi_change_group_render(self, group):
        """
        Change the group render style for the group
        """
        group.increment_style()
        self.recreate()
        return True

    def multi_group_selected(self, group):
        """
        Groups the selected rooms together into the given
        group.
        """
        if group:
            for room in self.selected:
                group.add_room(room)
        else:
            roomlist = list(self.selected)
            for room in roomlist[1:]:
                self.mapobj.group_rooms(roomlist[0], room)
        self.recreate()
        return True

    def multi_ungroup_selected(self):
        """
        Ungroup the selected rooms
        """
        need_gfx_update = False
        for room in self.selected:
            if self.mapobj.remove_room_from_group(room):
                need_gfx_update = True
        if need_gfx_update:
            self.recreate()
            return True
        else:
            return False

class MapArea(QtWidgets.QGraphicsView):
    """
    Class which holds the viewport into our scene.  Not much
    happens in this class - there's stuff which perhaps
    *should* be part of this class which is instead part of
    our MainWindow classes, but I don't really feel like ripping
    that stuff apart.
    """

    statusbar = QtCore.pyqtSignal(str)

    def __init__(self, parent):

        super().__init__(parent)
        self.mainwindow = parent
        # If we notice issues with text rendering in the
        # future, 'or' in the TextAntialiasing hint too
        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.scene = MapScene(self, parent)
        self.setScene(self.scene)
        self.setBackgroundBrush(QtGui.QBrush(Constants.c_background_out_of_scene))
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
