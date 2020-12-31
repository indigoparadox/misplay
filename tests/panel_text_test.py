
import unittest
from misplay.displays.dummy import DummyDisplay
from misplay.panels.panel import TextPanel

class PanelTextTester( unittest.TestCase ):

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
            'panel': 'static',
            'size': '19',
            'lines': '3',
            'text': 'fii;foo;faa'
        }
        self.panel = TextPanel( **panel_cfg )
        display_cfg['panels'] = [self.panel]

        self.display = DummyDisplay( **display_cfg )

    def test_line_height( self ):
        self.assertEqual( self.panel.line_height(), 18 )

    def test_line_height_0( self ):
        self.assertEqual( self.panel.line_height( 0 ), 18 )

    def test_line_height_1( self ):
        self.assertEqual( self.panel.line_height( 1 ), 18 )

    def test_line_height_1( self ):
        self.assertEqual( self.panel.line_height( 2 ), 18 )

    def test_panel_lines_height( self ):
        self.assertEqual( self.panel.panel_lines_height(), 63 )

