
from .misplay import Misplay
from PIL import Image, ImageFont, ImageDraw
import misplay.displays.drivers.epd2in13 as epd2in13
import logging
import random
import os

class EPD2in13( Misplay ):

    def __init__( self, refresh, w, h, r, sources, msg_ttl, wp_int, wp_path, font_fam, font_size ):
        super().__init__( refresh, w, h, r, 120, 80, sources, msg_ttl )

        self.wp_countup = wp_int
        self.wp_int = wp_int
        self.wp_path = wp_path
        self.font_fam = font_fam
        self.font_size = font_size
        
        logger = logging.getLogger( 'misplay.displays.epd2in13' )

        # Setup display.
        logger.info( 'setting up display...' )

        self.epd = epd2in13.EPD()
        self.canvas = Image.new( \
            '1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255 )

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

    def text( self, text, pos, erase=True ):
        self.epd.init( self.epd.lut_partial_update )

        font24 = ImageFont.truetype( self.font_fam, self.font_size )
        draw = ImageDraw.Draw( self.canvas )

        # Erase text area to prevent overlap, then draw text.
        ts = font24.getsize( text )
        if erase:
            self.blank( pos[0], pos[1], ts[0], ts[1], draw )
        draw.text( pos, text, font = font24, fill = 0 )

    def flip( self ):

        self.epd.display( self.epd.getbuffer( self.canvas.rotate( self.rotate ) ) )
         
        #self.epd.sleep()

    def update( self, elapsed ):

        logger = logging.getLogger( 'epd2in13.update' )

        # Change the image on wallpapers-interval seconds.
        self.wp_countup += elapsed
        if self.wp_int <= self.wp_countup:
            self.wp_countup = 0
            entry_path = '.'
            while '.' == entry_path[0]:
                entry_iter = random.choice( os.listdir( self.wp_path ) )
                entry_path = os.path.join( self.wp_path, entry_iter )
            logger.debug( 'selecting image: {}'.format( entry_path ) )

            # Blackout the image area to prevent artifacts.
            draw = ImageDraw.Draw( self.canvas )
            self.blank( 0, 0, self.w, self.h, draw, 0 )
            self.flip()
            self.blank( 0, 0, self.w, self.h, draw, 255 )
            self.flip()

            # Draw the new wallpaper.
            self.image( entry_path, height=self.h )
        else:
            logger.debug(
                '{} until wp change'.format( self.wp_int - self.wp_countup ) )

