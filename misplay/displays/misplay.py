
import os
import time
import logging

FIFO_Y = 60

class Misplay( object ):

    def __init__( self, fifo_path, refresh, w, h, r, mx, my ):

        logger = logging.getLogger( 'misplay.init' )

        # Setup wallpaper timers.
        self.last_update = int( time.time() )
        self.fifo_path = fifo_path
        self.refresh = refresh
        self.w = w
        self.h = h
        self.rotate = r
        self.margin_x = mx
        self.margin_y = my

        try:
            os.mkfifo( self.fifo_path )
        except FileExistsError as e:
            pass

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

    def loop( self ):

        logger = logging.getLogger( 'misplay.loop' )
        logger.setLevel( logging.DEBUG )

        #self.fifo_path = self.config['ipc']['fifo']
        logger.debug( 'opening IPC FIFO {}...'.format( self.fifo_path ) )
         
        while( True ):
            seconds = int( time.time() )
            elapsed = seconds - self.last_update
            self.last_update = int( time.time() )
            logger.debug( '{} seconds elapsed'.format( elapsed ) )
            self.wp_countup += elapsed

            # TODO: Update config w/ exception.
            #self.config.read( self.config_path )
            #wp_int = self.config.getint( 'display', 'wallpapers-interval' )
            #wp_path = self.config['display']['wallpapers-path']
            #display_w = self.config.getint( self.display_type, 'width' )
            #display_h = self.config.getint( self.display_type, 'height' )

            #logger.debug(
            #    '{} until wp change'.format( wp_int - self.wp_countup ) )

            # Use cached fifo path to avoid issues from changing path later.
            fifo_buf = None
            fifo_buf_sz = 128
            fifo_io = os.open( self.fifo_path, os.O_RDONLY | os.O_NONBLOCK )
            try:
                fifo_buf = os.read( fifo_io, fifo_buf_sz )
            except OSError as e:
                if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                    fifo_buf = None
                else:
                    raise
            os.close( fifo_io )

            if fifo_buf:
                fifo_buf = fifo_buf.decode( 'utf-8' )
                self.text( fifo_buf, (self.margin_x, FIFO_Y) )

            self.update()

            # Update time display.
            self.text( time.strftime( '%H:%M' ), (self.margin_x, self.margin_y) )

            # Sleep.
            logger.debug( 'sleeping for {} seconds...'.format( self.refresh ) )
            time.sleep( self.refresh )


