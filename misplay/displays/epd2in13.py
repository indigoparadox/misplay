
import logging

from PIL import Image, ImageFont, ImageDraw

import misplay.displays.drivers.epd2in13 as epd2in13 # pylint: disable=import-error
from misplay.displays import Misplay # pylint: disable=import-error

class EPD2in13( Misplay ):

    def __init__( self, refresh, width, height, rotate, panels, margins=0, font=None, size=0 ):
        logger = logging.getLogger( 'misplay.displays.epd2in13' )

        # Setup display.
        logger.info( 'setting up display...' )

        self.epd = epd2in13.EPD()
        self.canvas = Image.new( \
            '1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255 )
        self.updated = False

        super().__init__( refresh, width, height, rotate, margins, panels, font, size )

        self.epd.init( self.epd.lut_full_update )

    def image( self, path, pos=(0, 0), width=80, height=100 ):
        bmp = Image.open( path )
        bmp.thumbnail( (width, height) )
        self.canvas.paste( bmp, pos )
        self.updated = True

    def blank( self, x, y, w, h, fill=255 ):

        # Get a pen if none provided.
        draw = ImageDraw.Draw( self.canvas )

        # Blank out the area.
        draw.rectangle( (x, y, x+w, y+h), fill=fill )
        self.updated = True

    def text( self, text, font_family, font_size, position ):

        font = ImageFont.truetype( font_family, font_size )
        draw = ImageDraw.Draw( self.canvas )

        # Erase text area to prevent overlap, then draw text.
        ts = font.getsize( 'X' )
        if text:
            ts = font.getsize( text )
            self.blank( position[0], position[1], ts[0], ts[1] )
            draw.text( position, text, font = font, fill = 0 )
            self.updated = True

        return ts

    def flip( self ):

        if self.updated:
            self.epd.display( self.epd.getbuffer( self.canvas.rotate( self.rotate ) ) )
            self.updated = False

        #self.epd.sleep()
