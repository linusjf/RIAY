import re

def strip_code_guards(content: str) -> str:
    """Strip markdown code guards from content.
    
    Args:
        content: String containing markdown content with possible code guards
        
    Returns:
        String with markdown code guards removed
    """
    # Remove ```markdown and ```json guards
    content = re.sub(r'^\s*```(markdown|json)\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*```\s*$', '', content, flags=re.MULTILINE)
    return content.strip()
