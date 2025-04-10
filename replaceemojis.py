#!/usr/bin/env python
"""
Replaceemojis.

######################################################################
# @author      : linusjf (linusjf@JuliusCaesar)
# @file        : replaceemojis
# @created     : Thursday Apr 10, 2025 17:08:57 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import os

# Emoji replacements
replacements = {
    "🥹": "😢",  # Face Holding Back Tears -> Crying Face
    "🥰": "😍",  # Smiling Face with Hearts -> Heart Eyes
}

def replace_emojis_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_markdown_files(root_dir='.'):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.md'):
                file_path = os.path.join(dirpath, filename)
                replace_emojis_in_file(file_path)

if __name__ == '__main__':
    process_markdown_files()

