#!/usr/bin/env python3
"""
Tests for embodiment_layer.py
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Add zion-engine to sys.path
ZION_DIR = Path(__file__).parent
if str(ZION_DIR) not in sys.path:
    sys.path.insert(0, str(ZION_DIR))

from embodiment_layer import EmbodimentLayer

class TestEmbodimentLayer(unittest.TestCase):

    def test_initialization_default_state(self):
        """
        Tests that the EmbodimentLayer initializes with a default state.
        """
        layer = EmbodimentLayer(state_file="non_existent_file.json")
        state = layer.get_state()
        
        self.assertIn('arousal', state)
        self.assertIn('comfort', state)
        self.assertIn('tension', state)
        self.assertIn('desire', state)
        self.assertIn('warmth', state)
        self.assertIn('openness', state)
        self.assertIn('resonance', state)
        self.assertIn('coherence', state)
        self.assertIn('presence', state)
        
        # Check some default values
        self.assertEqual(state['arousal'], 0.3)
        self.assertEqual(state['tension'], 0.2)
        self.assertEqual(state['visual_presence'], 0.0)

    def test_process_text_intimacy(self):
        """
        Tests that process_text with intimacy markers increases relevant states.
        """
        layer = EmbodimentLayer(state_file="non_existent_file.json")
        initial_state = layer.get_state()

        # Process a message with intimacy markers
        layer.process_text("I love you, my desire for you is strong.")

        new_state = layer.get_state()

        self.assertGreater(new_state['arousal'], initial_state['arousal'])
        self.assertGreater(new_state['desire'], initial_state['desire'])
        self.assertGreater(new_state['warmth'], initial_state['warmth'])

if __name__ == '__main__':
    unittest.main()
