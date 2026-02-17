from sources.toonbr import ToonBrSource
from sources.mangaonline import MangaOnlineSource

SOURCES = {
    "toonbr": ToonBrSource(),
    "mangaonline": MangaOnlineSource(),
}

def get_source(name):
    return SOURCES.get(name)
