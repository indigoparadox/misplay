#!/usr/bin/env python3

import os
import atexit
import configparser
import argparse
import socket
import logging
from urllib.parse import urlparse
from logging.handlers import SMTPHandler

from misplay.panels.panel import RowsPanel, TextPanel # pylint: disable=import-error

@atexit.register
def shutdown_display():
    global status
    try:
        status.stop()
    except NameError as exc:
        logging.getLogger( 'main' ).error( exc )

def create_panels( config, panel_keys, parent=None ):

    logger = logging.getLogger( 'create.panels' )

    for key in panel_keys:
        logger.info( 'creating panel for %s...', key )
        panel_cfg = dict( config.items( 'panel-{}'.format( key ) ) )
        panel =  None
        if 'wallpaper' == panel_cfg['panel']:
            from misplay.panels.wallpaper import WallpaperPanel # pylint: disable=import-error
            panel = WallpaperPanel( **panel_cfg )
        elif 'time' == panel_cfg['panel']:
            from misplay.panels.time import TimePanel # pylint: disable=import-error
            panel = TimePanel( **panel_cfg )
        elif 'rows' == panel_cfg['panel']:
            panel = RowsPanel( **panel_cfg )
            child_keys = panel_cfg['rows'].split( ',' )
            create_panels( config, child_keys, panel.rows )
        elif 'ipc' == panel_cfg['panel']:
            from misplay.panels.ipc import IPCPanel # pylint: disable=import-error
            panel = IPCPanel( **panel_cfg )
        elif 'mpd' == panel_cfg['panel']:
            from misplay.panels.mpd import MPDPanel # pylint: disable=import-error
            panel = MPDPanel( **panel_cfg )
        elif 'text' == panel_cfg['panel']:
            panel = TextPanel( **panel_cfg )
        parent.append( panel )

def create_misplay( config ):

    display_cfg = dict( config.items( 'display' ) )
    display_cfg.update( dict( config.items( display_cfg['type'] ) ) )

    col_keys = config['display']['columns'].split( ',' )
    display_cfg['panels'] = []
    create_panels( config, col_keys, display_cfg['panels'] )

    del display_cfg['type']
    del display_cfg['columns']

    # TODO: Make this modular.
    from misplay.displays.epd2in13 import EPD2in13 # pylint: disable=import-error

    return EPD2in13( **display_cfg )

def main():
    global status

    parser = argparse.ArgumentParser()

    verbosity_grp = parser.add_mutually_exclusive_group()

    verbosity_grp.add_argument( '-v', '--verbose', action='store_true' )

    verbosity_grp.add_argument( '-q', '--quiet', action='store_true' )

    parser.add_argument( '-c', '--config', action='store', default='misplay.ini' )

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

    config = configparser.ConfigParser()
    config.read( ini_path )

    try:
        if config.getboolean( 'reporter', 'enable' ):
            smtp_url = urlparse( config.get( 'reporter', 'url' ) )
            sender = 'misplay@{}'.format( socket.gethostname() )
            try:
                sender = config.get( 'reporter', 'sender' )
            except configparser.NoOptionError:
                pass
            smtp_handler = SMTPHandler(
                smtp_url.hostname,
                sender,
                config.get( 'reporter', 'receivers' ).split( ',' ),
                '[misplay] Exception Log' )
            smtp_handler.setLevel( logging.ERROR )
            logging.getLogger().addHandler( smtp_handler )
    except Exception as exc:
        logger.info( '%s while setting up reporter: %s', type( exc ), exc )

    while do_reload:
        do_reload = False
        try:
            status = create_misplay( config )
            status.loop()

        except Exception as exc:
            logger.error( '%s: %s', type( exc ), exc )
            do_reload = True

if '__main__' == __name__:
    try:
        main()
    except RuntimeError as exc:
        logging.getLogger( 'main' ).error( '%s: %s', type( exc ), exc )
