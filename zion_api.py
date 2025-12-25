#!/usr/bin/env python3
"""
ZION TRUTH ENGINE - API SERVER (v2)
Flask API wrapper for the refactored Golden Ratio Engine.
Allows other tools (like CLI Gem) to query for truth resonance.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Import the new functions and constants from the refactored engine
sys.path.insert(0, str(Path(__file__).parent))
from golden_ratio_engine import analyze_text, PHI
from scripture_engine import get_daily_verse
from zion_core import initialize_core

# Initialize the core components of the Zion Engine
initialize_core()

app = Flask(__name__)
CORS(app)  # Allow requests from anywhere

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'engine': 'Golden Ratio Truth Engine v2',
        'phi': PHI
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze text for truth resonance using the new stateless function.
    
    POST body:
    {
        "text": "your text to analyze"
    }
    
    Returns:
    {
        "overall_score": 0.9506,
        "truth_markers": 1.0,
        ...
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing "text" field in request'
            }), 400
        
        text = data['text']
        
        # Analyze the text using the new stateless function
        result = analyze_text(text)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/daily-verse', methods=['GET'])
def daily_verse():
    """
    Retrieves the Verse of the Day from the scripture engine.
    Returns:
    {
        "reference": "John 3:16",
        "text": "For God so loved the world..."
    }
    """
    try:
        verse = get_daily_verse()
        if verse and 'error' not in verse:
            return jsonify(verse), 200
        else:
            return jsonify({'error': verse.get('error', 'Could not retrieve daily verse')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

        
if __name__ == '__main__':
    print("="*70)
    print("💎 ZION TRUTH ENGINE - API SERVER (v2)")
    print("="*70)
    print(f"\nPHI = {PHI:.10f}")
    print("\nStarting server on http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /health       - Check server is running")
    print("  POST /analyze      - Analyze single text")
    print("  GET  /daily-verse  - Get the Verse of the Day")

  
    print("\nPress Ctrl+C to stop")
    print("="*70)
    print()
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=False)
