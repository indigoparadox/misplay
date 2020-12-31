
import random
import os
import logging
# XXX
from PIL import Image, ImageFont, ImageDraw
from .panel import MisplayPanel

class WallpaperPanel( MisplayPanel ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.path = kwargs['path']
        self.wp_countup = int( kwargs['interval'] )
        self.wp_int = int( kwargs['interval'] )

    def update( self, elapsed ):
        logger = logging.getLogger( 'wallpaper.update' )

        # Change the image on wallpapers-interval seconds.
        self.wp_countup += elapsed
        if self.wp_int <= self.wp_countup:
            self.wp_countup = 0
            entry_path = '.'
            while '.' == entry_path[0]:
                entry_iter = random.choice( os.listdir( self.path ) )
                entry_path = os.path.join( self.path, entry_iter )
            logger.debug( 'selecting image: {}'.format( entry_path ) )

            # Blackout the image area to prevent artifacts.
            # TODO: Use display blanking function?
            draw = ImageDraw.Draw( self.display.canvas )
            # TODO: Get X/Y for drawing this panel from display.
            self.display.blank( 0, 0, self.w, self.h, draw, 0 )
            self.display.flip()
            self.display.blank( 0, 0, self.w, self.h, draw, 255 )
            self.display.flip()

            # Draw the new wallpaper.
            self.display.image( entry_path, height=self.h )
        else:
            logger.debug(
                '{} until wp change'.format( self.wp_int - self.wp_countup ) )

