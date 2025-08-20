#!/usr/bin/env python
"""
Fileutils.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : fileutils
# @created     : Wednesday Aug 20, 2025 18:38:28 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import shutil
import os

def copy_file(source: str, destination: str) -> bool:
    """
    Copy a file from source to destination.

    Args:
        source (str): Path to the source file.
        destination (str): Path to the destination file or directory.

    Returns:
        bool: True if copy succeeded, False otherwise.
    """
    try:
        if not os.path.isfile(source):
            return False

        # If destination is a directory, append the filename
        if os.path.isdir(destination):
            destination = os.path.join(destination, os.path.basename(source))

        shutil.copy2(source, destination)  # copy2 preserves metadata
        return True

    except Exception:
        return False
