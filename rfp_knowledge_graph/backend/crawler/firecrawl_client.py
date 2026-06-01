from firecrawl import FirecrawlApp
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("firecrawl_client")
settings = get_settings()

_app = None


def _get_app() -> FirecrawlApp:
    global _app
    if _app is None:
        if not settings.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY not configured")
        _app = FirecrawlApp(api_key=settings.firecrawl_api_key)
    return _app


def crawl_url(url: str, max_pages: int = 20, include_patterns: list[str] | None = None) -> list[dict]:
    app = _get_app()
    logger.info(f"Starting crawl of {url} (max {max_pages} pages)")

    params: dict = {
        "limit": max_pages,
        "scrapeOptions": {"formats": ["markdown"]},
    }
    if include_patterns:
        params["includePaths"] = [f".*({'|'.join(include_patterns)}).*"]

    result = app.crawl_url(url, params=params, poll_interval=5)

    pages = []
    data = result.get("data", []) if isinstance(result, dict) else result
    for page in data:
        if isinstance(page, dict):
            pages.append({
                "url": page.get("metadata", {}).get("sourceURL", url),
                "markdown": page.get("markdown", ""),
                "title": page.get("metadata", {}).get("title", ""),
            })

    logger.info(f"Crawled {len(pages)} pages from {url}")
    return pages


def scrape_page(url: str) -> dict:
    app = _get_app()
    result = app.scrape_url(url, params={"formats": ["markdown"]})
    return {
        "url": url,
        "markdown": result.get("markdown", ""),
        "title": result.get("metadata", {}).get("title", ""),
    }
