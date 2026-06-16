import asyncio
import httpx

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

    # Setting a baseline timeout of 10 seconds for connect/read/write operations
    return httpx.AsyncClient(headers=headers, timeout=10)

async def scrape_page(url, client, parse_function):
    """
    Fetches one property page asynchronously and parses it using parse_function.
    """

    try:
        await asyncio.sleep(1) # Polite delay: let other requests run concurrently while this one pauses
        response = await client.get(url) # "await" here means "send the request, and while waiting for the response, let other tasks run".
        response.raise_for_status()
        
        # Parse and return data
        data = parse_function(response.text)
        data["url"] = url
        return data
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None


async def scrape_all(urls, parse_function, max_concurrent = 5):
    """
    Scrapes all URLs concurrently while strictly limiting the max active connections (5 by default).
    """

    semaphore = asyncio.Semaphore(max_concurrent) # Counter that limits concurrency.

    async def worker(url):
        async with semaphore: # Limits how many workers hit the web at once
            return await scrape_page(url, client, parse_function)

    async with make_client() as client:
        tasks = [worker(url) for url in urls]
        results = await asyncio.gather(*tasks)

    # Filter out any None values from failed pages
    return [r for r in results if r is not None]

def save_to_csv(df, path):
    df.to_csv(path, index=False)