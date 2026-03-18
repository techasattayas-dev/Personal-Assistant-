"""
Tool: scrape_web — Scrape web content with Apify, fallback to BeautifulSoup.

Uses Apify cheerio-scraper actor for robust scraping (handles JS-rendered content),
automatically falls back to requests + BeautifulSoup when Apify quota is exhausted
or token is unavailable.

Requires APIFY_TOKEN in .env for Apify (optional; BeautifulSoup works without it).
"""

import os
import requests
from pathlib import Path

from bs4 import BeautifulSoup


MAX_CONTENT_DEFAULT = 50000


def scrape_web(
    url: str,
    content_selector: str | None = None,
    max_content_length: int = MAX_CONTENT_DEFAULT,
) -> str:
    """Scrape web content from a URL.

    Tries Apify first (if APIFY_TOKEN is set), falls back to BeautifulSoup.

    Args:
        url: The URL to scrape (must start with http:// or https://).
        content_selector: Optional CSS selector to extract specific content.
        max_content_length: Max characters to return (default 50000).

    Returns:
        Scraped text content or error message.
    """
    if not url or not url.strip():
        return "ERROR: URL is required."

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return "ERROR: Invalid URL. Must start with http:// or https://"

    # Try Apify first
    apify_token = os.getenv("APIFY_TOKEN")
    if apify_token:
        result = _scrape_with_apify(url, content_selector, apify_token, max_content_length)
        if not result.startswith("APIFY_FALLBACK:"):
            return result
        # If we got a fallback signal, continue to BeautifulSoup
        fallback_reason = result.replace("APIFY_FALLBACK:", "").strip()
    else:
        fallback_reason = "No APIFY_TOKEN configured"

    # Fallback to BeautifulSoup
    result = _scrape_with_beautifulsoup(url, content_selector, max_content_length)

    # Prepend fallback notice if Apify was attempted but failed
    if apify_token and not result.startswith("ERROR"):
        result = f"[Scraped via BeautifulSoup — Apify fallback: {fallback_reason}]\n\n{result}"

    return result


def _scrape_with_apify(
    url: str,
    content_selector: str | None,
    api_token: str,
    max_length: int,
) -> str:
    """Scrape using Apify cheerio-scraper actor."""
    try:
        from apify_client import ApifyClient
    except ImportError:
        return "APIFY_FALLBACK: apify-client not installed"

    try:
        client = ApifyClient(api_token)

        # Use cheerio-scraper (fast, server-side, no browser)
        actor_input = {
            "startUrls": [{"url": url}],
            "maxCrawlPages": 1,
            "crawlerType": "cheerio",
        }

        if content_selector:
            actor_input["keepUrlFragments"] = False

        # Run actor synchronously (blocks until done, max ~60s for cheerio)
        run = client.actor("apify/website-content-crawler").call(
            run_input=actor_input,
            timeout_secs=120,
        )

        if not run:
            return "APIFY_FALLBACK: Actor run returned no result"

        # Get results from dataset
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            return "APIFY_FALLBACK: No dataset ID in run result"

        results = []
        for item in client.dataset(dataset_id).iterate_items():
            # website-content-crawler returns text in 'text' field
            text = item.get("text", "")
            if text:
                results.append(text)
            elif item.get("markdown"):
                results.append(item["markdown"])

        if not results:
            return "APIFY_FALLBACK: Apify returned no content"

        content = "\n\n".join(results)

        # Apply CSS selector filtering if content is HTML and selector provided
        if content_selector and "<" in content:
            soup = BeautifulSoup(content, "html.parser")
            element = soup.select_one(content_selector)
            if element:
                content = element.get_text(separator="\n", strip=True)

        # Truncate
        if len(content) > max_length:
            content = content[:max_length] + "\n\n[... content truncated at {max_length} chars ...]"

        return f"[Scraped via Apify]\n\n{content}"

    except Exception as e:
        err_msg = str(e)
        # Redact API token from error messages
        if api_token and api_token in err_msg:
            err_msg = err_msg.replace(api_token, "[REDACTED]")

        # Detect quota exhaustion
        if any(code in err_msg.lower() for code in ["402", "429", "quota", "limit", "exceeded"]):
            return f"APIFY_FALLBACK: Quota exhausted — {type(e).__name__}"

        return f"APIFY_FALLBACK: {type(e).__name__}: {err_msg[:200]}"


def _scrape_with_beautifulsoup(
    url: str,
    content_selector: str | None,
    max_length: int,
) -> str:
    """Fallback scraping using requests + BeautifulSoup."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract based on CSS selector if provided
        if content_selector:
            element = soup.select_one(content_selector)
            if not element:
                return f"ERROR: CSS selector '{content_selector}' not found on page."
            target = element
        else:
            # Try common content containers in order
            target = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", {"role": "main"})
                or soup.find("div", {"id": "content"})
                or soup.find("div", {"class": "content"})
                or soup.body
            )

        if not target:
            return "ERROR: Could not find content on page."

        # Remove noise elements
        for tag in target.find_all(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        # Extract clean text
        content = target.get_text(separator="\n", strip=True)

        # Clean up excessive whitespace
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        content = "\n".join(lines)

        if not content:
            return "ERROR: Page returned empty content after extraction."

        # Truncate
        if len(content) > max_length:
            content = content[:max_length] + f"\n\n[... content truncated at {max_length} chars ...]"

        return content

    except requests.Timeout:
        return f"ERROR: Request timed out after 15 seconds for {url}"
    except requests.HTTPError as e:
        return f"ERROR: HTTP {e.response.status_code} for {url}"
    except requests.RequestException as e:
        return f"ERROR: Failed to fetch URL: {type(e).__name__}"
    except Exception as e:
        return f"ERROR: Scraping failed: {type(e).__name__}: {str(e)[:200]}"
