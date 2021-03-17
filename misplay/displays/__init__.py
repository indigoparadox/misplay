
import time
import logging
from misplay.panels.panel import RowsPanel # pylint: disable=import-error,no-name-in-module

#class RefreshException( Exception ):
#    pass

class Misplay( object ):

    def __init__( self, refresh, w, h, r, margins, panels, font, size ):

        self.logger = logging.getLogger( 'misplay' )

        # Setup wallpaper timers.
        self.last_update = int( time.time() )
        self.refresh = float( refresh )
        self.w = int( w )
        self.h = int( h )
        self.rotate = int( r )
        self.margins = int( margins )
        self.panels = panels
        self.font_family = font
        self.font_size = int( size )
        self._populate_panels( self.panels, 0, 0 )

    def stop( self ):
        for pnl in self.panels:
            pnl.stop()
        self.clear()

    def _populate_panels( self, panels, x_iter, y_iter, parent_width=0 ):
        if 0 >= parent_width:
            parent_width = self.w
        last_width = 0
        for panel in panels:
            if isinstance( panel, RowsPanel ):
                y_iter = self.margins
                x_iter += last_width
                x_iter += self.margins
                self.logger.debug( 'populating %s at %d, %d...',
                    type( panel ), x_iter, y_iter )
                self._populate_panels( panel.rows, x_iter, y_iter, panel.w )
            elif panel:
                self.logger.debug( 'populating %s at %d, %d...',
                    type( panel ), x_iter, y_iter )
                panel.display = self
                panel.x = x_iter
                panel.y = y_iter

                # Panels are rows by default, so increment Y.
                y_iter += panel.h
                y_iter += self.margins

            if 0 == panel.w:
                self.logger.debug( 'auto-setting panel width to %d',
                    parent_width )
                panel.w = parent_width

            last_width = panel.w

    def _update_panels( self, panels, elapsed ):
        for panel in panels:
            self.logger.debug( 'updating panel...' )
            if isinstance( panel, RowsPanel ):
                self._update_panels( panel.rows, elapsed )
            elif panel:
                panel.update( elapsed )

    def clear( self ):
        pass

    def image( self, path, pos, width, height ):
        pass

    def blank( self, x, y, w, h, fill ):
        pass

    def text( self, text, font_family, font_size, position ):
        pass

    def flip( self ):
        pass

    def loop( self ):
        while( True ):
            seconds = int( time.time() )
            elapsed = seconds - self.last_update
            self.last_update = int( time.time() )
            self.logger.debug( '%d seconds elapsed', elapsed )

            try:
                self._update_panels( self.panels, elapsed )

                self.flip()
            except Exception as exc: # pylint: disable=broad-except
                self.logger.error( '%s during refresh: %s', type( exc ), exc )

            # Sleep.
            self.logger.debug(
                'sleeping for %d seconds...', self.refresh )
            time.sleep( self.refresh )
