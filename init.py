from extractors.utkarsh import UtkarshExtractor
from extractors.appx import AppxExtractor
from extractors.classplus import ClassPlusExtractor
from extractors.universal import UniversalExtractor

def get_extractor(url: str):
    """Get appropriate extractor for the URL"""
    url = url.lower()
    
    if 'utkarsh' in url:
        return UtkarshExtractor()
    elif 'appx' in url:
        return AppxExtractor()
    elif 'classplus' in url:
        return ClassPlusExtractor()
    else:
        return UniversalExtractor()
