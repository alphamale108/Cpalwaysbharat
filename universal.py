import re
import aiohttp
from typing import Optional, Dict
from extractors.base_extractor import BaseExtractor

class UniversalExtractor(BaseExtractor):
    PLATFORM = "universal"
    
    def is_valid_url(self, url: str) -> bool:
        return bool(re.match(r'https?://\S+', url))
    
    async def extract(self, url: str) -> Dict:
        """Universal extractor for direct video/PDF links"""
        content_type = await self._detect_content_type(url)
        
        if content_type == 'video':
            return await self._extract_video(url)
        elif content_type == 'document':
            return await self._extract_document(url)
        else:
            raise Exception("Unsupported content type")
    
    async def _detect_content_type(self, url: str) -> str:
        """Detect if URL points to video or document"""
        if url.lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx')):
            return 'document'
        
        # Check via HEAD request
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as resp:
                content_type = resp.headers.get('Content-Type', '').lower()
                
                if 'video' in content_type:
                    return 'video'
                elif 'application/pdf' in content_type:
                    return 'document'
                elif 'm3u8' in content_type or 'mpd' in content_type:
                    return 'video'
        
        # Fallback to URL pattern
        if re.search(r'\.(mp4|m3u8|mpd|mov|avi|mkv)$', url, re.I):
            return 'video'
        
        raise Exception("Could not determine content type")
    
    async def _extract_video(self, url: str) -> Dict:
        """Extract video information"""
        return {
            'title': url.split('/')[-1].split('?')[0],
            'type': 'video',
            'stream_url': url,
            'thumbnail': None,
            'duration': 0,
            'file_path': None  # Will be set during download
        }
    
    async def _extract_document(self, url: str) -> Dict:
        """Extract document information"""
        return {
            'title': url.split('/')[-1].split('?')[0],
            'type': 'document',
            'file_url': url,
            'file_path': None  # Will be set during download
        }
