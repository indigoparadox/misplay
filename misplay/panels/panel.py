
class MisplayPanel( object ):
    def __init__( self, w, h ):
        self.w = int( w )
        self.h = int( h )

        # These will be set by the display.
        self.display = None
        self.x = 0
        self.y = 0

class RowsPanel( MisplayPanel ):
    def __init__( self, width, height, panel, rows ):
        super().__init__( width, height )
        self.rows = []

