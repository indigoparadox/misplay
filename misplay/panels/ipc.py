
import logging
from .panel import TextPanel
from datetime import datetime

class IPCPanel( TextPanel ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        self.ttl = kwargs['ttl'] if 'ttl' in kwargs else 0
        self.messages = []
        self.sources = []
        sources = kwargs['sources'].split( ',' )
        if 'fifo' in sources:
            from misplay.sources.fifo import FIFOSource
            self.sources.append( FIFOSource( **kwargs ) )
        if 'mqtt' in sources:
            from misplay.sources.mqtt import MQTTSource
            self.sources.append( MQTTSource( **kwargs ) )

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


