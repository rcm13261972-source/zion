#!/usr/bin/env python3
"""
A tool to download and clean plain text from a URL,
specifically designed to handle Project Gutenberg files.
"""

import requests
import sys
import os

def download_and_clean(url, output_path):
    """
    Downloads text from a URL, attempts to clean Gutenberg headers/footers,
    and saves it to the specified output path.
    """
    try:
        print(f"⬇️ Downloading from {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        raw_text = response.text
        print("Download complete.")

        clean_text = raw_text
        
        # Try to strip Gutenberg headers/footers
        start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
        end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"

        # Find the second occurrence of the start marker if it exists
        try:
            start_index = raw_text.index(start_marker, raw_text.index(start_marker) + 1)
            # Find the position of the newline after the marker
            start_index = raw_text.index('\n', start_index) + 1
            clean_text = raw_text[start_index:]
            print("Gutenberg header found and stripped.")
        except ValueError:
            # If the start marker isn't found twice, we're likely in a file without a ToC header
            try:
                start_index = raw_text.index(start_marker)
                start_index = raw_text.index('\n', start_index) + 1
                clean_text = raw_text[start_index:]
                print("Gutenberg header found and stripped.")
            except ValueError:
                print("Could not find Gutenberg markers. Using raw text.")

        try:
            end_index = clean_text.rindex(end_marker)
            clean_text = clean_text[:end_index].strip()
            print("Gutenberg footer found and stripped.")
        except ValueError:
            print("Gutenberg footer not found. Saving raw text.")

        # Save the cleaned text
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        
        print(f"Successfully saved clean text to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to download from URL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 download_text.py <URL> <output_filepath>")
        sys.exit(1)
    
    url_to_download = sys.argv[1]
    path_to_save = sys.argv[2]
    
    download_and_clean(url_to_download, path_to_save)
