
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
    def __init__( self, width=0, height=0, font=None, size=0, lines=1, text=None, panel=None ):
        super().__init__( width, height )
        self.lines = int( lines )
        self.font_family = font
        self.font_size = int( size )
        self._display = None
        self._line_height = 0
        self._static_text = text

    @property
    def display( self ):
        return self._display
    
    @display.setter
    def display( self, value ):
        logger = logging.getLogger( 'panel.text' )
        if value:
            if not self.font_family:
                self.font_family = value.font_family
            if not self.font_size:
                self.font_size = value.font_size
            text_sz = value.text( None, self.font_family, self.font_size, None )
            self._line_height = text_sz[1]
            self.h = (self._line_height + value.margins) * (self.lines)
            logger.debug( 'setting height to: {} ({})'.format(
                self.h, self._line_height ) )
        self._display = value

    def text( self, text, line=0 ):
        margin = line * self.display.margins
        line_y = self.y + (line * self._line_height) + margin
        self.display.blank( self.x, line_y, self.w, self.h, fill=255 )
        self.display.text(
            text, self.font_family, self.font_size, (self.x, line_y) )

    def update( self, elapsed ):
        if self._static_text:
            self.text( self._static_text, 0 )

class RowsPanel( MisplayPanel ):
    def __init__( self, width, height, panel, rows ):
        super().__init__( width, height )
        self.rows = []

