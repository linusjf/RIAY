import re
import os
from dotenv import dotenv_values


def parse_bash_array(file_path, var_name):
    """Parse a bash array from a file and return its values as a Python list.

    Args:
        file_path: Path to the bash file
        var_name: Name of the array variable to parse

    Returns:
        list: The array values or empty list if not found
    """
    with open(file_path, 'r') as f:
        content = f.read()

    # Match array definition like: VAR=( "a" "b" "c" )
    pattern = re.compile(rf'{var_name}\s*=\s*\((.*?)\)', re.DOTALL)
    match = pattern.search(content)
    if not match:
        return []

    array_body = match.group(1)
    # Extract all quoted strings
    values = re.findall(r'"(.*?)"', array_body)
    return values

def load_dotenv_with_system_interpolation(dotenv_path=".env", override=False):
    """
    Load a dotenv file, expanding references to existing environment variables.

    Args:
        dotenv_path (str): Path to the .env file (default: ".env").
        override (bool): Whether to override existing os.environ values.

    Returns:
        dict: The interpolated key-value pairs (with non-None values only).
    """
    raw_env = dotenv_values(dotenv_path)

    interpolated = {
        k: os.path.expandvars(v) for k, v in raw_env.items() if v is not None
    }

    for k, v in interpolated.items():
        if override or k not in os.environ:
            os.environ[k] = v  # ✅ v is guaranteed to be a str

    return interpolated
