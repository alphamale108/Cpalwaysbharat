import re
import aiohttp
from typing import Dict, List
from extractors.base_extractor import BaseExtractor

class UtkarshExtractor(BaseExtractor):
    PLATFORM = "utkarsh"
    
    def is_valid_url(self, url: str) -> bool:
        return bool(re.match(r'https?://(www\.)?utkarsh\.com/.+', url))
    
    async def extract(self, url: str) -> Dict:
        """Extract content from Utkarsh Classes"""
        async with aiohttp.ClientSession() as session:
            # Step 1: Get course ID from URL
            course_id = self._extract_course_id(url)
            if not course_id:
                raise Exception("Could not extract course ID from URL")
            
            # Step 2: Call Utkarsh API (simulated)
            api_url = f"https://api.utkarsh.com/courses/{course_id}/public"
            async with session.get(api_url) as response:
                if response.status != 200:
                    raise Exception(f"Utkarsh API error: HTTP {response.status}")
                
                data = await response.json()
                
                # Step 3: Process course content
                return self._parse_course_content(data)
    
    def _extract_course_id(self, url: str) -> Optional[str]:
        """Extract course ID from Utkarsh URL"""
        match = re.search(r'/courses/([^/]+)', url)
        return match.group(1) if match else None
    
    def _parse_course_content(self, data: Dict) -> Dict:
        """Parse Utkarsh API response into standardized format"""
        # Find the first available video or PDF
        content = None
        for section in data.get('sections', []):
            for item in section.get('items', []):
                if item.get('type') in ['video', 'pdf']:
                    content = item
                    break
            if content:
                break
        
        if not content:
            raise Exception("No downloadable content found in course")
        
        # Prepare result based on content type
        result = {
            'title': f"{data.get('course_title', 'Utkarsh Course')} - {content.get('title', 'Content')}",
            'type': content['type'],
            'platform': self.PLATFORM,
            'thumbnail': data.get('thumbnail_url'),
            'download_url': content.get('url'),
            'qualities': []
        }
        
        # Handle video durations
        if content['type'] == 'video':
            result['duration'] = content.get('duration_seconds', 0)
            result['duration_formatted'] = self._format_duration(result['duration'])
            
            # Add qualities if available
            if content.get('qualities'):
                result['qualities'] = [
                    {
                        'resolution': q.get('quality', 'Unknown'),
                        'url': q['url'],
                        'size': self._format_size(q.get('size_bytes', 0))
                    }
                    for q in content['qualities']
                ]
                result['preferred_quality'] = result['qualities'][0]['url']
            else:
                # Default quality if none specified
                result['qualities'] = [{
                    'resolution': 'Original',
                    'url': content['url'],
                    'size': self._format_size(content.get('size_bytes', 0))
                }]
                result['preferred_quality'] = content['url']
        
        return result
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _format_size(self, bytes: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} TB"
