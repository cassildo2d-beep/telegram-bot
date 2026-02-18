import httpx
import asyncio

async def fetch_image(client, url):
    try:
        r = await client.get(url, timeout=30.0)
        r.raise_for_status()
        return r.content
    except Exception:
        return None

async def download_images(urls):
    """
    Recebe lista de URLs, retorna lista de bytes de cada imagem
    """
    results = []
    async with httpx.AsyncClient(http2=True, timeout=30.0) as client:
        tasks = [fetch_image(client, url) for url in urls]
        fetched = await asyncio.gather(*tasks)
        results = [img for img in fetched if img]
    return results
