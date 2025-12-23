#!/usr/bin/env python3
"""
Analysis Review Script
Reads the historical resonance analysis CSV and extracts key insights.
- Identifies Top 10 Breakthrough Moments (highest resonance)
- Identifies Top 10 Friction Points (lowest resonance)
"""

import csv
import sys
from pathlib import Path

ANALYSIS_FILE = Path(__file__).parent / 'historical_resonance_analysis.csv'

def review_results():
    """
    Reads the CSV, sorts by score, and prints the highest and lowest
    scoring messages.
    """
    if not ANALYSIS_FILE.exists():
        print(f"❌ Analysis file not found at {ANALYSIS_FILE}")
        print("Please run 'analyze_eternal_memory.py' first.")
        sys.exit(1)

    with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        # Use a try-except block to handle potential empty file or header issues
        try:
            reader = csv.DictReader(f)
            # Ensure required columns are present
            if not all(col in reader.fieldnames for col in ['overall_score', 'speaker', 'content']):
                print("❌ CSV file is missing required columns (overall_score, speaker, content).")
                return
            data = list(reader)
        except (csv.Error, Exception) as e:
            print(f"❌ Error reading or parsing CSV file: {e}")
            return

    if not data:
        print("No data found in analysis file.")
        return

    # Convert score to float for sorting, handling potential errors
    for row in data:
        try:
            row['overall_score'] = float(row['overall_score'])
        except (ValueError, TypeError):
            row['overall_score'] = 0.0 # Default to 0 if conversion fails

    # Sort by score
    data.sort(key=lambda x: x['overall_score'], reverse=True)

    print("\n" + "="*80)
    print("✨ TOP 10 BREAKTHROUGH MOMENTS (Highest Resonance) ✨")
    print("="*80)
    if len(data) > 0:
        for row in data[:10]:
            print(f"\nScore: {row['overall_score']:.4f} | Speaker: {row.get('speaker', 'N/A')}")
            print(f"   > {row.get('content', '').strip()[:250]}")
    else:
        print("No breakthrough moments found.")

    print("\n\n" + "="*80)
    print("⚠ TOP 10 FRICTION POINTS (Lowest Resonance) ⚠")
    print("="*80)
    if len(data) > 0:
        # We want the 10 lowest scores that are NOT zero (as zero often means empty lines)
        non_zero_data = [row for row in data if row['overall_score'] > 0.0]
        lowest_data = sorted(non_zero_data, key=lambda x: x['overall_score'])
        
        for row in lowest_data[:10]:
            print(f"\nScore: {row['overall_score']:.4f} | Speaker: {row.get('speaker', 'N/A')}")
            print(f"   > {row.get('content', '').strip()[:250]}")
    else:
        print("No friction points found.")

    print("\n" + "="*80)


if __name__ == '__main__':
    review_results()
