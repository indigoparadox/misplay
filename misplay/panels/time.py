
import time
from .panel import TextPanel

class TimePanel( TextPanel ):

    def __init__( self, panel, font, size ):
        super().__init__( 0, 0, font, size, 1 )

    def update( self, elapsed ):
        # Update time display.
        self.text( time.strftime( '%H:%M' ), 0 )

