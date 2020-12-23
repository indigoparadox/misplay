
import errno
from paho.mqtt import client as mqtt_client
import ssl

class MisplaySource( object ):

    def __init__( self, config_path ):

        self.mqtt = mqtt_client.Client(
            self.config.get( 'ipc.mqtt', 'uid' ) )
        #client.on_connect = mqtt_on_connect
        self.mqtt.connect(
            self.config.get( 'ipc.mqtt', 'host' ),
            self.config.getint( 'ipc.mqtt', 'port' ) )
        self.mqtt.subscribe( '{}/#'.format(
            self.config.get( 'ipc.mqtt', 'topic' ) ) )
        if self.config.getboolean( 'ipc.mqtt', 'ssl' ):
            self.mqtt.tls_set(
                self.config.get( 'ipc.mqtt', 'ca' ),
                tls_version=ssl.PROTOCOL_TLSv1_2 )
        self.mqtt.on_message = self.mqtt_receive
        self.mqtt.loop_start()

    def mqtt_receive( self, client, userdata, message ):
        logger = logging.getLogger( 'misplay.mqtt.receive' )
        logger.info( str( message.payload.decode( 'utf-8' ) ) )

