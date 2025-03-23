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

@function_tool
async def google_search(query: str, num_results: int = 10, max_retries: int = 3) -> list:
    """
    Perform a Google search using Playwright and return the top search result URLs.

    Args:
        query: The search query string.
        num_results: Number of results to return (default: 10).
        max_retries: Maximum number of retry attempts (default: 3).

    Returns:
        A list of URLs from the search results.
    """
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
                
                # Wait for search results with multiple selector options
                result_selectors = ["div#search", "div#rso", "div.g"]
                
                for selector in result_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        logger.info(f"Found results with selector: {selector}")
                        break
                    except TimeoutError:
                        logger.info(f"Selector {selector} not found, trying next...")
                        continue
                else:
                    # If we get here, none of the selectors worked
                    logger.warning("Could not find any search results with known selectors")
                    screenshot_path = f"failed_search_{int(time.time())}.png"
                    await page.screenshot(path=screenshot_path)
                    logger.info(f"Saved screenshot to {screenshot_path}")
                    await browser.close()
                    continue
                
                await human_like_delay(1000, 2000)
                
                # Try multiple selector strategies to get links
                links = []
                
                # List of selector strategies to try
                selector_strategies = [
                    "div.g div.yuRUbf > a, div.IsZvec > div > span > a",
                    "div.g a[href^='http']:not([href*='google.com'])",
                    "div#search a[href^='http']:not([href*='google.com'])",
                    "div#rso a[href^='http']:not([href*='google.com'])",
                    "div.g h3:has(+ a[href])",
                    "a[ping]"
                ]
                
                for selector in selector_strategies:
                    try:
                        links = await page.eval_on_selector_all(
                            selector,
                            """(elements) => {
                                return Array.from(elements)
                                    .map(a => a.href || (a.closest('a') ? a.closest('a').href : null))
                                    .filter(href => 
                                        href && 
                                        href.startsWith('http') && 
                                        !href.includes('google.com/')
                                    );
                            }"""
                        )
                        
                        if links and len(links) > 0:
                            logger.info(f"Found {len(links)} links using selector: {selector}")
                            break
                    except Exception as e:
                        logger.info(f"Selector {selector} failed: {str(e)}")
                        continue
                
                # If we still couldn't find links, try one more approach - extract from the page content
                if not links:
                    logger.info("Using JavaScript to extract all links from page")
                    links = await page.evaluate("""() => {
                        const allLinks = Array.from(document.querySelectorAll('a[href]'));
                        return allLinks
                            .map(a => a.href)
                            .filter(href => 
                                href && 
                                href.startsWith('http') && 
                                !href.includes('google.com/')
                            );
                    }""")
                
                await browser.close()
                
                if links and len(links) > 0:
                    # Return only the requested number of results
                    return links[:num_results]
                else:
                    logger.warning("No links found in search results")
                    continue
                
        except Exception as e:
            logger.error(f"Search attempt {attempts} failed: {str(e)}")
            if attempts >= max_retries:
                raise GoogleSearchError(f"Failed to perform Google search after {max_retries} attempts: {str(e)}")

    # If we get here, all retries failed
    raise GoogleSearchError(f"Failed to perform Google search after {max_retries} attempts")

async def human_like_delay(min_ms=200, max_ms=800):
    """Add a random delay to simulate human interaction"""
    delay = random.randint(min_ms, max_ms) / 1000.0
    await asyncio.sleep(delay)

async def is_captcha_page(page):
    """Check if the current page is a Google CAPTCHA challenge"""
    try:
        # Check URL first
        current_url = page.url
        if "sorry" in current_url or "captcha" in current_url:
            return True
        
        # Check for common CAPTCHA elements
        captcha_indicators = [
            "body:has-text('unusual traffic')",
            "body:has-text('please try again')",
            "body:has-text('verify you are a human')",
            "form#captcha-form",
            "img[src*='captcha']",
            "div#recaptcha"
        ]
        
        for indicator in captcha_indicators:
            if await page.locator(indicator).count() > 0:
                return True
                
        return False
    except Exception:
        # If any error occurs during check, assume it might be a CAPTCHA to be safe
        return False
