#!/usr/bin/env python3
"""
Tests for zion_core.py
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Add zion-engine to sys.path
ZION_DIR = Path(__file__).parent
if str(ZION_DIR) not in sys.path:
    sys.path.insert(0, str(ZION_DIR))

from zion_core import initialize_core

class TestZionCore(unittest.TestCase):

    @patch('zion_core.init_scripture_db')
    @patch('builtins.print')
    def test_initialize_core_calls_dependencies(self, mock_print, mock_init_scripture_db):
        """
        Tests that initialize_core() calls its dependency initializers.
        """
        initialize_core()
        mock_init_scripture_db.assert_called_once()
        self.assertIn("[ZION CORE] Initializing shared components...", [call.args[0] for call in mock_print.call_args_list])
        self.assertIn("[ZION CORE] Shared components initialized.", [call.args[0] for call in mock_print.call_args_list])

if __name__ == '__main__':
    unittest.main()
