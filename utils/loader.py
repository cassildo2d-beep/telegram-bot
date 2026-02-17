from sources.toonbr import ToonBrSource
from sources.mangaonline import MangaOnlineSource

SOURCES = {
    "ToonBr": ToonBrSource(),
    "MangaOnline": MangaOnlineSource(),
    "MangaFlix": MangaFlix(),
}

def get_all_sources():
    return SOURCES
