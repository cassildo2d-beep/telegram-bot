import httpx

API_URL = "https://api.toonbr.com/api"
CDN_URL = "https://cdn2.toonbr.com"

class ToonBrSource:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)

    async def search(self, query):
        try:
            r = await self.client.get(
                f"{API_URL}/manga",
                params={"search": query}
            )
            data = r.json()
            mangas = []
            for m in data.get("data", []):
                mangas.append({
                    "title": m.get("title"),
                    "slug": m.get("slug")
                })
            return mangas
        except Exception:
            return []

    async def chapters(self, manga_url):
        try:
            slug = manga_url.rstrip("/").split("/")[-1]
            r = await self.client.get(f"{API_URL}/manga/{slug}")
            data = r.json()
            chapters = []
            for ch in data.get("chapters", []):
                chapters.append({
                    "chapter_number": ch.get("chapter_number"),
                    "id": ch.get("id"),
                    "url": str(ch.get("id")),  # usamos o id como URL interno
                    "manga_title": data.get("title")
                })
            return chapters
        except Exception:
            return []

    async def pages(self, chapter_id):
        try:
            r = await self.client.get(f"{API_URL}/chapter/{chapter_id}")
            data = r.json()
            imgs = []
            for p in data.get("pages", []):
                if p.get("imageUrl"):
                    imgs.append(CDN_URL + p["imageUrl"])
            return imgs
        except Exception:
            return []
