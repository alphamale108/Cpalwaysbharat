import re
import aiohttp
from typing import Dict, List
from extractors.base_extractor import BaseExtractor

class AppxExtractor(BaseExtractor):
    PLATFORM = "appx"
    
    def is_valid_url(self, url: str) -> bool:
        return bool(re.match(r'https?://(www\.)?appx\.com/.+', url))
    
    async def extract(self, url: str) -> Dict:
        """Extract content from Appx without login"""
        # First get the course page to find API endpoints
        async with aiohttp.ClientSession() as session:
            # Step 1: Get course ID from URL
            course_id = self._extract_course_id(url)
            if not course_id:
                raise Exception("Could not extract course ID from URL")
            
            # Step 2: Call Appx API to get course content
            api_url = f"https://api.appx.com/v1/courses/{course_id}/public"
            async with session.get(api_url) as response:
                if response.status != 200:
                    raise Exception(f"Appx API error: HTTP {response.status}")
                
                data = await response.json()
                
                # Step 3: Process course content
                return self._parse_course_content(data)
    
    def _extract_course_id(self, url: str) -> Optional[str]:
        """Extract course ID from Appx URL"""
        match = re.search(r'/course/([^/]+)', url)
        return match.group(1) if match else None
    
    def _parse_course_content(self, data: Dict) -> Dict:
        """Parse Appx API response into standardized format"""
        # Find the first available video or PDF
        content = None
        for item in data.get('modules', []):
            for resource in item.get('resources', []):
                if resource.get('type') in ['video', 'pdf']:
                    content = resource
                    break
            if content:
                break
        
        if not content:
            raise Exception("No downloadable content found in course")
        
        # Prepare result based on content type
        result = {
            'title': f"{data.get('title', 'Appx Course')} - {content.get('title', 'Content')}",
            'type': content['type'],
            'platform': self.PLATFORM,
            'thumbnail': data.get('thumbnail'),
            'download_url': content.get('url'),
            'qualities': []
        }
        
        # Handle video qualities if available
        if content['type'] == 'video' and content.get('qualities'):
            result['qualities'] = [
                {
                    'resolution': q.get('quality', 'Unknown'),
                    'url': q['url'],
                    'size': self._format_size(q.get('size_bytes', 0))
                }
                for q in content['qualities']
            ]
            result['preferred_quality'] = result['qualities'][0]['url']
        
        return result
    
    def _format_size(self, bytes: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} TB"
