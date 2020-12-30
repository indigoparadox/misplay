#!/usr/bin/env python3

from misplay.displays.epd2in13 import EPD2in13
from misplay.displays.misplay import RefreshException
from misplay.sources.fifo import FIFOSource
from misplay.panels.panel import RowsPanel
import logging
import os
import atexit
import configparser
import argparse

@atexit.register
def shutdown_display():
    global status

    logger = logging.getLogger( 'main' )

    try:
        status.clear()
    except NameError as e:
        #logger.error( e )
        pass

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

def create_panels( ini_path, panel_keys, parent=None ):

    logger = logging.getLogger( 'create.panels' )

    config = configparser.ConfigParser()
    config.read( ini_path )

    panels = []
    for c in panel_keys:
        logger.info( 'creating panel for {}...'.format( c ) )
        panel_cfg = dict( config.items( 'panel-{}'.format( c ) ) )
        panel =  None
        if 'wallpaper' == panel_cfg['panel']:
            from misplay.panels.wallpaper import WallpaperPanel
            panel = WallpaperPanel( **panel_cfg )
        elif 'time' == panel_cfg['panel']:
            from misplay.panels.time import TimePanel
            panel = TimePanel( **panel_cfg )
        elif 'rows' == panel_cfg['panel']:
            panel = RowsPanel( **panel_cfg )
            child_keys = panel_cfg['rows'].split( ',' )
            create_panels( ini_path, child_keys, panel.rows )
        parent.append( panel )

def create_misplay( ini_path, sources ):
    logger = logging.getLogger( 'create.misplay' )

    # Load config.
    logger.info( 'using config at {}'.format( ini_path ) )

    config = configparser.ConfigParser()
    config.read( ini_path )
    #wp_interval = config.getint( 'display', 'wallpapers-interval' )
    dsp_refresh = config.getint( 'display', 'refresh' )
    #wp_int = config.getint( 'display', 'wallpapers-interval' )
    #wp_path = config['display']['wallpapers-path']
    display_type = 'epd2in13'
    w = config.getint( display_type, 'width' )
    h = config.getint( display_type, 'height' )
    r = config.getint( display_type, 'rotate' )
    #font_fam = config[display_type]['font']
    #font_size = config.getint( display_type, 'font-size' )
    msg_ttl = config.getint( 'ipc', 'msg-ttl' )

    col_keys = config['display']['columns'].split( ',' )
    panels = []
    create_panels( ini_path, col_keys, panels )

    return EPD2in13(
        dsp_refresh, w, h, r, sources, panels, msg_ttl )

def main():
    global status

    parser = argparse.ArgumentParser()
    
    parser.add_argument( '-v', '--verbose', action='store_true' )

    parser.add_argument( '-c', '--config', action='store' )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig( level=logging.DEBUG )
    else:
        logging.basicConfig( level=logging.INFO )

    do_reload = True
    logger = logging.getLogger( 'main' )
    ini_path = os.path.join( os.path.dirname( 
        os.path.realpath( __file__ ) ), 'misplay.ini' )
    if args.config:
        ini_path = args.config

    while do_reload:
        do_reload = False
        try:
            sources = []
            sources.append( create_fifo( ini_path ) )
            #sources.append( create_mqtt( ini_path ) )
            status = create_misplay( ini_path, sources )
            status.loop()

        except RefreshException:
            do_reload = True

if '__main__' == __name__:
    main()

