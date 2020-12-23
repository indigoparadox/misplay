#!/usr/bin/env python3

from misplay.displays.epd2in13 import MisplayEPD2in13
from misplay.displays.misplay import RefreshException
import logging
import os
import atexit
import configparser

@atexit.register
def shutdown_display():
    global status

    status.clear()

def create_misplay( ini_path ):
    logger = logging.getLogger( 'create' )

    # Load config.
    logger.info( 'using config at {}'.format( ini_path ) )

    config = configparser.ConfigParser()
    config.read( ini_path )
    wp_interval = config.getint( 'display', 'wallpapers-interval' )
    fifo_path = config['ipc']['fifo']
    dsp_refresh = config.getint( 'display', 'refresh' )
    wp_int = config.getint( 'display', 'wallpapers-interval' )
    wp_path = config['display']['wallpapers-path']
    display_type = 'epd2in13'
    w = config.getint( display_type, 'width' )
    h = config.getint( display_type, 'height' )
    r = config.getint( display_type, 'rotate' )
    font_fam = config[display_type]['font']
    font_size = config.getint( display_type, 'font-size' )

    return MisplayEPD2in13(
        fifo_path, dsp_refresh, w, h, r, wp_int, wp_path, font_fam, font_size )

def main():
    global status

    do_reload = True

    logging.basicConfig( level=logging.INFO )
    logger = logging.getLogger( 'main' )

    ini_path = os.path.join( os.path.dirname( 
        os.path.realpath( __file__ ) ), 'misplay.ini' )

    while do_reload:
        do_reload = False
        try:
            status = create_misplay( ini_path )
            status.loop()

        except RefreshException:
            do_reload = True

if '__main__' == __name__:
    main()

