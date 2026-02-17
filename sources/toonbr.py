# sources/toonbr.py
import asyncio
from utils.http import GET
from utils.parser import parse_json
from utils.cbz import create_cbz

class ToonBrSource:
    name = "ToonBr"
    apiUrl = "https://api.toonbr.com"
    cdnUrl = "https://cdn2.toonbr.com"

    async def search(self, query: str):
        url = f"{self.apiUrl}/api/manga?search={query}"
        resp = await GET(url)
        data = parse_json(resp)
        results = []
        for m in data.get("data", []):
            results.append({
                "title": m.get("name"),
                "url": m.get("_id"),
            })
        return results

    async def chapters(self, manga_id: str):
        url = f"{self.apiUrl}/api/manga/{manga_id}"
        resp = await GET(url)
        data = parse_json(resp)
        chapters = []
        for ch in data.get("chapters", []):
            chapters.append({
                "name": f"Cap {ch.get('number')}",
                "url": ch.get("_id"),  # ID real do capítulo
                "chapter_number": ch.get("number"),
                "manga_title": data.get("name"),
            })
        return chapters

    async def pages(self, chapter_id: str):
        url = f"{self.apiUrl}/api/chapter/{chapter_id}"
        resp = await GET(url)
        data = parse_json(resp)
        pages = []
        for idx, p in enumerate(data.get("pages", [])):
            pages.append(f"{self.cdnUrl}{p.get('imageUrl')}")
        return pages
