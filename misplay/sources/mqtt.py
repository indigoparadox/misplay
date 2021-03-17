
import logging
import ssl
from paho.mqtt import client as mqtt_client
from misplay.sources.source import MisplaySource # pylint: disable=import-error

class MQTTSource( MisplaySource ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        self.logger = logging.getLogger( 'sources.mqtt' )

        self.topic = kwargs['mqtttopic']
        self.mqtt = mqtt_client.Client(
            kwargs['mqttuid'], True, None, mqtt_client.MQTTv31 )
        self.mqtt.loop_start()
        self.mqtt.enable_logger()
        self.mqtt.message_callback_add( '{}/msg'.format( self.topic ),
            self.mqtt_received )
        self.logger.info( 'enabling TLS...' )
        if 'mqttssl' in kwargs and kwargs['mqttssl']:
            self.mqtt.tls_set(
                kwargs['mqttca'], tls_version=ssl.PROTOCOL_TLSv1_2 )
        self.mqtt.on_connect = self.mqtt_connected
        self.logger.info( 'connecting to MQTT at %s:%d...',
            kwargs['mqtthost'], int( kwargs['mqttport'] ) )
        self.mqtt.connect( kwargs['mqtthost'], int( kwargs['mqttport'] ) )

    def stop( self ):
        self.mqtt.loop_stop()

    def mqtt_connected( self, client, userdata, flags, rc ): # pylint: disable=unused-argument
        logger = logging.getLogger( 'sources.mqtt.connected' )
        logger.info( 'subscribing to %s/#...', self.topic )
        self.mqtt.subscribe( '{}/#'.format( self.topic ) )

    def mqtt_received( self, client, userdata, message ): # pylint: disable=unused-argument
        msg_buf = str( message.payload.decode( 'utf-8' ) )
        logger = logging.getLogger( 'sources.mqtt.received' )
        logger.info( msg_buf )
        self.panel.add_message( msg_buf )
