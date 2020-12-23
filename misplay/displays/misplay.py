
import os
import time
import logging

FIFO_Y = 60

class RefreshException( Exception ):
    pass

class Misplay( object ):

    def __init__( self, refresh, w, h, r, mx, my, sources ):

        logger = logging.getLogger( 'misplay.init' )

        # Setup wallpaper timers.
        self.last_update = int( time.time() )
        self.refresh = refresh
        self.w = w
        self.h = h
        self.rotate = r
        self.margin_x = mx
        self.margin_y = my
        self.sources = sources
        self._src_buf = None

        for src in self.sources:
            src.set_misplay( self )
            logger.info( 'starting {}'.format( type( src ) ) )
            src.start()

    def clear( self ):
        pass

    def image( self, path, pos, width, height, erase ):
        pass

    def blank( self, x, y, w, h, draw, fill ):
        pass
    
    def text( self, text, pos, erase ):
        pass

    def flip( self ):
        pass

    def update( self ):
        pass

    def source_text( self, text ):
        self._src_buf = text

    def loop( self ):

        logger = logging.getLogger( 'misplay.loop' )
        logger.setLevel( logging.DEBUG )

        while( True ):
            seconds = int( time.time() )
            elapsed = seconds - self.last_update
            self.last_update = int( time.time() )
            logger.debug( '{} seconds elapsed'.format( elapsed ) )
            self.wp_countup += elapsed


            self.update()

            # Update time display.
            self.text( time.strftime( '%H:%M' ), (self.margin_x, self.margin_y) )
            if self._src_buf:
                self.text( self._src_buf, (self.margin_x, FIFO_Y) )

            # Sleep.
            logger.debug( 'sleeping for {} seconds...'.format( self.refresh ) )
            time.sleep( self.refresh )


