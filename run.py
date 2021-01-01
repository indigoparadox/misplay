#!/usr/bin/env python3

from misplay.displays.epd2in13 import EPD2in13
from misplay.displays.misplay import RefreshException
from misplay.panels.panel import RowsPanel, TextPanel
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
        status.stop()
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
        elif 'ipc' == panel_cfg['panel']:
            from misplay.panels.ipc import IPCPanel
            panel = IPCPanel( **panel_cfg )
        elif 'mpd' == panel_cfg['panel']:
            from misplay.panels.mpd import MPDPanel
            panel = MPDPanel( **panel_cfg )
        elif 'text' == panel_cfg['panel']:
            panel = TextPanel( **panel_cfg )
        parent.append( panel )

def create_misplay( ini_path ):
    logger = logging.getLogger( 'create.misplay' )

    # Load config.
    logger.info( 'using config at {}'.format( ini_path ) )

    config = configparser.ConfigParser()
    config.read( ini_path )

    display_cfg = dict( config.items( 'display' ) )
    display_cfg.update( dict( config.items( display_cfg['type'] ) ) )

    col_keys = config['display']['columns'].split( ',' )
    display_cfg['panels'] = []
    create_panels( ini_path, col_keys, display_cfg['panels'] )

    del display_cfg['type']
    del display_cfg['columns']

    return EPD2in13( **display_cfg )

def main():
    global status

    parser = argparse.ArgumentParser()

    verbosity_grp = parser.add_mutually_exclusive_group()
    
    verbosity_grp.add_argument( '-v', '--verbose', action='store_true' )

    verbosity_grp.add_argument( '-q', '--quiet', action='store_true' )

    parser.add_argument( '-c', '--config', action='store' )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig( level=logging.DEBUG )
    elif args.quiet:
        logging.basicConfig( level=logging.ERROR )
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
            status = create_misplay( ini_path )
            status.loop()

        except RefreshException:
            do_reload = True

if '__main__' == __name__:
    main()

