import re
from typing import Union, List

def strip_code_guard(content: str, guard_types: Union[str, List[str]] = None) -> str:
    """Strip specified markdown code guards from content.
    
    Args:
        content: String containing markdown content with possible code guards
        guard_types: Either a string or list of strings specifying which code guards to remove.
                    If None, removes all common code guards (markdown, json).
                    Example values: "markdown", ["markdown", "json"]
        
    Returns:
        String with specified markdown code guards removed
    """
    if guard_types is None:
        guard_types = ["markdown", "json"]
    elif isinstance(guard_types, str):
        guard_types = [guard_types]
    
    # Create regex pattern for specified guard types
    guard_pattern = "|".join(re.escape(g) for g in guard_types)
    content = re.sub(r'^\s*```(' + guard_pattern + r')\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*```\s*$', '', content, flags=re.MULTILINE)
    return content.strip()
