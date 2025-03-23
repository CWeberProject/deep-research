import re

def clean_markdown(markdown_text: str) -> str:
    """
    Clean and format markdown text.
    
    Args:
        markdown_text: The markdown text to clean
        
    Returns:
        Cleaned markdown text
    """
    # Remove consecutive empty lines
    markdown_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown_text)
    
    # Remove HTML comments
    markdown_text = re.sub(r'<!--.*?-->', '', markdown_text, flags=re.DOTALL)
    
    # Fix bullet points that might have gotten mangled
    markdown_text = re.sub(r'(\n\s*)-\s*', r'\1- ', markdown_text)
    
    # Fix header formatting
    markdown_text = re.sub(r'(\n\s*)#([^#\s])', r'\1# \2', markdown_text)
    
    # Remove non-ASCII characters that might cause issues
    markdown_text = re.sub(r'[^\x00-\x7F]+', ' ', markdown_text)
    
    # Fix common Markdown formatting issues
    markdown_text = re.sub(r'\*\*\s+', '** ', markdown_text)
    markdown_text = re.sub(r'\s+\*\*', ' **', markdown_text)
    
    return markdown_text.strip()

def truncate_markdown(markdown_text: str, max_length: int = 8000) -> str:
    """
    Truncate markdown text to a maximum length while preserving formatting.
    
    Args:
        markdown_text: The markdown text to truncate
        max_length: Maximum length in characters
        
    Returns:
        Truncated markdown text
    """
    if len(markdown_text) <= max_length:
        return markdown_text
    
    # Truncate to max_length
    truncated = markdown_text[:max_length]
    
    # Try to end at a paragraph
    last_paragraph = truncated.rfind('\n\n')
    if last_paragraph > 0 and last_paragraph > max_length * 0.8:
        truncated = truncated[:last_paragraph]
    
    # Add indication of truncation
    truncated += "\n\n...(content truncated)..."
    
    return truncated
