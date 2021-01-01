
import logging
import threading
from .panel import TextPanel
from datetime import datetime

class IPCPanel( TextPanel ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        self.ttl = int( kwargs['ttl'] ) if 'ttl' in kwargs else 0
        self.messages = []
        self.msg_lock = threading.Lock()
        self.last_msg = None
        self.sources = []
        self.countup = 0
        sources = kwargs['sources'].split( ',' )
        kwargs['panel'] = self
        if 'fifo' in sources:
            from misplay.sources.fifo import FIFOSource
            self.sources.append( FIFOSource( **kwargs ) )
        if 'mqtt' in sources:
            from misplay.sources.mqtt import MQTTSource
            self.sources.append( MQTTSource( **kwargs ) )

    def add_message( self, msg ):
        logger = logging.getLogger( 'ipc.message.add' )
        logger.debug( 'msg received: {}'.format( msg ) )
        msg_pkt = {'msg': msg, 'timestamp': datetime.now()}
        with self.msg_lock:
            self.messages.append( msg_pkt )

    def stop( self ):
        for src in self.sources:
            src.stop()

    def update( self, elapsed ):
        logger = logging.getLogger( 'ipc.update' )

        self.countup += elapsed
        logger.debug( 'ipc ttl counter: {}'.format( self.countup ) )

        with self.msg_lock:
            # Show message if any.
            if 0 < len( self.messages ) and \
            (self.last_msg != self.messages[0]['msg'] or not self.last_msg):
                self.last_msg = self.messages[0]['msg']
                logger.debug(
                    'displaying message: {}'.format( self.messages[0]['msg'] ) )
                self.text( self.messages[0]['msg'], 0, blank=True )
                logger.debug(
                    'reset countup from {} to 0'.format( self.countup ) )
                self.countup = 0

            # Remove expired messages.
            if 0 < len( self.messages ) and \
            self.ttl <= self.countup:
                logger.debug(
                    'message expired at {}, removing. {} left.'.format(
                        self.countup, len( self.messages ) - 1 ) )
                self.messages.pop( 0 )
                self.text( ' ', blank=True )

            self.countup += elapsed

