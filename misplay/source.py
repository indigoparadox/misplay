
import errno
import logging
import ssl
import os
import time
from threading import Thread
from paho.mqtt import client as mqtt_client

class MisplaySource( Thread ):
    def __init__( self ):
        super().__init__()
        self._misplay = None
        self._running = False

    def set_misplay( self, misplay ):
        self._misplay = misplay

    def is_running( self ):
        return self._running

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

    def read_fifo( self ):
        logger = logging.getLogger( 'sources.fifo.read' )

        #self.fifo_path = self.config['ipc']['fifo']
        logger.debug( 'opening IPC FIFO {}...'.format( self.fifo_path ) )
         
        # Use cached fifo path to avoid issues from changing path later.
        fifo_buf = None
        fifo_buf_sz = 128
        fifo_io = os.open( self.fifo_path, os.O_RDONLY | os.O_NONBLOCK )
        try:
            fifo_buf = os.read( fifo_io, fifo_buf_sz )
        except OSError as e:
            if errno.EAGAIN == e.errno or errno.EWOULDBLOCK == e.errno:
                fifo_buf = None
            else:
                raise
        os.close( fifo_io )

        if fifo_buf:
            fifo_buf = fifo_buf.decode( 'utf-8' )
            self.misplay.source_text( fifo_buf )

    def run( self ):
        while self._running:
            self.read_fifo()
            time.sleep( 5 )

class MQTTSource( MisplaySource ):
    def __init__( self, uid, host, port, topic, ssl, ca ):

        logger = logging.getLogger( 'sources.mqtt' )

        super().__init__()

        self.mqtt = mqtt_client.Client( uid )
        #client.on_connect = mqtt_on_connect
        logger.info( 'connecting to MQTT at {}:{}...'.format( host, port ) )
        self.mqtt.connect( host, port )
        logger.info( 'subscribing to {}/#...'.format( topic ) )
        if ssl:
            self.mqtt.tls_set( ca, tls_version=ssl.PROTOCOL_TLSv1_2 )
        logger.info( 'enabling TLS...' )
        self.mqtt.subscribe( '{}/#'.format( topic ) )
        self.mqtt.on_message = self.mqtt_receive
        self.mqtt.loop_start()
        logger.info( 'ready.' )

    def mqtt_receive( self, client, userdata, message ):
        logger = logging.getLogger( 'sources.mqtt.receive' )
        logger.info( str( message.payload.decode( 'utf-8' ) ) )

