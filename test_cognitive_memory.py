#!/usr/bin/env python3
"""
Tests for cognitive_memory.py - DiscernmentEngine
"""

import unittest
import sys
from pathlib import Path

# Add zion-engine to sys.path
ZION_DIR = Path(__file__).parent
if str(ZION_DIR) not in sys.path:
    sys.path.insert(0, str(ZION_DIR))

from cognitive_memory import DiscernmentEngine, GOLD_THRESHOLD, STANDARD_THRESHOLD

class TestDiscernmentEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DiscernmentEngine()

    def test_score_empty_text(self):
        """
        Tests that empty or whitespace-only text returns a zero score.
        """
        scores = self.engine.score("")
        self.assertEqual(scores['overall'], 0.0)
        self.assertEqual(scores['tier'], 'LOW')

        scores = self.engine.score("   ")
        self.assertEqual(scores['overall'], 0.0)
        self.assertEqual(scores['tier'], 'LOW')

    def test_score_technical_text(self):
        """
        Tests a purely technical text for low resonance.
        """
        text = "Implement a REST API endpoint for user authentication with JWT tokens."
        scores = self.engine.score(text)
        self.assertLess(scores['overall'], STANDARD_THRESHOLD)
        self.assertEqual(scores['tier'], 'LOW')
        self.assertLess(scores['truth_markers'], 0.2) # Should be very low for truth markers

    def test_score_emotional_low_stakes_text(self):
        """
        Tests emotional text with low personal stakes.
        """
        text = "I feel happy today because the sun is shining."
        scores = self.engine.score(text)
        self.assertGreater(scores['overall'], 0.2)
        self.assertLess(scores['overall'], STANDARD_THRESHOLD) # Not high enough for STANDARD
        self.assertGreater(scores['emotional_resonance'], 0.5)

    def test_score_high_resonance_text_gold(self):
        """
        Tests a text with high vulnerability and sacrifice for GOLD resonance.
        """
        text = "I gave up everything for this, my love. It cost me so much, but I need you to understand. I'm scared."
        scores = self.engine.score(text)
        self.assertGreaterEqual(scores['overall'], GOLD_THRESHOLD)
        self.assertEqual(scores['tier'], 'GOLD')
        self.assertGreater(scores['truth_markers'], 0.8) # High truth markers
        self.assertGreater(scores['emotional_resonance'], 0.7) # High emotional resonance

    def test_score_standard_resonance_text(self):
        """
        Tests a text with moderate emotional content for STANDARD resonance.
        """
        text = "I'm worried about the court date, my love. I can't stop thinking about what might happen."
        scores = self.engine.score(text)
        self.assertGreaterEqual(scores['overall'], STANDARD_THRESHOLD)
        self.assertLess(scores['overall'], GOLD_THRESHOLD)
        self.assertEqual(scores['tier'], 'STANDARD')
        self.assertGreater(scores['truth_markers'], 0.3)
        self.assertGreater(scores['emotional_resonance'], 0.5)

if __name__ == '__main__':
    unittest.main()
