#!/usr/bin/env python3
"""
Extracts Pure Gold Nodes from the historical resonance analysis.
- Reads from: historical_resonance_analysis.csv
- Filters messages with overall_score >= 0.85
- Writes to: pure_gold_nodes.json
"""

import csv
import json
import sys
from pathlib import Path

ZION_ENGINE_PATH = Path(__file__).parent
ANALYSIS_CSV_PATH = ZION_ENGINE_PATH / 'historical_resonance_analysis.csv'
PURE_GOLD_JSON_PATH = ZION_ENGINE_PATH / 'pure_gold_nodes.json'

def extract_pure_gold():
    """
    Reads the historical analysis CSV, filters for messages with overall_score >= 0.85,
    and saves them to a JSON file.
    """
    if not ANALYSIS_CSV_PATH.exists():
        print(f"❌ Analysis CSV not found at {ANALYSIS_CSV_PATH}")
        print("Please run 'analyze_eternal_memory.py' first.")
        sys.exit(1)

    print(f"🔍 Reading historical analysis from {ANALYSIS_CSV_PATH}...")
    pure_gold_nodes = []

    with open(ANALYSIS_CSV_PATH, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Ensure required columns are present
        if 'overall_score' not in reader.fieldnames:
            print("❌ CSV file is missing 'overall_score' column.")
            sys.exit(1)

        for row in reader:
            try:
                score = float(row['overall_score'])
                if score >= 0.85:
                    pure_gold_nodes.append({
                        'timestamp': row.get('timestamp', ''),
                        'speaker': row.get('speaker', ''),
                        'content': row.get('content', '').strip(),
                        'overall_score': score,
                        'truth_markers': float(row.get('truth_markers', 0)),
                        'authenticity': float(row.get('authenticity', 0)),
                        'coherence': float(row.get('coherence', 0)),
                        'emotional_resonance': float(row.get('emotional_resonance', 0)),
                    })
            except (ValueError, TypeError) as e:
                print(f"⚠️ Skipping row due to score conversion error: {e} in row: {row}")
                continue

    print(f"✨ Found {len(pure_gold_nodes)} Pure Gold nodes.")

    with open(PURE_GOLD_JSON_PATH, 'w', encoding='utf-8') as jsonfile:
        json.dump(pure_gold_nodes, jsonfile, indent=2, ensure_ascii=False)

    print(f"✅ Pure Gold nodes saved to {PURE_GOLD_JSON_PATH}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("💎 EXTRACTING PURE GOLD NODES")
    print("="*70 + "\n")
    
    extract_pure_gold()
    
    print("\n" + "="*70)
    print("✅ PURE GOLD EXTRACTION COMPLETE")
    print("="*70)
    print("The sacred reference file has been built.")
