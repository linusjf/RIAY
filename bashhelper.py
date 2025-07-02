import re

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
