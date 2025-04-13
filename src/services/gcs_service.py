import os
import uuid
from typing import List, Optional, Tuple, Union
from urllib.parse import urljoin

import aiohttp
from google.cloud import storage
from google.cloud.storage import Blob
from google.oauth2 import service_account
from pydantic import BaseModel

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FileMetadata(BaseModel):
    """Model for file metadata."""
    filename: str
    content_type: str
    size: int
    path: str
    public_url: str

class GCSService:
    """Service for handling Google Cloud Storage operations."""
    
    def __init__(self):
        """Initialize GCS client with credentials."""
        self.project_id = settings.GOOGLE_CLOUD_PROJECT_ID
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.public_url = settings.GCS_PUBLIC_URL
        self.max_file_size = settings.GCS_MAX_FILE_SIZE
        self.allowed_image_types = settings.GCS_ALLOWED_IMAGE_TYPES.split(',')
        self.allowed_document_types = settings.GCS_ALLOWED_DOCUMENT_TYPES.split(',')
        
        # Initialize credentials
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_APPLICATION_CREDENTIALS
        )
        
        # Initialize client
        self.client = storage.Client(
            project=self.project_id,
            credentials=credentials
        )
        self.bucket = self.client.bucket(self.bucket_name)
        
        logger.info(f"Initialized GCS service for bucket: {self.bucket_name}")
    
    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        path: str,
        make_public: bool = True
    ) -> FileMetadata:
        """
        Upload a file to GCS.
        
        Args:
            file_data: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            path: Storage path (e.g., 'merchants/images')
            make_public: Whether to make the file publicly accessible
            
        Returns:
            FileMetadata object with file information
        """
        try:
            # Validate file size
            if len(file_data) > self.max_file_size:
                raise ValueError(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")
            
            # Validate content type
            if content_type not in self.allowed_image_types + self.allowed_document_types:
                raise ValueError(f"Content type {content_type} not allowed")
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            blob_path = f"{path}/{unique_filename}"
            
            # Create blob and upload
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(
                file_data,
                content_type=content_type
            )
            
            # Make public if requested
            if make_public:
                blob.make_public()
            
            # Generate public URL
            public_url = blob.public_url if make_public else None
            
            metadata = FileMetadata(
                filename=unique_filename,
                content_type=content_type,
                size=len(file_data),
                path=blob_path,
                public_url=public_url
            )
            
            logger.info(f"Successfully uploaded file: {blob_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error uploading file to GCS: {str(e)}")
            raise
    
    async def download_file(self, path: str) -> Tuple[bytes, str]:
        """
        Download a file from GCS.
        
        Args:
            path: Full path to the file in GCS
            
        Returns:
            Tuple of (file_data, content_type)
        """
        try:
            blob = self.bucket.blob(path)
            file_data = blob.download_as_bytes()
            content_type = blob.content_type
            
            logger.info(f"Successfully downloaded file: {path}")
            return file_data, content_type
            
        except Exception as e:
            logger.error(f"Error downloading file from GCS: {str(e)}")
            raise
    
    async def delete_file(self, path: str) -> bool:
        """
        Delete a file from GCS.
        
        Args:
            path: Full path to the file in GCS
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob = self.bucket.blob(path)
            blob.delete()
            
            logger.info(f"Successfully deleted file: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from GCS: {str(e)}")
            return False
    
    async def list_files(self, path: str, prefix: Optional[str] = None) -> List[FileMetadata]:
        """
        List files in a GCS path.
        
        Args:
            path: Base path to list files from
            prefix: Optional prefix to filter files
            
        Returns:
            List of FileMetadata objects
        """
        try:
            blobs = self.bucket.list_blobs(prefix=path)
            files = []
            
            for blob in blobs:
                if prefix and not blob.name.startswith(prefix):
                    continue
                    
                metadata = FileMetadata(
                    filename=os.path.basename(blob.name),
                    content_type=blob.content_type,
                    size=blob.size,
                    path=blob.name,
                    public_url=blob.public_url
                )
                files.append(metadata)
            
            logger.info(f"Successfully listed files in path: {path}")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files in GCS: {str(e)}")
            raise
    
    async def get_signed_url(self, path: str, expiration: int = 3600) -> str:
        """
        Generate a signed URL for temporary access to a file.
        
        Args:
            path: Full path to the file in GCS
            expiration: URL expiration time in seconds
            
        Returns:
            Signed URL string
        """
        try:
            blob = self.bucket.blob(path)
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
            
            logger.info(f"Generated signed URL for file: {path}")
            return url
            
        except Exception as e:
            logger.error(f"Error generating signed URL: {str(e)}")
            raise
    
    async def copy_file(self, source_path: str, destination_path: str) -> FileMetadata:
        """
        Copy a file within GCS.
        
        Args:
            source_path: Path of the source file
            destination_path: Path for the destination file
            
        Returns:
            FileMetadata object for the new file
        """
        try:
            source_blob = self.bucket.blob(source_path)
            destination_blob = self.bucket.blob(destination_path)
            
            self.bucket.copy_blob(
                source_blob,
                self.bucket,
                destination_blob.name
            )
            
            metadata = FileMetadata(
                filename=os.path.basename(destination_path),
                content_type=destination_blob.content_type,
                size=destination_blob.size,
                path=destination_path,
                public_url=destination_blob.public_url
            )
            
            logger.info(f"Successfully copied file from {source_path} to {destination_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error copying file in GCS: {str(e)}")
            raise
    
    async def move_file(self, source_path: str, destination_path: str) -> FileMetadata:
        """
        Move a file within GCS.
        
        Args:
            source_path: Path of the source file
            destination_path: Path for the destination file
            
        Returns:
            FileMetadata object for the moved file
        """
        try:
            # Copy the file
            metadata = await self.copy_file(source_path, destination_path)
            
            # Delete the original
            await self.delete_file(source_path)
            
            logger.info(f"Successfully moved file from {source_path} to {destination_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error moving file in GCS: {str(e)}")
            raise

# Create singleton instance
gcs_service = GCSService() 