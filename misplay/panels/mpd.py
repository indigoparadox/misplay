
import logging
from .panel import TextPanel
from mpd import MPDClient

class MPDPanel( TextPanel ):

    def __init__( self, panel, mpd, font=None, size =0 ):
        super().__init__( 0, 0, font, size, 2 )

        self.mpc = MPDClient()
        self.mpc.idletimeout = None
        self.mpd_addr = mpd
        self.last_song = None

    def _mpd_command( self, command, *args ):
        self.mpc.connect( self.mpd_addr )
        res = command( *args )
        self.mpc.disconnect()
        return res

    def update( self, elapsed ):
        logger = logging.getLogger( 'mpd.update' )

        song_changed = False
        mpsong = self._mpd_command( self.mpc.currentsong )
        if self.last_song != mpsong['title']:
            song_changed = True
            self.last_song = mpsong['title']

        self.text( mpsong['title'], 0, blank=song_changed )
        
        mpstatus = self._mpd_command( self.mpc.status )
        mpstate = 'Stopped'
        if 'play' == mpstatus['state']:
            mpstate = 'Playing'
        elif 'pause' == mpstatus['state']:
            mpstate = 'Paused'

        self.text( '{}/{} {}'.format(
            mpstatus['time'], mpstatus['duration'], mpstate ), 1, blank=song_changed )

