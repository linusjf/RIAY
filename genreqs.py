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
import re
import subprocess
from pathlib import Path
from typing import Set, Dict, List, Match, Optional

project_dir = Path(".")
imported_modules: Set[str] = set()

# Match import and from-import lines
pattern: re.Pattern = re.compile(r"^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)")

def get_imported_modules() -> None:
    """Find all imported top-level modules."""
    for py_file in project_dir.rglob("*.py"):
        try:
            for line in py_file.read_text(errors="ignore").splitlines():
                match: Optional[Match[str]] = pattern.match(line)
                if match:
                    mod: str = match.group(1).split(".")[0]
                    if mod not in ("__future__", "typing", "os", "sys"):  # stdlib filter hint
                        imported_modules.add(mod)
        except Exception:
            continue

def get_installed_packages() -> Dict[str, str]:
    """Get installed packages from pip freeze."""
    return {
        pkg.split("==")[0].lower(): pkg
        for pkg in subprocess.getoutput("pip freeze").splitlines()
    }

def match_packages() -> tuple[List[str], List[str]]:
    """Match imported modules to installed packages."""
    installed: Dict[str, str] = get_installed_packages()
    found: List[str] = []
    unmatched: List[str] = []

    for mod in sorted(imported_modules):
        if mod.lower() in installed:
            found.append(installed[mod.lower()])
        else:
            unmatched.append(mod)
    return found, unmatched

def write_dependencies(found: List[str]) -> None:
    """Write dependencies to deps.txt."""
    with open("deps.txt", "w") as f:
        f.write("\n".join(sorted(found)) + "\n")

def main() -> None:
    """Main execution function."""
    get_imported_modules()
    found, unmatched = match_packages()
    write_dependencies(found)

    print(f"✅ Saved {len(found)} dependencies to deps.txt")
    if unmatched:
        print("⚠️ Unmatched imports (manual check may be needed):")
        print(", ".join(unmatched))

if __name__ == "__main__":
    main()
