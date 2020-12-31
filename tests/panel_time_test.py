
import unittest
from misplay.displays.dummy import DummyDisplay
from misplay.panels.time import TimePanel

class PanelTimeTester( unittest.TestCase ):

    def setUp( self ):
        display_cfg = {
            'refresh': '0.5',
            'margins': '3',
            'font': '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            'size': '13',
            'height': '122',
            'width': '250',
            'rotate': '0'
        }

        panel_cfg = {
            'panel': 'time',
            'size': '18',
            'dtsize': '14',
            'date': 'true'
        }
        self.panel = TimePanel( **panel_cfg )
        display_cfg['panels'] = [self.panel]

        self.display = DummyDisplay( **display_cfg )

    def test_line_height_0( self ):
        self.assertEqual( self.panel.line_height( 0 ), 17 )

    def test_line_height_1( self ):
        self.assertEqual( self.panel.line_height( 1 ), 14 )

    def test_panel_lines_height( self ):
        self.assertEqual( self.panel.panel_lines_height(), 37 )

