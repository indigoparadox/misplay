
import unittest
import os
import sys
import time
from unittest.mock import Mock, patch
from contextlib import ExitStack

sys.path.append( os.path.dirname( os.path.dirname( __file__ ) ) )

class TestSources( unittest.TestCase ):

    def test_sources_fifo( self ):

        args = {
            'panel': Mock(),
            'fifo': 'fifo path test',
            'fifopoll': 0.1
        }

        with ExitStack() as stack:
            os_mkfifo = stack.enter_context( patch( 'os.mkfifo', autospec=True ) )
            os_open = stack.enter_context( patch( 'os.open', autospec=True ) )
            os_read = stack.enter_context( patch( 'os.read', autospec=True ) )

            from misplay.sources import fifo

            fifo.FIFOThread.start = Mock()
            fifo_src = fifo.FIFOSource( **args )

            fifo_src._fifo_thread.start.assert_called()

            fifo_buf = fifo_src._fifo_thread.source.read_fifo()
            if fifo_buf:
                fifo_src._fifo_thread.source.panel.add_message( fifo_buf )
            time.sleep( fifo_src._fifo_thread.source.fifo_poll )

            os_open.assert_called_once_with( 'fifo path test', 2048 )
            os_read.assert_called_once()
