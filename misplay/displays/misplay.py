
import os
import time
import logging
from datetime import datetime

FIFO_Y = 60

class RefreshException( Exception ):
    pass

class Misplay( object ):

    def __init__( self, refresh, w, h, r, mx, my, sources, msg_ttl ):

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
        self.messages = []
        self.msg_ttl = msg_ttl

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

    def update( self, elapsed ):
        pass

    def loop( self ):

        logger = logging.getLogger( 'misplay.loop' )

        while( True ):
            seconds = int( time.time() )
            elapsed = seconds - self.last_update
            self.last_update = int( time.time() )
            logger.debug( '{} seconds elapsed'.format( elapsed ) )

            # Call implementation-specific update.
            self.update( elapsed )

            for src in self.sources:
                logger.debug( 'polling source {}'.format( type( src ) ) )
                buf = src.poll()
                if buf:
                    logger.debug( 'msg found: {}'.format( buf ) )
                    msg = {'msg': buf, 'timestamp': datetime.now()}
                    self.messages.append( msg )
                else:
                    logger.debug( 'no messages' )

            # Show message if any.
            if 0 < len( self.messages ):
                self.text( self.messages[0]['msg'], (self.margin_x, FIFO_Y) )

            # Update time display.
            self.text( time.strftime( '%H:%M' ), (self.margin_x, self.margin_y) )

            self.flip()

            # Sleep.
            logger.debug( 'sleeping for {} seconds...'.format( self.refresh ) )
            time.sleep( self.refresh )


