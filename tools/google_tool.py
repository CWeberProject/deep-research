import asyncio
import urllib.parse
from playwright.async_api import async_playwright, TimeoutError
import random
import time
import logging
from agents import function_tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSearchError(Exception):
    """Exception raised when Google search fails."""
    pass

@function_tool(name_override="google")
async def google_search(query: str) -> str:
    """
    Perform a Google search using Playwright and return the top search result URLs.

    Args:
        query: The search query string.

    Returns:
        A string representation of the search result URLs, one URL per line.
    """
    # Set default values internally
    num_results = 10
    max_retries = 3
    
    # Encode the query for URL
    encoded_query = urllib.parse.quote_plus(query)
    
    # Track retry attempts
    attempts = 0
    
    while attempts < max_retries:
        try:
            attempts += 1
            logger.info(f"Search attempt {attempts}/{max_retries} for '{query}'")
            
            # Add delay between retries with exponential backoff
            if attempts > 1:
                wait_time = 2 ** attempts + random.uniform(1, 5)
                logger.info(f"Waiting {wait_time:.2f}s before retry...")
                await asyncio.sleep(wait_time)
            
            # Launch browser with more stealth options
            async with async_playwright() as p:
                # Use additional browser arguments to avoid detection
                browser_args = [
                    '--no-sandbox', 
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    f'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X {random.choice(["10_15_7", "11_2_3", "12_0_1"])} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 122)}.0.0.0 Safari/537.36'
                ]
                
                browser = await p.chromium.launch(
                    headless=True,
                    args=browser_args
                )
                
                # Create a context with additional settings
                context = await browser.new_context(
                    viewport={"width": random.randint(1024, 1920), "height": random.randint(768, 1080)},
                    device_scale_factor=random.choice([1, 2]),
                    locale=random.choice(['en-US', 'en-GB', 'en-CA']),
                    timezone_id='America/Los_Angeles',
                    permissions=['geolocation']
                )
                
                # Add script to modify navigator properties
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                """)
                
                page = await context.new_page()
                
                # Go to Google directly with query to avoid homepage detection
                url = f"https://www.google.com/search?q={encoded_query}&num={min(num_results + 5, 100)}"
                logger.info(f"Navigating to search URL...")
                
                # Navigate with a timeout
                await page.goto(url, wait_until='load', timeout=30000)
                await human_like_delay(500, 1500)
                
                # Check if we're on the CAPTCHA page
                if await is_captcha_page(page):
                    logger.warning("CAPTCHA challenge detected! Retrying with new browser instance...")
                    await browser.close()
                    continue
                
                # Wait for search results
                await page.wait_for_selector("div#search", timeout=10000)
                await human_like_delay(1000, 2000)
                
                # Target the main Google search result links specifically
                main_result_selectors = [
                    "a.zReHs[jsname='UWckNb']",  # Specific class based on your example
                    "div.g div.yuRUbf > a",      # Common structure for main results
                    "//a[contains(@class, 'zReHs') and @jsname='UWckNb']",  # XPath alternative
                    "div[jscontroller] > div > div > div > div > a[data-ved]",  # Structure-based
                    "h3.LC20lb + div + span > a", # Targeting links near headings
                    "h3.LC20lb"                   # Find headings and get their parent links
                ]
                
                links = []
                
                # Try each selector strategy to extract the main result links
                for selector in main_result_selectors:
                    try:
                        if selector.startswith("//"):  # Handle XPath selectors
                            elements = await page.locator(selector).all()
                            extracted_links = []
                            for el in elements:
                                href = await el.get_attribute("href")
                                if href and href.startswith("http") and "google.com/" not in href:
                                    extracted_links.append(href)
                        elif selector == "h3.LC20lb":  # Special handling for headings
                            extracted_links = await page.evaluate("""() => {
                                const headings = Array.from(document.querySelectorAll('h3.LC20lb'));
                                return headings
                                    .map(h => {
                                        const link = h.closest('a') || 
                                                    h.parentElement.closest('a') ||
                                                    h.parentElement.parentElement.querySelector('a');
                                        return link ? link.href : null;
                                    })
                                    .filter(href => href && href.startsWith('http') && !href.includes('google.com/'));
                            }""")
                        else:  # Regular CSS selectors
                            extracted_links = await page.eval_on_selector_all(
                                selector,
                                """(elements) => {
                                    return Array.from(elements)
                                        .map(a => a.href)
                                        .filter(href => 
                                            href && 
                                            href.startsWith('http') && 
                                            !href.includes('google.com/')
                                        );
                                }"""
                            )
                        
                        if extracted_links and len(extracted_links) > 0:
                            logger.info(f"Found {len(extracted_links)} main result links using selector: {selector}")
                            links.extend(extracted_links)
                            if len(links) >= num_results:
                                break
                    except Exception as e:
                        logger.info(f"Selector {selector} failed: {str(e)}")
                        continue
                
                # If standard selectors fail, try a more targeted approach with the exact structure
                if not links:
                    logger.info("Attempting to extract main results using the exact structure")
                    try:
                        links = await page.evaluate("""() => {
                            const mainLinks = Array.from(document.querySelectorAll('a[jsname="UWckNb"][class="zReHs"]'));
                            if (mainLinks.length === 0) {
                                const headings = Array.from(document.querySelectorAll('h3.LC20lb'));
                                return headings
                                    .map(h => {
                                        const link = h.closest('a') || h.parentElement.closest('a');
                                        return link ? link.href : null;
                                    })
                                    .filter(href => href && href.startsWith('http') && !href.includes('google.com/'));
                            }
                            return mainLinks
                                .map(a => a.href)
                                .filter(href => href && href.startsWith('http') && !href.includes('google.com/'));
                        }""")
                    except Exception as e:
                        logger.error(f"Error extracting main links with exact structure: {str(e)}")
                
                await browser.close()
                
                # Remove duplicates while preserving order
                unique_links = []
                seen = set()
                for link in links:
                    if link not in seen:
                        seen.add(link)
                        unique_links.append(link)
                
                if unique_links and len(unique_links) > 0:
                    # Convert list of links to a string with one URL per line
                    result_links = unique_links[:num_results]
                    return '\n'.join(result_links)
                else:
                    logger.warning("No main result links found in search results")
                    continue
                
        except Exception as e:
            logger.error(f"Search attempt {attempts} failed: {str(e)}")
            if attempts >= max_retries:
                raise GoogleSearchError(f"Failed to perform Google search after {max_retries} attempts: {str(e)}")

    raise GoogleSearchError(f"Failed to perform Google search after {max_retries} attempts")

def human_like_delay(min_ms=200, max_ms=800):
    """Add a random delay to simulate human interaction"""
    delay = random.randint(min_ms, max_ms) / 1000.0
    asyncio.sleep(delay)

def is_captcha_page(page):
    """Check if the current page is a Google CAPTCHA challenge"""
    try:
        current_url = page.url
        if "sorry" in current_url or "captcha" in current_url:
            return True
        
        captcha_indicators = [
            "body:has-text('unusual traffic')",
            "body:has-text('please try again')",
            "body:has-text('verify you are a human')",
            "form#captcha-form",
            "img[src*='captcha']",
            "div#recaptcha"
        ]
        
        for indicator in captcha_indicators:
            if page.locator(indicator).count() > 0:
                return True
                
        return False
    except Exception:
        return False

# Add a __main__ section for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a Google search from the command line")
    parser.add_argument("query", help="The search query to run")
    args = parser.parse_args()
    
    async def run_search():
        try:
            results = await google_search(args.query)
            print("\nSearch Results:")
            print("---------------")
            print(results)
            print("\nTotal results found:", len(results.split('\n')))
        except GoogleSearchError as e:
            print(f"Error: {e}")
    
    # Run the async function
    asyncio.run(run_search())
