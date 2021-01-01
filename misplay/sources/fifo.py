
import logging
import os
import time
import errno
import threading
from .source import MisplaySource

class FIFOThread( threading.Thread ):
    def __init__( self, source ):
        super().__init__()
        self.source = source
        self.running = True

    def run( self ):
        while self.running:
            fifo_buf = self.source.read_fifo()
            if fifo_buf:
                self.source.panel.add_message( fifo_buf )
            time.sleep( self.source.fifo_poll )

class FIFOSource( MisplaySource ):
    def __init__( self, **kwargs ):
        super().__init__( **kwargs )
        logger = logging.getLogger( 'sources.fifo' )
        self._fifo_path = kwargs['fifo']
        self._fifo_lock = threading.Lock()
        self.create_fifo()
        self._fifo_thread = FIFOThread( self )
        self._fifo_thread.start()
        self.fifo_poll = int( kwargs['fifopoll'] )

    def create_fifo( self ):
        logger = logging.getLogger( 'sources.fifo.create' )
        try:
            logger.info( 'creating FIFO at {}...'.format( self._fifo_path ) )
            os.mkfifo( self._fifo_path )
        except FileExistsError as e:
            logger.info( 'FIFO already exists.' )

    def stop( self ):
        self._fifo_thread.running = False

    def read_fifo( self ):
        logger = logging.getLogger( 'sources.fifo.read' )

        fifo_buf = None
        fifo_buf_sz = 128
        with self._fifo_lock:
            #self.fifo_path = self.config['ipc']['fifo']
            #logger.debug( 'opening IPC FIFO {}...'.format( self._fifo_path ) )
             
            # Use cached fifo path to avoid issues from changing path later.
            fifo_io = os.open( 
                self._fifo_path, os.O_RDONLY | os.O_NONBLOCK )
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

