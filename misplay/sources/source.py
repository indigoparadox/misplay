
class MisplaySource( object ):
    def __init__( self, **kwargs ):
        self.panel = kwargs['panel']

    def poll( self ):
        return None
