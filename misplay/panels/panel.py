
import logging

class MisplayPanel( object ):
    def __init__( self, w, h ):
        self.w = int( w )
        self.h = int( h )

        # These will be set by the display.
        self.display = None
        self.x = 0
        self.y = 0

class TextPanel( MisplayPanel ):
    def __init__( self, width, height, font, size, lines ):
        super().__init__( width, height )
        self.lines = int( lines )
        self.font_family = font
        self.font_size = int( size )
        self._display = None

    @property
    def display( self ):
        return self._display
    
    @display.setter
    def display( self, value ):
        logger = logging.getLogger( 'panel.text' )
        if value:
            text_sz = value.text( None, self.font_family, self.font_size, None )
            self.h = text_sz[1]
            logger.debug( 'setting height to: {}'.format( self.h ) )
        self._display = value

    def text( self, text, line ):
        # TODO: Add correct line height.
        self.display.text( text,
            self.font_family, self.font_size,
            (self.x, self.y) )

class RowsPanel( MisplayPanel ):
    def __init__( self, width, height, panel, rows ):
        super().__init__( width, height )
        self.rows = []

