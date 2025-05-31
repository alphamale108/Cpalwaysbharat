import os
import re
import aiohttp
import yt_dlp
from typing import List

async def process_text_file(file_path: str) -> List[str]:
    """Extract valid URLs from text file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all HTTP/HTTPS URLs
    urls = re.findall(r'https?://\S+', content)
    
    # Clean up URLs (remove trailing punctuation)
    cleaned_urls = []
    for url in urls:
        url = re.sub(r'[.,;!?)]+$', '', url)
        if url not in cleaned_urls:  # Avoid duplicates
            cleaned_urls.append(url)
    
    # Clean up the downloaded file
    os.remove(file_path)
    
    return cleaned_urls

async def download_file(url: str, file_type: str) -> str:
    """Download file from URL with appropriate method"""
    if file_type == 'video':
        return await download_video(url)
    else:
        return await download_direct(url)

async def download_video(url: str) -> str:
    """Download video using yt-dlp"""
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_%(id)s.%(ext)s',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def download_direct(url: str) -> str:
    """Download file directly"""
    file_name = url.split('/')[-1].split('?')[0]
    file_path = f"downloaded_{file_name}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download file (HTTP {response.status})")
            
            with open(file_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
    
    return file_path

def clean_temp_files():
    """Clean up temporary downloaded files"""
    for file in os.listdir('.'):
        if file.startswith('downloaded_') or file.startswith('temp_'):
            try:
                os.remove(file)
            except:
                pass
