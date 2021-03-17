
import logging

import buttonshim # pylint: disable=import-error
from mpd import MPDClient

# TODO: Make this configurable.
SOCK_ADDR = '/var/run/mpd/socket'

class MPDButtonHandler( object ):

    def __init__( self ):
        self.mpc = MPDClient()
        self.mpc.idletimeout = False

    @buttonshim.on_press( buttonshim.BUTTON_C )
    def voldown_handler( self, button, pressed ): # pylint: disable=unused-argument
        logger = logging.getLogger( 'button.voldown' )
        logger.debug( 'button pressed' )
        mpstatus = self.mpd_command( self.mpc.status ) # pylint: disable=no-member
        self.mpd_command( self.mpc.setvol, int( mpstatus['volume'] ) - 5 ) # pylint: disable=no-member
        logger.info( 'volume is now %d', mpstatus['volume'] )

    @buttonshim.on_press( buttonshim.BUTTON_D )
    def volup_handler( self, button, pressed ): # pylint: disable=unused-argument
        logger = logging.getLogger( 'button.volup' )
        logger.debug( 'button pressed' )
        mpstatus = self.mpd_command( self.mpc.status ) # pylint: disable=no-member
        self.mpd_command( self.mpc.setvol, int( mpstatus['volume'] ) + 5  ) # pylint: disable=no-member
        logger.info( 'volume is now %d', mpstatus['volume'] )

    @buttonshim.on_press( buttonshim.BUTTON_E )
    def play_handler( self, button, pressed ): # pylint: disable=unused-argument
        logger = logging.getLogger( 'button.playpause' )
        logger.debug( 'button pressed' )
        self.mpd_command( self.mpc.pause ) # pylint: disable=no-member

    def mpd_command( self, command, *args ):
        self.mpc.connect( SOCK_ADDR )
        res = command( *args )
        self.mpc.disconnect()
        return res
