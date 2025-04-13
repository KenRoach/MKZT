import os
import logging
from typing import Dict, Any, Optional
from instagram_private_api import Client, ClientCompatPatch
from instagram_private_api.errors import ClientError

logger = logging.getLogger(__name__)

class InstagramClient:
    """Client for handling Instagram messaging"""
    
    def __init__(self):
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        
        if not all([self.username, self.password]):
            raise ValueError("Missing required Instagram configuration")
            
        self.client = Client(self.username, self.password)
        
    async def send_direct_message(
        self,
        user_id: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a direct message to a user"""
        try:
            # Prepare message parameters
            message_params = {
                "text": message,
                "thread_id": user_id
            }
            
            # Add media if provided
            if media_url:
                # Download media to temporary file
                media_path = await self._download_media(media_url)
                message_params["media"] = media_path
                
            # Send the message
            response = self.client.direct_send(**message_params)
            
            # Clean up temporary media file if created
            if media_url:
                os.remove(media_path)
                
            return {
                "status": "success",
                "message_id": response["thread_id"],
                "status": "sent"
            }
            
        except ClientError as e:
            logger.error(f"Instagram error sending direct message: {str(e)}")
            raise
            
    async def get_user_id(self, username: str) -> str:
        """Get Instagram user ID from username"""
        try:
            user_info = self.client.username_info(username)
            return user_info["user"]["pk"]
        except ClientError as e:
            logger.error(f"Instagram error getting user ID: {str(e)}")
            raise
            
    async def _download_media(self, url: str) -> str:
        """Download media from URL to temporary file"""
        import aiohttp
        import tempfile
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to download media from {url}")
                    
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(await response.read())
                temp_file.close()
                
                return temp_file.name

# Create singleton instance
instagram_client = InstagramClient() 