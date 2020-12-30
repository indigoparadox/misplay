
from .misplay import Misplay
from PIL import Image, ImageFont, ImageDraw
import misplay.displays.drivers.epd2in13 as epd2in13
import logging
import random
import os

class EPD2in13( Misplay ):

    def __init__( self, refresh, width, height, rotate, panels, margins=0, font=None, size=0 ):
        logger = logging.getLogger( 'misplay.displays.epd2in13' )

        # Setup display.
        logger.info( 'setting up display...' )

        self.epd = epd2in13.EPD()
        self.canvas = Image.new( \
            '1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255 )

        super().__init__( refresh, width, height, rotate, margins, panels, font, size )

        self.clear()

    def clear( self ):
        self.epd.init( self.epd.lut_full_update )
        self.epd.Clear( 0xFF )

    def image( self, path, pos=(0, 0), width=80, height=100, erase=True ):
        self.epd.init( self.epd.lut_partial_update )
  
        bmp = Image.open( path )
        bmp.thumbnail( (width, height) )
        draw = ImageDraw.Draw( self.canvas )

        if erase:
            draw.rectangle( (pos[0], pos[1], \
                pos[0] + bmp.size[0], pos[1] + bmp.size[1]), fill = 255 )
        self.canvas.paste( bmp, (10,10) )

    def blank( self, x, y, w, h, draw=None, fill=255 ):
        self.epd.init( self.epd.lut_partial_update )

        do_flip = False

        # Get a pen if none provided.
        if None == draw:
            draw = ImageDraw.Draw( self.canvas )
            do_flip = True

        # Blank out the area.
        draw.rectangle( (x, y, x+w, y+h), fill=fill )
        if do_flip:
            self.flip()

    def text( self, text, font_family, font_size, position, erase=True ):
        self.epd.init( self.epd.lut_partial_update )

        font = ImageFont.truetype( font_family, font_size )
        draw = ImageDraw.Draw( self.canvas )

        # Erase text area to prevent overlap, then draw text.
        ts = font.getsize( 'X' )
        if text:
            ts = font.getsize( text )
            if erase:
                self.blank( position[0], position[1], ts[0], ts[1], draw )
            draw.text( position, text, font = font, fill = 0 )

        return ts

    def flip( self ):

        self.epd.display( self.epd.getbuffer( self.canvas.rotate( self.rotate ) ) )
         
        #self.epd.sleep()

