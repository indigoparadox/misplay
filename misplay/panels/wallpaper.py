
import random
import os
import logging

from PIL import ImageDraw

from .panel import MisplayPanel

class WallpaperPanel( MisplayPanel ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.path = kwargs['path']
        self.wp_countup = int( kwargs['interval'] )
        self.wp_int = int( kwargs['interval'] )
        self.logger = logging.getLogger( 'wallpaper' )

    def update( self, elapsed ):

        # Change the image on wallpapers-interval seconds.
        self.wp_countup += elapsed
        if self.wp_int <= self.wp_countup:
            self.wp_countup = 0
            entry_path = '.'
            while '.' == entry_path[0]:
                entry_iter = random.choice( os.listdir( self.path ) )
                entry_path = os.path.join( self.path, entry_iter )
            self.logger.debug( 'selecting image: %s', entry_path )

            # Blackout the image area to prevent artifacts.
            draw = ImageDraw.Draw( self.display.canvas )
            self.display.blank( 0, 0, self.w, self.h, draw, 0 )
            self.display.flip()
            self.display.blank( 0, 0, self.w, self.h, draw, 255 )
            self.display.flip()

            # Draw the new wallpaper.
            self.display.image( entry_path, height=self.h )
        else:
            self.logger.debug(
                '%d until wp change', self.wp_int - self.wp_countup )
