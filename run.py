#!/usr/bin/env python3

from misplay.misplay import Misplay
import logging
import os
import atexit

status = None

@atexit.register
def shutdown_display():
    status.clear()

if '__main__' == __name__:

    logging.basicConfig( level=logging.INFO )

    ini_path = os.path.join( os.path.dirname( 
        os.path.realpath( __file__ ) ), 'misplay.ini' )

    status = Misplay( ini_path )
    status.loop()

