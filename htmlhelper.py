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

def clean_filename_text(url):
    """Clean text from URLs to create safe filenames.
    
    Args:
        url: URL string to extract filename from
        
    Returns:
        Cleaned string with only alphabetic characters and spaces
    """
    # Extract the filename part from the URL
    filename = url.rsplit('/', 1)[-1]
    # Remove extension
    filename = filename.rsplit('.', 1)[0]
    # Remove non-alphabet characters, replace with space
    cleaned = re.sub(r'[^A-Za-z]+', ' ', filename)
    # Strip leading/trailing whitespace and normalize spaces
    return cleaned.strip()
