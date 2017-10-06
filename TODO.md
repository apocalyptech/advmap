Bugs to fix:

 * If one of these Qt bugs ever gets fixed:
    https://bugreports.qt.io/browse/QTBUG-63322
    https://bugreports.qt.io/browse/QTBUG-63386
   ... get rid of our `draw_dashed_line` function and go back to
   using setDashPattern() like I'd love to be doing.

 * There's some very minor rendering oddities I'd like to get sorted out
   at some point - We improved our border strength recently, which looks
   fine, but it would be nice to figure out getting those to draw a single
   pixel wide instead of the 2 they are now.  Also, the intersections of
   each side of the rect on our GUIRoom doesn't "meet up" the way I'd 
   hope.  If you zoom in to a screenshot, you can see easily where the
   two brush strokes meet and leave a tiny gap at the corners.

 * I think that scrollbar positioning doesn't Do The Right Thing when
   processing undo/redo - look in to that and make sure we're not
   recentering inappropriately, etc.

 * Also, would be nice if the New/Quit/Revert confirmation dialogs don't
   show up when the user hasn't made any changes.  We'll have to be a *bit*
   fuzzy about that 'cause our undo/redo doesn't take into account potential
   changes on the Game Edit dialog, and we'd have to figure out a way to
   know when we're at a certain map state, but I'd think it would be doable.

Features to implement:

 * Write whole set of game maps out to PNGs.  I assume it only makes sense
   to do that into separate files.

 * Extra connection drawing styles, such as "rounded".  That could be
   interesting, though, since all our current code (such as with dashed
   lines) assumes straight lines.

 * Popup when LMB on a connection to edit conn attributes (should be much
   more manageable than our previous Advanced tab on Room Edit)

 * I'd really like to start unit-testing the GUI; apparently there
   *is* a QTest class, or something, which can assist with this.

 * QInputDialog.getText() doesn't let you specify custom buttons; would
   be nice to use our standard ones with icons, so I may need to write
   my own class to do that.
 
 * User-editable keybindings.  I suspect I'd probably never get to the
   point of having a preferences menu for it, but at least having a config
   file would be nice.
 
 * For connections which end up being at least partially a straight line,
   pretend that the relevant stubs don't exist and instead draw a straight
   line all the way through.  Not that our dotted/ladder connections look
   *bad* the way they currently are, but there's a noticeable change
   between the stub area and the main connection area, when the connection
   is straight.

 * Indication of how many rooms are selected, in our secondary info area,
   until now only used for two-step actions.  This may actually be
   trickyish, though, 'cause we CAN do some two-step actions with rooms
   selected.  Perhaps we shouldn't be able to?

Things to consider:

 * Should we still be able to edit Notes in readonly mode?

 * Connections involving more than two rooms?  I'm not sure if it'd be
   worth putting that together, though there's a few cases where it could
   technically come in handy, such as the bank puzzle in Zork II, or the
   opening loop of Shay's section in Broken Age.  Those are definitely
   corner cases, though, and I suspect I won't find it worth the effort to
   expand this functionality.  Those cases generally benefit from a
   Label-type room to provide extra info in the middle anyway.

 * Double-sized rooms, or even arbitrarily-large room.  Sort of a
   super-group where the room itself takes over space instead of just
   the background notification

 * Our current handling of QGraphicsScene/QGraphicsView owes a lot to how
   we were handling things back in the Gtk+ version - namely, that when
   changes occur to the data, we trigger a complete recreation of the
   entire scene, rather than try to keep track of changes.  The datasets
   involved here are small enough by modern computer standards that it
   doesn't really matter, but it's still pretty inefficient.  Really we
   should be just updating what's changed and keeping the rest of the scene
   intact.  That's more work than I cared to deal with, since we'd have a
   lot of QGraphicsFooItems lying around all over the place, but it's
   something to consider for the future.

 * It would probably make sense to move from a custom binary savefile
   format to using gzipped JSON or something.

