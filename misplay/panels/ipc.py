
import logging
from misplay.sources.fifo import FIFOSource
from .panel import TextPanel
from datetime import datetime

class IPCPanel( TextPanel ):

    def __init__( self, panel, lines, sources, ttl, font=None, size=0, fifo=None ):
        super().__init__( 0, 0, font, size, lines )

        self.ttl = ttl
        self.messages = []
        self.sources = []
        for src in sources:
            if 'fifo' in sources and fifo:
                self.sources.append( FIFOSource( fifo ) )

    def update( self, elapsed ):
        logger = logging.getLogger( 'ipc.update' )

        # Update time display.
        for src in self.sources:
            logger.debug( 'polling source {}'.format( type( src ) ) )
            buf = src.poll()
            if buf:
                logger.debug( 'msg found: {}'.format( buf ) )
                msg = {'msg': buf, 'timestamp': datetime.now()}
                self.messages.append( msg )
            else:
                logger.debug( 'no messages' )

        # Show message if any.
        # TODO: Use proper number of lines.
        if 0 < len( self.messages ):
            self.text( self.messages[0]['msg'], 0 )


