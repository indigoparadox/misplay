#!/usr/bin/env python3

import epd2in13
import time
import PIL
import traceback
import os
from PIL import ImageFont, ImageDraw
import random
import logging
import configparser
import errno

WP_MAX_W = 100
TIME_X = 120
TIME_Y = 80
FIFO_Y = 60

class Misplay( object ):

    def __init__( self ):
        self.config = configparser.ConfigParser()
        self.config.read( '/etc/misplay.ini' )
        self.epd = epd2in13.EPD()
        self.canvas = PIL.Image.new( \
            '1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255 )
        self.blank( 0, 0, epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH, fill=255 )
        self.last_update = int( time.time() )
        self.wp_countup = \
            self.config.getint( 'display', 'wallpapers-interval' )

        try:
            os.mkfifo( self.config['ipc']['fifo'] )
        #except OSError as e:
        #    # If it exists then we're fine.
        #    if errno.EEXIST != e:
        #        raise
        except FileExistsError as e:
            pass

    def clear( self ):
        self.epd.init( self.epd.lut_full_update )
        self.epd.Clear( 0xFF )

    def image( self, path, pos=(0, 0), width=80, erase=True ):
        self.epd.init( self.epd.lut_partial_update )
  
        bmp = PIL.Image.open( path )
        bmp.thumbnail( (width, epd2in13.EPD_HEIGHT) )
        draw = ImageDraw.Draw( self.canvas )

        if erase:
            draw.rectangle( (pos[0], pos[1], \
                pos[0] + bmp.size[0], pos[1] + bmp.size[1]), fill = 255 )
        self.canvas.paste( bmp, (10,10) )

        self.update()

    def blank( self, x, y, w, h, draw=None, fill=255 ):
        self.epd.init( self.epd.lut_partial_update )

        do_update = False

        # Get a pen if none provided.
        if None == draw:
            draw = ImageDraw.Draw( self.canvas )
            do_update = True

        # Blank out the area.
        draw.rectangle( (x, y, x+w, y+h), fill=fill )
        if do_update:
            self.update()
    
    def text( self, text, pos, erase=True ):
        self.epd.init( self.epd.lut_partial_update )

        font24 = ImageFont.truetype( self.config['display']['font'],
          self.config.getint( 'display', 'font-size' ) )
        draw = ImageDraw.Draw( self.canvas )

        # Erase text area to prevent overlap, then draw text.
        ts = font24.getsize( text )
        if erase:
            self.blank( pos[0], pos[1], ts[0], ts[1], draw )
        draw.text( pos, text, font = font24, fill = 0 )

        self.update()

    def update( self ):
        self.epd.display( self.epd.getbuffer( self.canvas.rotate( 180 ) ) )
         
        #self.epd.sleep()

    def loop( self ):

        logger = logging.getLogger( 'misplay.loop' )
        logger.setLevel( logging.DEBUG )

        fifo_path = self.config['ipc']['fifo']
        logger.debug( 'opening IPC FIFO {}...'.format( fifo_path ) )
         
        while( True ):
            seconds = int( time.time() )
            elapsed = seconds - self.last_update
            self.last_update = int( time.time() )
            logger.debug( '{} seconds elapsed'.format( elapsed ) )
            self.wp_countup += elapsed

            # Update config.
            self.config.read( '/etc/misplay.ini' )
            wp_int = self.config.getint( 'display', 'wallpapers-interval' )
            wp_path = self.config['display']['wallpapers-path']

            logger.debug( '{} until wp change'.format( wp_int - self.wp_countup ) )

            # Use cached fifo path to avoid issues from changing path later.
            fifo_buf = None
            fifo_buf_sz = 128
            fifo_io = os.open( fifo_path, os.O_RDONLY | os.O_NONBLOCK )
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
                status.text( fifo_buf, (TIME_X, FIFO_Y) )

            # Change the image on wallpapers-interval seconds.
            if wp_int <= self.wp_countup:
                self.wp_countup = 0
                entry_path = '.'
                while '.' == entry_path[0]:
                    entry_iter = random.choice( os.listdir( wp_path ) )
                    entry_path = os.path.join( wp_path, entry_iter )
                logger.debug( 'selecting image: {}'.format( entry_path ) )

                # Blackout the image area to prevent artifacts.
                draw = ImageDraw.Draw( self.canvas )
                status.blank( 0, 0, epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH,
                    draw, 0 )
                self.update()
                status.blank( 0, 0, epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH,
                    draw, 127 )
                self.update()

                # Draw the new wallpaper.
                status.image( entry_path )

            # Update time display.
            status.text( time.strftime( '%H:%M' ), (TIME_X, TIME_Y) )

            # Sleep.
            logger.debug( 'sleeping for {} seconds...'.format(
                self.config.getint( 'display', 'refresh' ) ) )
            time.sleep( self.config.getint( 'display', 'refresh' ) )

if '__main__' == __name__:

    logging.basicConfig( level=logging.INFO )

    status = Misplay()
    status.clear()
    status.loop()

