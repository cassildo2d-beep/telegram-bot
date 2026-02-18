import httpx
import asyncio

async def download_image(client, url):
    try:
        r = await client.get(url, timeout=30.0)
        r.raise_for_status()
        return r.content
    except:
        return None

async def download_images(urls):
    async with httpx.AsyncClient(http2=True) as client:
        tasks = [download_image(client, u) for u in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
