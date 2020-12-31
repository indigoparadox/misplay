
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
        self._static_text = text

    @property
    def display( self ):
        return self._display
    
    @display.setter
    def display( self, value ):
        logger = logging.getLogger( 'panel.text' )

        # Grab the display's font info if we don't have any.
        # TODO: Make pseudo-properties to do this on the fly.
        if value:
            if not self.font_family:
                self.font_family = value.font_family
            if not self.font_size:
                self.font_size = value.font_size

        # Set the display and calc height if needed.
        self._display = value
        if self._display:
            new_h = self.panel_lines_height()
            logger.debug( 'setting height to: {}'.format( new_h ) )
            self.h = new_h

    def line_height( self, line_idx=0 ):
        logger = logging.getLogger( 'panel.text.height.line' )
        text_sz = self.display.text(
            None, self.font_family, self.font_size, None )
        logger.debug( '{} line {} height: {}'.format( type( self ), line_idx,
            text_sz[1] ) )
        return text_sz[1]

    def panel_lines_height( self, through=-1 ):
        logger = logging.getLogger( 'panel.text.height' )
        height_out = 0
        if 0 > through:
            through = self.lines
        #through += 1
        for line in range( through ):
            height_out += self.line_height( line )
        margins_out = (self.display.margins * through)
        logger.debug( '{} height for {} lines: {} + {}'.format(
            type( self ), through, height_out, margins_out ) )
        return height_out + margins_out

    def text( self, text, line=0, blank=False, font_fam=None, font_sz=0 ):
        # Use panel font size by default.
        if not font_fam:
            font_fam = self.font_family
        if 0 >= font_sz:
            font_sz = self.font_size

        # Figure out line offset.
        margin = line * self.display.margins
        line_y = self.y + self.panel_lines_height( line )
        line_h = self.line_height( line )
        if blank:
            self.display.blank( self.x, line_y, self.w, line_h, fill=255 )
        self.display.text( text, font_fam, font_sz, (self.x, line_y) )

    def update( self, elapsed ):
        if self._static_text:
            self.text( self._static_text, 0 )

class RowsPanel( MisplayPanel ):
    def __init__( self, width, height, panel, rows ):
        super().__init__( width, height )
        self.rows = []

