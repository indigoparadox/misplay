
import logging
from .panel import TextPanel
from mpd import MPDClient

class MPDPanel( TextPanel ):

    def __init__( self, panel, font, size, mpd ):
        super().__init__( 0, 0, font, size, 2 )

        self.mpc = MPDClient()
        self.mpc.idletimeout = None
        self.mpc.connect( mpd )

    def update( self, elapsed ):
        logger = logging.getLogger( 'mpd.update' )

        mpsong = self.mpc.currentsong()
        self.text( mpsong['title'], 0 )
        
        mpstatus = self.mpc.status()
        mpstate = 'Stopped'
        if 'play' == mpstatus['state']:
            mpstate = 'Playing'
        elif 'pause' == mpstatus['state']:
            mpstate = 'Paused'

        self.text( '{}/{} {}'.format(
            mpstatus['time'], mpstatus['duration'], mpstate ), 1 )

