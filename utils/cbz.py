import os
import zipfile
import aiohttp
import asyncio
import tempfile
import re
from pathlib import Path

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

async def download_image(session, url, path, progress_callback=None, index=0, total=1):
    async with session.get(url) as resp:
        if resp.status == 200:
            data = await resp.read()
            with open(path, "wb") as f:
                f.write(data)
            if progress_callback:
                await progress_callback(index + 1, total)

async def create_cbz(images, manga_title, chapter_name, progress_callback=None):
    safe_title = sanitize_filename(manga_title)
    safe_chap = sanitize_filename(chapter_name)

    cache_dir = Path("./cbz_cache")
    cache_dir.mkdir(exist_ok=True)
    cbz_name = f"{safe_title} - {safe_chap}.cbz"
    cbz_path = cache_dir / cbz_name

    # Retorna do cache se existir
    if cbz_path.exists():
        return str(cbz_path), cbz_name

    temp_dir = tempfile.mkdtemp()
    async with aiohttp.ClientSession() as session:
        tasks = []
        total = len(images)
        for idx, img_url in enumerate(images):
            ext = os.path.splitext(img_url)[1].split("?")[0] or ".jpg"
            img_path = os.path.join(temp_dir, f"{idx:03d}{ext}")
            tasks.append(download_image(session, img_url, img_path, progress_callback, idx, total))
        await asyncio.gather(*tasks)

    with zipfile.ZipFile(cbz_path, "w", compression=zipfile.ZIP_DEFLATED) as cbz:
        for file in sorted(os.listdir(temp_dir)):
            if file.endswith(".jpg") or file.endswith(".png"):
                cbz.write(os.path.join(temp_dir, file), arcname=file)

    # limpa pasta temporária
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)

    return str(cbz_path), cbz_name
