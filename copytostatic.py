#!/usr/bin/env python3
import os
import shutil

SOURCE_ROOT = '.'  # Root of your project
TARGET_IMGS_ROOT = os.path.join('_static', 'images')
TARGET_PDFS_ROOT = os.path.join('_static', 'pdfs')
# Directories to skip
EXCLUDED_DIRS = {'_static', 'build', 'styles', 'tests', '.git'}

def collect_jpg_files_with_paths(source_root, target_root):
    for root, dirs, files in os.walk(source_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.lower().endswith('.jpg'):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source_root)
                dst_path = os.path.join(target_root, rel_path)

                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                if os.path.abspath(src_path) != os.path.abspath(dst_path):
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied {src_path} to {dst_path}")

def collect_pdf_files_with_paths(source_root, target_root):
    for root, dirs, files in os.walk(source_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.lower().endswith('.pdf'):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source_root)
                dst_path = os.path.join(target_root, rel_path)

                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                if os.path.abspath(src_path) != os.path.abspath(dst_path):
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied {src_path} to {dst_path}")

if __name__ == "__main__":
    collect_jpg_files_with_paths(SOURCE_ROOT, TARGET_IMGS_ROOT)
    collect_pdf_files_with_paths(SOURCE_ROOT, TARGET_PDFS_ROOT)
