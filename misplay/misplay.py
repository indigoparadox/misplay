#!/usr/bin/env python3

from . import epd2in13
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

    def __init__( self, config_path ):

        logger = logging.getLogger( 'misplay.init' )

        # Load config.
        logger.info( 'using config at {}'.format( config_path ) )
        self.config = configparser.ConfigParser()
        self.config.read( config_path )
        self.config_path = config_path
        self.display_type = self.config['display']['type']

        # Setup display.
        logger.info( 'setting up display {}'.format( self.display_type ) )
        if 'epd2in13' == self.display_type:
            self.epd = epd2in13.EPD()
            self.canvas = PIL.Image.new( \
                '1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255 )

        # Setup wallpaper timers.
        self.last_update = int( time.time() )
        self.wp_countup = \
            self.config.getint( 'display', 'wallpapers-interval' )

        try:
            os.mkfifo( self.config['ipc']['fifo'] )
        except FileExistsError as e:
            pass

        self.clear()

    def clear( self ):
        self.epd.init( self.epd.lut_full_update )
        self.epd.Clear( 0xFF )

    def image( self, path, pos=(0, 0), width=80, height=100, erase=True ):
        self.epd.init( self.epd.lut_partial_update )
  
        bmp = PIL.Image.open( path )
        bmp.thumbnail( (width, height) )
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

        font24 = ImageFont.truetype( self.config[self.display_type]['font'],
          self.config.getint( self.display_type, 'font-size' ) )
        draw = ImageDraw.Draw( self.canvas )

        # Erase text area to prevent overlap, then draw text.
        ts = font24.getsize( text )
        if erase:
            self.blank( pos[0], pos[1], ts[0], ts[1], draw )
        draw.text( pos, text, font = font24, fill = 0 )

        self.update()

    def update( self ):

        rotate = self.config.getint( self.display_type, 'rotate' )
        self.epd.display( self.epd.getbuffer( self.canvas.rotate( rotate ) ) )
         
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
            self.config.read( self.config_path )
            wp_int = self.config.getint( 'display', 'wallpapers-interval' )
            wp_path = self.config['display']['wallpapers-path']
            display_w = self.config.getint( self.display_type, 'width' )
            display_h = self.config.getint( self.display_type, 'height' )

            logger.debug(
                '{} until wp change'.format( wp_int - self.wp_countup ) )

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
                self.text( fifo_buf, (TIME_X, FIFO_Y) )

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
                self.blank( 0, 0, display_w, display_h, draw, 0 )
                self.update()
                self.blank( 0, 0, display_w, display_h, draw, 255 )
                self.update()

                # Draw the new wallpaper.
                self.image( entry_path, height=display_h )

            # Update time display.
            self.text( time.strftime( '%H:%M' ), (TIME_X, TIME_Y) )

            # Sleep.
            logger.debug( 'sleeping for {} seconds...'.format(
                self.config.getint( 'display', 'refresh' ) ) )
            time.sleep( self.config.getint( 'display', 'refresh' ) )

