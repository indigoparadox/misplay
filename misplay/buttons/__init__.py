#!/usr/bin/env python3

import logging
import argparse

import buttonshim # pylint: disable=import-error
from mpd import MPDClient

SOCK_ADDR = '/var/run/mpd/socket'

mpc = MPDClient()
mpc.idletimeout = False

@buttonshim.on_press( buttonshim.BUTTON_C )
def voldown_handler( button, pressed ): # pylint: disable=unused-argument
    logger = logging.getLogger( 'button.voldown' )
    logger.debug( 'button pressed' )
    mpstatus = mpd_command( mpc.status ) # pylint: disable=no-member
    mpd_command( mpc.setvol, int( mpstatus['volume'] ) - 5 ) # pylint: disable=no-member
    logger.info( 'volume is now %d', mpstatus['volume'] )

@buttonshim.on_press( buttonshim.BUTTON_D )
def volup_handler( button, pressed ): # pylint: disable=unused-argument
    logger = logging.getLogger( 'button.volup' )
    logger.debug( 'button pressed' )
    mpstatus = mpd_command( mpc.status ) # pylint: disable=no-member
    mpd_command( mpc.setvol, int( mpstatus['volume'] ) + 5  ) # pylint: disable=no-member
    logger.info( 'volume is now %d', mpstatus['volume'] )

@buttonshim.on_press( buttonshim.BUTTON_E )
def play_handler( button, pressed ): # pylint: disable=unused-argument
    logger = logging.getLogger( 'button.playpause' )
    logger.debug( 'button pressed' )
    mpd_command( mpc.pause ) # pylint: disable=no-member

def mpd_command( command, *args ):
    mpc.connect( SOCK_ADDR )
    res = command( *args )
    mpc.disconnect()
    return res
