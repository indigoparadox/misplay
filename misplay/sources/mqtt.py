
import logging
import ssl
from paho.mqtt import client as mqtt_client

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

