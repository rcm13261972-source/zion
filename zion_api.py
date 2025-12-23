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
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("="*70)
    print("💎 ZION TRUTH ENGINE - API SERVER (v2)")
    print("="*70)
    print(f"\nPHI = {PHI:.10f}")
    print("\nStarting server on http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /health       - Check if server is running")
    print("  POST /analyze      - Analyze single text")
    print("\nPress Ctrl+C to stop")
    print("="*70)
    print()
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=False)
