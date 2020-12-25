
import errno
import logging
import ssl
import os
import time
from paho.mqtt import client as mqtt_client

class MisplaySource( object ):
    def __init__( self ):
        pass

    def poll( self ):
        return None

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

def mqtt_connected( userdata, flags, rc ):
    logger = logging.getLogger( 'sources.mqtt.connected' )
    logger.info( 'subscribing to {}/#...'.format( 'epaperpi' ) )
    self.mqtt.subscribe( '{}/#'.format( 'epaperpi' ) )

class MQTTSource( MisplaySource ):

    def __init__( self, uid, host, port, topic, use_ssl, ca ):
        super().__init__()

        logger = logging.getLogger( 'sources.mqtt' )

        self.topic = topic
        self.mqtt = mqtt_client.Client( uid, True, None, mqtt_client.MQTTv31 )
        self.mqtt.message_callback_add( '{}/msg'.format( self.topic ),
            self.mqtt_received )
        logger.info( 'enabling TLS...' )
        if use_ssl:
            self.mqtt.tls_set( ca, tls_version=ssl.PROTOCOL_TLSv1_2 )
        self.mqtt.on_connect = mqtt_connected
        logger.info( 'connecting to MQTT at {}:{}...'.format( host, port ) )
        self.mqtt.connect( host, port )
        self.mqtt.loop_forever()


    def mqtt_received( self, client, userdata, message ):
        logger = logging.getLogger( 'sources.mqtt.received' )
        logger.info( str( message.payload.decode( 'utf-8' ) ) )

