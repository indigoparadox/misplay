
from misplay.displays import Misplay
from PIL import Image, ImageFont, ImageDraw
import logging
import random
import os

class DummyDisplay( Misplay ):

    def __init__( self, refresh, width, height, rotate, panels, margins=0, font=None, size=0 ):
        logger = logging.getLogger( 'misplay.displays.dummy' )

        # Setup display.
        logger.info( 'setting up display...' )

        width = int( width )
        height = int( height )

        self.canvas = Image.new( '1', (width, height), 255 )

        super().__init__( refresh, width, height, rotate, margins, panels, font, size )

    def text( self, text, font_family, font_size, position, erase=True ):

        font = ImageFont.truetype( font_family, font_size )
        draw = ImageDraw.Draw( self.canvas )

        # Erase text area to prevent overlap, then draw text.
        ts = font.getsize( 'X' )
        if text:
            ts = font.getsize( text )

        return ts

