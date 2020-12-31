
import logging
import time
from .panel import TextPanel

class TimePanel( TextPanel ):

    def __init__( self, panel, font=None, size=0, date=False, dtsize=0 ):
        logger = logging.getLogger( 'panel.time' )
        super().__init__( 0, 0, font, size )
        self.date_size = int( dtsize )
        if 'true' == date:
            logger.debug( 'date display enabled' )
            self.show_date = True
            self.lines = 2
        else:
            logger.debug( 'date display disabled' )
            self.show_date = False

    def line_height( self, line_idx ):
        logger = logging.getLogger( 'panel.time.height.line' )
        font_sz = self.font_size
        # The date line is shorter.
        if 1 == line_idx:
            font_sz = self.date_size
        text_sz = self.display.text( None, self.font_family, font_sz, None )
        logger.debug( '{} line {} height: {}'.format( type( self ), line_idx,
            text_sz[1] ) )
        return text_sz[1]

    def update( self, elapsed ):
        # Update time display.
        self.text( time.strftime( '%H:%M' ), 0 )
        if self.show_date:
            self.text( time.strftime( '%m/%d/%Y %a' ), 1, font_sz=self.date_size )

