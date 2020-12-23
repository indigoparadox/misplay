#!/usr/bin/env python3

from misplay.displays.epd2in13 import MisplayEPD2in13
import logging
import os
import atexit
import configparser

if '__main__' == __name__:

    logging.basicConfig( level=logging.INFO )
    logger = logging.getLogger( 'main' )

    ini_path = os.path.join( os.path.dirname( 
        os.path.realpath( __file__ ) ), 'misplay.ini' )

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

    status = MisplayEPD2in13(
        fifo_path, dsp_refresh, w, h, r, wp_int, wp_path, font_fam, font_size )

    @atexit.register
    def shutdown_display():
        status.clear()

    status.loop()

