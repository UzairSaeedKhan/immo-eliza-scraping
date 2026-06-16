import asyncio
import httpx
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("scraping.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def make_client():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
    }
    logger.debug("Creating HTTP client with custom headers and 10s timeout")
    return httpx.AsyncClient(headers=headers, timeout=10)


async def scrape_page(url, client, parse_function):
    """
    Fetches one property page asynchronously and parses it using parse_function.
    """
    logger.info(f"Scraping: {url}")
    try:
        await asyncio.sleep(1)
        response = await client.get(url)
        response.raise_for_status()
        logger.info(f"OK [{response.status_code}]: {url}")

        data = parse_function(response.text)
        # data["url"] = url Not needed probably
        logger.debug(f"Parsed {len(data)} fields from {url}")
        return data

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code} error for {url}: {e}")
    except httpx.TimeoutException:
        logger.warning(f"Timed out: {url}")
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
    return None


async def scrape_all(urls, parse_function, max_concurrent=10):
    """
    Scrapes all URLs concurrently while strictly limiting the max active connections.
    """
    total = len(urls)
    logger.info(f"Starting scrape: {total} URLs, max {max_concurrent} concurrent")

    semaphore = asyncio.Semaphore(max_concurrent)
    completed = 0

    async def worker(url):
        nonlocal completed
        async with semaphore:
            result = await scrape_page(url, client, parse_function)
            completed += 1
            logger.info(f"Progress: {completed}/{total}")
            return result

    async with make_client() as client:
        tasks = [worker(url) for url in urls]
        results = await asyncio.gather(*tasks)

    successful = [r for r in results if r is not None]
    failed = total - len(successful)
    logger.info(f"Done: {len(successful)} succeeded, {failed} failed out of {total}")
    return successful