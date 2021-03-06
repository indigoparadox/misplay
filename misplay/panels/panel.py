
import logging
import traceback

class MisplayPanel( object ):
    def __init__( self, **kwargs ):
        self.w = int( kwargs['w'] ) if 'w' in kwargs else \
            int( kwargs['width'] ) if 'width' in kwargs else 0
        self.h = int( kwargs['h'] ) if 'h' in kwargs else \
            int( kwargs['height'] ) if 'height' in kwargs else 0
        self.logger = logging.getLogger( 'panel' )
        self.logger_loop = logging.getLogger( 'loop.panel' )

        # These will be set by the display.
        self.display = None
        self.x = 0
        self.y = 0

    def stop( self ):
        pass

class TextPanel( MisplayPanel ):
    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.lines = int( kwargs['lines'] ) if 'lines' in kwargs else 1
        self.font_family = kwargs['font'] if 'font' in kwargs else None
        self.font_size = int( kwargs['size'] ) if 'size' in kwargs else 0
        self._display = None
        self._static_text = kwargs['text'] if 'text' in kwargs else None

    @property
    def lines( self ):
        return self._lines

    @lines.setter
    def lines( self, value ):
        self._lines = value
        self._last_text = ['' for i in range( self._lines )]

    @property
    def display( self ):
        return self._display

    @display.setter
    def display( self, value ):

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
            self.logger.debug(
                'setting height to: %d', new_h )
            self.h = new_h

    def line_height( self, line_idx=0 ):
        text_sz = self.display.text(
            None, self.font_family, self.font_size, None )
        self.logger_loop.debug( '%s line %d height: %d',
            type( self ), line_idx, text_sz[1] )
        return text_sz[1]

    def panel_lines_height( self, through=-1 ):
        height_out = 0
        if 0 > through:
            through = self.lines
        for line in range( through ):
            height_out += self.line_height( line )
        margins_out = (self.display.margins * through)
        self.logger_loop.debug( '%s height for %d lines: %d + %d',
            type( self ), through, height_out, margins_out )
        return height_out + margins_out

    def text( self, text, line=0, font_fam=None, font_sz=0 ):
        # Use panel font size by default.
        if not font_fam:
            font_fam = self.font_family
        if 0 >= font_sz:
            font_sz = self.font_size

        # Figure out line offset.
        line_y = self.y + self.panel_lines_height( line )
        line_h = self.line_height( line )
        if text != self._last_text[line]:
            #traceback.print_stack()
            # The call to display.text() will notify the display it's been
            # updated.
            self._last_text[line] = text
            self.display.blank( self.x, line_y, self.w, line_h, fill=255 )
            self.display.text( text, font_fam, font_sz, (self.x, line_y) )

    def update( self, elapsed ): # pylint: disable=unused-argument
        if self._static_text:
            self.text( self._static_text, 0 )

class RowsPanel( MisplayPanel ):
    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        self.rows = []
