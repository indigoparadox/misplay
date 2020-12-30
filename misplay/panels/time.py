
import time
from .panel import MisplayPanel

class TimePanel( MisplayPanel ):

    def __init__( self, panel, width=0, height=0, font=None, size=0 ):
        super().__init__( width, height )
        self.font_family = font
        self.font_size = int( size )

    def update( self, elapsed ):
        # Update time display.
        self.display.text( time.strftime( '%H:%M' ),
            self.font_family, self.font_size,
            (self.x, self.y) )

