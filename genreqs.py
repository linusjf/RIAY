#!/usr/bin/env python
"""
Genreqs.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : genreqs
# @created     : Thursday Jul 17, 2025 12:57:22 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import os
import re
import subprocess
from pathlib import Path

project_dir = Path(".")
imported_modules = set()

# Match import and from-import lines
pattern = re.compile(r"^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)")

# Step 1: Find all imported top-level modules
for py_file in project_dir.rglob("*.py"):
    try:
        for line in py_file.read_text(errors="ignore").splitlines():
            match = pattern.match(line)
            if match:
                mod = match.group(1).split(".")[0]
                if mod not in ("__future__", "typing", "os", "sys"):  # stdlib filter hint
                    imported_modules.add(mod)
    except Exception:
        continue

# Step 2: Get installed packages
installed = {
    pkg.split("==")[0].lower(): pkg
    for pkg in subprocess.getoutput("pip freeze").splitlines()
}

# Step 3: Match imported modules to installed packages
found = []
unmatched = []

for mod in sorted(imported_modules):
    if mod.lower() in installed:
        found.append(installed[mod.lower()])
    else:
        unmatched.append(mod)

# Step 4: Output
with open("deps.txt", "w") as f:
    f.write("\n".join(sorted(found)) + "\n")

print(f"✅ Saved {len(found)} dependencies to deps.txt")
if unmatched:
    print("⚠️ Unmatched imports (manual check may be needed):")
    print(", ".join(unmatched))
