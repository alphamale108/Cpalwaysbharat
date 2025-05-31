from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    @abstractmethod
    async def extract_content(self, url: str) -> dict:
        """
        Extract content from the given URL
        Returns a dictionary with:
        - title: str
        - description: str
        - duration: int (in seconds)
        - thumbnail: str (URL)
        - stream_url: str
        - subtitles: list (optional)
        """
        pass
    
    @abstractmethod
    def is_valid_url(self, url: str) -> bool:
        """
        Check if the URL is valid for this extractor
        """
        pass
