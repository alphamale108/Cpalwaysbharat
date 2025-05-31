import re
import aiohttp
from typing import Dict, List
from extractors.base_extractor import BaseExtractor

class ClassPlusExtractor(BaseExtractor):
    PLATFORM = "classplus"
    
    def is_valid_url(self, url: str) -> bool:
        return bool(re.match(r'https?://(www\.)?classplus\.app/.+', url))
    
    async def extract(self, url: str) -> Dict:
        """Extract content from ClassPlus without login"""
        # ClassPlus uses a different approach - we need to find the embedded iframe first
        async with aiohttp.ClientSession() as session:
            # Step 1: Get the page content to find iframe
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch ClassPlus page: HTTP {response.status}")
                
                html = await response.text()
                
                # Step 2: Extract iframe src
                iframe_src = self._extract_iframe_src(html)
                if not iframe_src:
                    raise Exception("Could not find content iframe in ClassPlus page")
                
                # Step 3: Get content from iframe
                return await self._get_iframe_content(session, iframe_src)
    
    def _extract_iframe_src(self, html: str) -> Optional[str]:
        """Extract iframe src from HTML"""
        match = re.search(r'<iframe[^>]+src="([^"]+)"', html)
        return match.group(1) if match else None
    
    async def _get_iframe_content(self, session: aiohttp.ClientSession, iframe_url: str) -> Dict:
        """Get content from iframe URL"""
        async with session.get(iframe_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch iframe content: HTTP {response.status}")
            
            # Parse the iframe content - this will vary based on ClassPlus implementation
            # Here we simulate finding the actual content URL
            content_url = self._find_content_url(await response.text())
            if not content_url:
                raise Exception("Could not find content URL in iframe")
            
            return {
                'title': "ClassPlus Content",
                'type': 'video' if 'video' in content_url else 'document',
                'platform': self.PLATFORM,
                'download_url': content_url,
                'qualities': [{
                    'resolution': 'Original',
                    'url': content_url,
                    'size': 'Unknown'
                }],
                'preferred_quality': content_url
            }
    
    def _find_content_url(self, html: str) -> Optional[str]:
        """Find the actual content URL in iframe HTML"""
        # This is a simplified version - real implementation would need to analyze the JS
        match = re.search(r'source:\s*["\']([^"\']+\.(mp4|pdf))["\']', html, re.I)
        return match.group(1) if match else None
