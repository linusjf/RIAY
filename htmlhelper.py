import re

def strip_span_tags_but_keep_contents(text):
    """Remove HTML span tags while preserving their contents.
    
    Args:
        text: String containing HTML with span tags
        
    Returns:
        String with span tags removed but contents preserved
    """
    # Remove opening <span ...> tag
    text = re.sub(r'<span[^>]*?>', '', text)
    # Remove closing </span> tag
    text = re.sub(r'</span>', '', text)
    return text
