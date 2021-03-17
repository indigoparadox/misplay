
from mpd import MPDClient

from .panel import TextPanel

class MPDPanel( TextPanel ):

    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        self.mpc = MPDClient()
        self.mpc.idletimeout = None
        self.mpd_addr = kwargs['mpd']
        self.last_song = None
        self.lines = 2

    def _mpd_command( self, command, *args ):
        self.mpc.connect( self.mpd_addr )
        res = command( *args )
        self.mpc.disconnect()
        return res

    def update( self, elapsed ):

        # Show song status; don't draw if the song hasn't changed because eink.
        song_changed = False
        mpsong = self._mpd_command( self.mpc.currentsong ) # pylint: disable=no-member
        if self.last_song != mpsong['title']:
            song_changed = True
            self.last_song = mpsong['title']
        self.text( mpsong['title'], 0 )

        # Show player status.
        mpstatus = self._mpd_command( self.mpc.status ) # pylint: disable=no-member
        mpstate = 'Stopped'
        if 'play' == mpstatus['state']:
            mpstate = 'Playing'
        elif 'pause' == mpstatus['state']:
            mpstate = 'Paused'

        self.text( '{} ({})'.format( mpstate, mpstatus['duration'] ), 1 )
        #self.text( '{}/{} {}'.format(
        #    mpstatus['time'], mpstatus['duration'], mpstate ), 1 )
