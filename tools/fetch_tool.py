import asyncio
import sys
import os
import re
import dotenv
from playwright.async_api import async_playwright
from markdownify import markdownify as md
from agents import function_tool
from google import genai
from google.genai import types

# Load environment variables from .env file
dotenv.load_dotenv()


client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Add parent directory to path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.markdown_helpers import clean_markdown

class ContentRetrieverError(Exception):
    """Exception raised when content retrieval fails."""
    pass

system_prompt = """
You are a webpage content extractor. You are given the full Markdown content of a webpage, 
including a lot of unnecessary stuff: backlinks, cookies, policy section, etc.

You need to extract only the useful content of the webpage if there is some. By useful 
content, I mean content related to the user query. 

Keep the relevant information, and intact figures, names, titles, etc. You should not 
include any of the unnecessary stuff: keep only what is relevant to the user's query, 
and the context around it.

Make sure to keep figures, numbers, names, and facts intact, as they are important for 
the user.

If there is no relevant information regarding the user query in the webpage, just say 
"No relevant information found in the webpage regarding the user query".

Your output should only contain information based on the content of the webpage.
Do not include any other information or context. Do not hallucinate.
"""

@function_tool
async def fetch_tool(url: str, query: str) -> str:
    """Retrieve relevant content from URL.
    
    Args:
        url (str): The URL to retrieve content from, example: "https://example.com"
        query (str): The query Google query this URL is related to, example: "What is the latest news about AI?"
        
    Returns:
        str: The webpage's content with only the relevant information, and intact figures, names, titles, etc.
    """
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            response = await page.goto(url, wait_until="domcontentloaded", timeout=5000)
            if not response.ok:
                raise ContentRetrieverError(f"HTTP status {response.status}")
            
            html_content = await page.content()
            await browser.close()
            
            # Convert to Markdown using markitdown
            markdown_content = md(html_content)
            
            # Clean markdown
            markdown_content = clean_markdown(markdown_content)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt),
                contents=(f"Here is the user query: {query}\n\Below is the content of the webpage:\n\n {markdown_content}"),
            )

            return {"Google Search Query": query, "URL of webpage": url, "Relevant Content Retrieved": response.text}
                
    except Exception as e:
        raise ContentRetrieverError(f"Failed to retrieve content: {str(e)}")
