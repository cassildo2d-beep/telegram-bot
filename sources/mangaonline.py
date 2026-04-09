import httpx
from bs4 import BeautifulSoup
from datetime import datetime


class MangaOnlineSource:
    name = "Manga Online"
    base_url = "https://mangaonline.red"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": base_url + "/",
    }

    timeout = httpx.Timeout(60.0)

    # ================= SEARCH =================
    async def search(self, query: str):
        if not query:
            return []

        params = {"s": query}

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            r = await client.get(self.base_url, params=params)

            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, "html.parser")

        results = []
        for manga in soup.select(".post-title a"):
            results.append({
                "title": manga.text.strip(),
                "url": manga["href"]
            })

        return results

    # ================= CHAPTERS =================
    async def chapters(self, manga_url: str):
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            r = await client.get(manga_url)

            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, "html.parser")

        chapters = []

        for ch in soup.select(".wp-manga-chapter"):
            link = ch.select_one("a")
            date = ch.select_one(".chapter-release-date")

            if link:
                chapters.append({
                    "name": link.text.strip(),
                    "url": link["href"],
                    "chapter_number": self._extract_number(link.text),
                    "date": self._parse_date(date.text.strip()) if date else None
                })

        # ordenar igual Tachiyomi (desc)
        chapters.sort(key=lambda x: float(x.get("chapter_number") or 0), reverse=True)

        return chapters

    # ================= PAGES =================
    async def pages(self, chapter_url: str):
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            r = await client.get(chapter_url)

            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, "html.parser")

        images = []

        for img in soup.select(".reading-content img"):
            src = img.get("src")
            if src:
                images.append(src)

        return images

    # ================= HELPERS =================
    def _extract_number(self, text):
        import re
        match = re.search(r"\d+(\.\d+)?", text)
        return match.group() if match else "0"

    def _parse_date(self, text):
        try:
            return datetime.strptime(text, "%d de %B de %Y")
        except Exception:
            return None
