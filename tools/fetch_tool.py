import asyncio
import sys
import os
import re
from playwright.async_api import async_playwright
from markdownify import markdownify as md
from agents import function_tool

# Add parent directory to path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.markdown_helpers import clean_markdown

class ContentRetrieverError(Exception):
    """Exception raised when content retrieval fails."""
    pass

@function_tool
async def content_retriever(url: str, max_retries: int = 3) -> str:
    """Retrieve content from URL and convert to Markdown.
    
    Args:
        url (str): The URL to retrieve content from.
        max_retries (int): The maximum number of retry attempts.
        
    Returns:
        str: The retrieved content in Markdown format.
    """
    for attempt in range(max_retries):
        try:
            # Add delay between retries
            if attempt > 0:
                await asyncio.sleep(2 ** attempt)
                
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                response = await page.goto(url, wait_until='networkidle', timeout=30000)
                if not response.ok:
                    raise ContentRetrieverError(f"HTTP status {response.status}")
                
                html_content = await page.content()
                await browser.close()
                
                # Convert to Markdown using markitdown
                markdown_content = md(html_content)
                
                # Clean markdown
                markdown_content = remove_boilerplate_text(markdown_content)
                markdown_content = clean_markdown(markdown_content)
                
                return markdown_content
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise ContentRetrieverError(f"Failed after {max_retries} attempts: {str(e)}")
    
    raise ContentRetrieverError(f"Failed after {max_retries} attempts")

def remove_boilerplate_text(markdown_content: str) -> str:
    """Remove common website boilerplate text."""
    patterns = [
        r'Cookie Policy.*?Privacy Policy',
        r'Terms of Service.*?Privacy Policy',
        r'©.*?All rights reserved',
        r'Copyright ©.*?\d{4}'
    ]
    
    for pattern in patterns:
        markdown_content = re.sub(pattern, '', markdown_content, flags=re.DOTALL)
    
    return markdown_content.strip()