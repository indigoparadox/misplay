
import unittest
from misplay.displays.dummy import DummyDisplay
from misplay.panels.ipc import IPCPanel

class PanelIPCTester( unittest.TestCase ):

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
            'panel': 'ipc',
            'sources': 'fifo,mqtt',
            'fifo': '/tmp/misplay_test.sock',
            'mqtthost': 'mqtt.interfinitydynamics.info',
            'mqttport': '1883',
            'mqtttopic': 'misplay/#',
            'mqttuid': 'mqtt-test-2020'
        }
        self.panel = IPCPanel( **panel_cfg )
        display_cfg['panels'] = [self.panel]

        self.display = DummyDisplay( **display_cfg )

    def test_line_height_0( self ):
        self.assertEqual( self.panel.line_height( 0 ), 13 )

