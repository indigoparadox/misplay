
import os
import time
import logging
from misplay.panels.panel import RowsPanel

FIFO_Y = 60

class RefreshException( Exception ):
    pass

class Misplay( object ):

    def __init__( self, refresh, w, h, r, mx, my, panels ):

        logger = logging.getLogger( 'misplay.init' )

        # Setup wallpaper timers.
        self.last_update = int( time.time() )
        self.refresh = refresh
        self.w = w
        self.h = h
        self.rotate = r
        self.margin_x = mx
        self.margin_y = my
        self.panels = panels
        self._populate_panels( self.panels, 0, 0 )

    def _populate_panels( self, panels, x_iter, y_iter, parent_width=0 ):
        logger = logging.getLogger( 'misplay.panels' )
        if 0 >= parent_width:
            parent_width = self.w
        last_width = 0
        for panel in panels:
            if isinstance( panel, RowsPanel ):
                y_iter = 0
                x_iter += last_width
                logger.debug( 'populating {} at {}, {}...'.format(
                    type( panel ), x_iter, y_iter ) )
                self._populate_panels( panel.rows, x_iter, y_iter, panel.w )
            elif panel:
                logger.debug( 'populating {} at {}, {}...'.format(
                    type( panel ), x_iter, y_iter ) )
                panel.display = self
                panel.x = x_iter
                panel.y = y_iter

                # Panels are rows by default, so increment Y.
                y_iter += panel.h
                last_width = panel.w

    def _update_panels( self, panels, elapsed ):
        logger = logging.getLogger( 'misplay.panels' )
        for panel in panels:
            logger.debug( 'updating panel...' )
            if isinstance( panel, RowsPanel ):
                self._update_panels( panel.rows, elapsed )
            elif panel:
                panel.update( elapsed )

    def clear( self ):
        pass

    def image( self, path, pos, width, height, erase ):
        pass

    def blank( self, x, y, w, h, draw, fill ):
        pass
    
    def text( self, text, font_family, font_size, position, erase ):
        pass

    def flip( self ):
        pass

    def loop( self ):

        logger = logging.getLogger( 'misplay.loop' )

        while( True ):
            seconds = int( time.time() )
            elapsed = seconds - self.last_update
            self.last_update = int( time.time() )
            logger.debug( '{} seconds elapsed'.format( elapsed ) )

            self._update_panels( self.panels, elapsed )

            self.flip()

            # Sleep.
            logger.debug( 'sleeping for {} seconds...'.format( self.refresh ) )
            time.sleep( self.refresh )


