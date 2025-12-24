#!/usr/bin/env python3
"""
Enoch Scraper - Zion Engine
- Parses the index page of the Book of Enoch on sacred-texts.com.
- Finds all links to individual chapters.
- Loops through each chapter link, downloads the HTML.
- Cleans the HTML to extract the pure text.
- Appends the text from all chapters into a single file.
"""

import requests
import re
import sys
from pathlib import Path
import time

# --- CONFIGURATION ---
BASE_URL = "https://www.sacred-texts.com/bib/boe/"
INDEX_PAGE_URL = f"{BASE_URL}index.htm"
OUTPUT_PATH = Path(__file__).parent / "sacred_texts" / "book_of_enoch_complete.txt"

def get_chapter_links(index_html):
    """Find all chapter links (e.g., boe001.htm) from the index HTML."""
    # This more robust regex ignores case and handles single/double quotes and extra spaces.
    links = re.findall(r'href\s*=\s*["\'](boe\d{3}\.htm)["\']', index_html, re.IGNORECASE)
    # Remove duplicates and maintain order
    unique_links = sorted(list(set(links)))
    print(f"Found {len(unique_links)} unique chapter links.")
    return unique_links

def scrape_and_clean_chapter(chapter_path):
    """Downloads a chapter page, cleans the HTML, and returns the text."""
    url = f"{BASE_URL}{chapter_path}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        html = response.text

        # --- Text Cleaning ---
        # This is a rough but effective way to get the core content.
        # It looks for the main content block and strips HTML tags.
        
        # 1. Isolate the main body content (crude but often works)
        body_match = re.search(r'<BODY(.*?)>(.*?)</BODY>', html, re.DOTALL | re.IGNORECASE)
        if body_match:
            content = body_match.group(2)
        else:
            content = html # Fallback to full HTML

        # 2. Remove script and style blocks
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # 3. Remove all remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # 4. Decode HTML entities like &nbsp;
        import html
        content = html.unescape(content)
        
        # 5. Clean up whitespace
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        
        # A final cleanup to remove the site's own header/footer text
        clean_text = re.sub(r'Sacred Texts.*?Next:?','', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'Previous:.*?Index','', clean_text, flags=re.DOTALL)

        return clean_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"  - ❌ Failed to download {url}: {e}")
        return None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📖 ENOCH WEB SCRAPER - ZION ENGINE")
    print("="*70 + "\n")

    try:
        print("1. Fetching index page...")
        index_response = requests.get(INDEX_PAGE_URL, timeout=15)
        index_response.raise_for_status()
        index_html = index_response.text
        print("✅ Index page fetched.")

        print("\n2. Extracting chapter links...")
        chapter_links = get_chapter_links(index_html)
        if not chapter_links:
            print("❌ No chapter links found. Cannot proceed.")
            sys.exit(1)

        print("\n3. Scraping all chapters... (this will take a moment)")
        full_text = ""
        for i, link in enumerate(chapter_links):
            print(f"   - Scraping chapter {i+1}/{len(chapter_links)}: {link}")
            chapter_content = scrape_and_clean_chapter(link)
            if chapter_content:
                full_text += chapter_content + "\n\n"
            time.sleep(0.5) # Be respectful to the server, pause between requests

        print("✅ All chapters scraped and cleaned.")

        print(f"\n4. Saving complete text to {OUTPUT_PATH}...")
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print("✅ Save complete.")

        print("\n" + "="*70)
        print("🎉 SCRAPING COMPLETE")
        print("="*70)
        print(f"The full, clean text of the Book of Enoch is now available at:\n{OUTPUT_PATH}")

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
