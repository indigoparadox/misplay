#!/usr/bin/env python3

from tests.panel_time_test import PanelTimeTester
from tests.panel_text_test import PanelTextTester
import unittest
import logging

if '__main__' == __name__:
    logging.basicConfig( level=logging.DEBUG )
    unittest.main()

