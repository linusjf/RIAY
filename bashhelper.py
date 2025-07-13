"""Utilities for working with bash configuration files and environment variables."""

import os
import re
from typing import Dict, List

from dotenv import dotenv_values


def parse_bash_array(file_path: str, var_name: str) -> List[str]:
    """Parse a bash array from a file and return its values as a Python list.

    Args:
        file_path: Path to the bash file containing the array definition.
        var_name: Name of the array variable to parse.

    Returns:
        List of string values from the array, or empty list if not found.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Match array definition like: VAR=( "a" "b" "c" )
    pattern = re.compile(rf'{var_name}\s*=\s*\((.*?)\)', re.DOTALL)
    match = pattern.search(content)
    if not match:
        return []

    array_body = match.group(1)
    # Extract all quoted strings
    return re.findall(r'"(.*?)"', array_body)


def load_dotenv_with_system_interpolation(
    dotenv_path: str = ".env",
    override: bool = False
) -> Dict[str, str]:
    """Load .env file with expansion of existing environment variables.

    Args:
        dotenv_path: Path to the .env file (default: ".env").
        override: Whether to override existing os.environ values.

    Returns:
        Dictionary of interpolated key-value pairs (non-None values only).
    """
    raw_env = dotenv_values(dotenv_path)
    interpolated = {
        key: os.path.expandvars(value)
        for key, value in raw_env.items()
        if value is not None
    }

    for key, value in interpolated.items():
        if override or key not in os.environ:
            os.environ[key] = value

    return interpolated

def str_to_bool(value: str) -> bool:
    return value.lower() in ("1", "true", "yes", "on")
