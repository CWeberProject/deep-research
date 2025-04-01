from agents import function_tool
import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import Dict, Any

@function_tool
def web_research(query: str, num_results: int) -> Dict[str, Any]:
    """
    Performs web research by searching the internet and retrieving results.

    Args:
        query: Search query to look up.
        num_results: Number of results to return (between 1 and 10).

    Returns:
        Dictionary containing search results with titles, URLs, and snippets.
    """
    try:
        # Handle default value for num_results within the function
        if num_results is None:
            num_results = 5
        num_results = max(1, min(10, num_results))

        # Prepare headers to simulate a browser.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Perform search on DuckDuckGo.
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse results page with BeautifulSoup.
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = soup.select(".result")

        results = []
        # Process requested number of results.
        for result in search_results[:num_results]:
            try:
                # Extract title, URL, and snippet.
                title_element = result.select_one(".result__title")
                title = title_element.get_text(strip=True) if title_element else "No title found"

                link_element = result.select_one(".result__url")
                link = link_element.get_text(strip=True) if link_element else None

                # If link is not complete, prefix it.
                if link and not link.startswith(("http://", "https://")):
                    link = "https://" + link

                snippet_element = result.select_one(".result__snippet")
                snippet = snippet_element.get_text(strip=True) if snippet_element else ""

                if link:
                    result_item = {
                        "title": title,
                        "url": link,
                        "snippet": snippet
                    }
                    results.append(result_item)
            except Exception as e:
                continue  # Skip problematic result and continue.

        return {
            "results": results,
            "query": query,
            "num_results": len(results)
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Example usage
    query = "Python programming"
    num_results = 5
    results = web_research(query, num_results)
    #print(results)
    urls = [result["url"] for result in results["results"]]
    print("URLs:", urls)