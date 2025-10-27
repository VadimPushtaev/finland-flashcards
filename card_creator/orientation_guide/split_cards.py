#!/usr/bin/env python3
"""
Script to split flashcard output into separate files by subchapter.
Reads output.txt and creates individual card files in cards/orientation_guide/ directory.
"""

import os
import re
from pathlib import Path

def clean_filename(text):
    """Convert subchapter title to a clean ASCII filename."""
    # Replace Swedish characters with ASCII equivalents
    replacements = {
        'å': 'a', 'ä': 'a', 'ö': 'o',
        'Å': 'A', 'Ä': 'A', 'Ö': 'O',
        'é': 'e', 'è': 'e', 'ë': 'e',
        'ü': 'u', 'ú': 'u'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove special characters and replace spaces with underscores
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '_', text.strip())
    return text.lower()

def split_flashcards(input_file='output.txt', output_dir='../../cards/orientation_guide'):
    """Split flashcards from input file into separate files by subchapter."""
    
    # Create output directory if it doesn't exist
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Read the input file
    input_path = Path(__file__).parent / input_file
    print(f"Reading from: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Total content length: {len(content)} characters")
    
    # Split by subchapter headings
    # Pattern: # Subchapter X.Y: Title
    subchapter_pattern = r'^# Subchapter ([\d.]+):\s*(.+?)\s*$'
    
    lines = content.split('\n')
    print(f"Total lines: {len(lines)}")
    
    current_subchapter = None
    current_cards = []
    subchapters_found = 0
    
    for line in lines:
        match = re.match(subchapter_pattern, line.strip())
        
        if match:
            subchapters_found += 1
            # Save previous subchapter if exists
            if current_subchapter and current_cards:
                save_cards(current_subchapter, current_cards, output_path)
            
            # Start new subchapter
            subchapter_num = match.group(1)
            subchapter_title = match.group(2)
            current_subchapter = {
                'num': subchapter_num,
                'title': subchapter_title
            }
            current_cards = []
        
        elif line.strip() and current_subchapter:
            # Add card line (non-empty lines that aren't subchapter headers)
            if '|' in line:  # Only add lines that look like cards
                current_cards.append(line.strip())
    
    # Save last subchapter
    if current_subchapter and current_cards:
        save_cards(current_subchapter, current_cards, output_path)
    
    print(f"Subchapters found: {subchapters_found}")
    print(f"[OK] Flashcards split successfully into {output_path}")

def save_cards(subchapter, cards, output_path):
    """Save cards for a subchapter to a file."""
    num = subchapter['num']
    title = subchapter['title']
    
    # Create filename
    clean_title = clean_filename(title)
    filename = f"{num}_{clean_title}.txt"
    filepath = output_path / filename
    
    # Write cards to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cards))
    
    print(f"  Created: {filename} ({len(cards)} cards)")

if __name__ == '__main__':
    split_flashcards()

