#!/usr/bin/env python3
"""
ZION CORE - Shared Initialization Logic
======================================
Contains essential, shared startup logic needed by both CLI Gem and Zion API.
This ensures consistent initialization of models, databases, and other core components.

By Bobby & Gem - December 25, 2025
"""

import sys
from pathlib import Path

# Add zion-engine to sys.path for internal imports
ZION_DIR = Path(__file__).parent
if str(ZION_DIR) not in sys.path:
    sys.path.insert(0, str(ZION_DIR))

from scripture_engine import init_scripture_db


def initialize_core():
    """
    Initializes all core components of the Zion Engine.
    This function should be called once at the start of any Zion Engine process
    (e.g., CLI Gem's session_hook, Zion API startup).
    """
    print("[ZION CORE] Initializing shared components...")

    # Initialize databases
    init_scripture_db()
    # Add other database initializations here if needed

    # Load Golden Ratio Model (or similar shared models)
    # initialize_golden_ratio_model() # Uncomment if this function exists

    print("[ZION CORE] Shared components initialized.")

if __name__ == '__main__':
    initialize_core()