#!/usr/bin/env python3

from misplay.displays.epd2in13 import EPD2in13
from misplay.displays.misplay import RefreshException
from misplay.source import MQTTSource, FIFOSource
import logging
import os
import atexit
import configparser

@atexit.register
def shutdown_display():
    global status

    logger = logging.getLogger( 'main' )

    try:
        status.clear()
    except NameError as e:
        logger.error( e )

def create_mqtt( ini_path ):
    logger = logging.getLogger( 'create.source' )

    # Load config.
    logger.info( 'using config at {}'.format( ini_path ) )

    config = configparser.ConfigParser()
    config.read( ini_path )
    uid = config.get( 'ipc.mqtt', 'uid' )
    host = config.get( 'ipc.mqtt', 'host' )
    port = config.getint( 'ipc.mqtt', 'port' )
    topic = config.get( 'ipc.mqtt', 'topic' )
    ssl = config.getboolean( 'ipc.mqtt', 'ssl' )
    ca = config.get( 'ipc.mqtt', 'ca' )

    return MQTTSource( uid, host, port, topic, ssl, ca )

def create_fifo( ini_path ):
    logger = logging.getLogger( 'create.source' )

    # Load config.
    logger.info( 'using config at {}'.format( ini_path ) )

    config = configparser.ConfigParser()
    config.read( ini_path )
    fifo_path = config['ipc']['fifo']

    return FIFOSource( fifo_path )

def create_misplay( ini_path, sources ):
    logger = logging.getLogger( 'create.misplay' )

    # Load config.
    logger.info( 'using config at {}'.format( ini_path ) )

    config = configparser.ConfigParser()
    config.read( ini_path )
    wp_interval = config.getint( 'display', 'wallpapers-interval' )
    dsp_refresh = config.getint( 'display', 'refresh' )
    wp_int = config.getint( 'display', 'wallpapers-interval' )
    wp_path = config['display']['wallpapers-path']
    display_type = 'epd2in13'
    w = config.getint( display_type, 'width' )
    h = config.getint( display_type, 'height' )
    r = config.getint( display_type, 'rotate' )
    font_fam = config[display_type]['font']
    font_size = config.getint( display_type, 'font-size' )

    return EPD2in13(
        dsp_refresh, w, h, r, sources, wp_int, wp_path, font_fam, font_size )

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
            sources = []
            sources.append( create_fifo( ini_path ) )
            #src = create_mqtt( ini_path )
            status = create_misplay( ini_path, sources )
            status.loop()

        except RefreshException:
            do_reload = True

if '__main__' == __name__:
    main()

