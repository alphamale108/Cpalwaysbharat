import os
import subprocess
from cryptography.fernet import Fernet
import logging
from typing import Dict

logger = logging.getLogger(__name__)

async def apply_drm(content_info: Dict) -> str:
    """
    Apply DRM protection to video content
    Returns path to the DRM-protected file
    """
    try:
        if content_info['type'] != 'video':
            return content_info.get('file_path')
        
        # Generate unique key for this content
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        # Download video if not already downloaded
        if not content_info.get('file_path'):
            from utilities.file_utils import download_file
            content_info['file_path'] = await download_file(content_info['stream_url'], 'video')
        
        input_file = content_info['file_path']
        output_file = f"drm_protected_{os.path.basename(input_file)}"
        
        # Encrypt the video file
        with open(input_file, 'rb') as f:
            file_data = f.read()
        
        encrypted_data = cipher.encrypt(file_data)
        
        with open(output_file, 'wb') as f:
            f.write(encrypted_data)
        
        # Clean up original file
        os.remove(input_file)
        
        return output_file
    
    except Exception as e:
        logger.error(f"DRM application failed: {str(e)}", exc_info=True)
        raise
