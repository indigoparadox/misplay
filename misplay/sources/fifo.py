
import logging
import os
import time
import errno
from .source import MisplaySource

class FIFOSource( MisplaySource ):
    def __init__( self, fifo_path ):
        super().__init__()
        logger = logging.getLogger( 'sources.fifo' )
        self._fifo_path = fifo_path
        self.create_fifo()

    def create_fifo( self ):
        logger = logging.getLogger( 'sources.fifo.create' )
        try:
            logger.info( 'creating FIFO at {}...'.format( self._fifo_path ) )
            os.mkfifo( self._fifo_path )
        except FileExistsError as e:
            logger.info( 'FIFO already exists.' )

    def poll( self ):
        logger = logging.getLogger( 'sources.fifo.read' )

        #self.fifo_path = self.config['ipc']['fifo']
        logger.debug( 'opening IPC FIFO {}...'.format( self._fifo_path ) )
         
        # Use cached fifo path to avoid issues from changing path later.
        fifo_buf = None
        fifo_buf_sz = 128
        fifo_io = os.open( self._fifo_path, os.O_RDONLY | os.O_NONBLOCK )
        try:
            fifo_buf = os.read( fifo_io, fifo_buf_sz )
        except OSError as e:
            if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                fifo_buf = None
            else:
                raise
        os.close( fifo_io )

        if fifo_buf:
            return fifo_buf.decode( 'utf-8' )
        return None

