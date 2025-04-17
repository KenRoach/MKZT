import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from src.utils.logger import logger, RequestContext, log_execution_time

# Load environment variables
load_dotenv()

class StorageHandler:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.bucket_name = os.getenv("STORAGE_BUCKET_NAME", "default")
        self.logger = logger
    
    @log_execution_time(logger)
    async def upload_file(self, file_path: str, destination_path: str) -> Dict[str, Any]:
        """Upload a file to storage"""
        try:
            self.logger.info(
                "Uploading file to storage",
                file_path=file_path,
                destination=destination_path,
                bucket=self.bucket_name
            )
            
            with open(file_path, 'rb') as f:
                response = self.supabase.storage.from_(self.bucket_name).upload(
                    destination_path,
                    f.read()
                )
            
            self.logger.info(
                "File uploaded successfully",
                file_path=file_path,
                destination=destination_path
            )
            
            return {
                "status": "success",
                "path": destination_path,
                "message": "File uploaded successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error uploading file",
                error=str(e),
                file_path=file_path,
                destination=destination_path
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def download_file(self, file_path: str, destination_path: str) -> Dict[str, Any]:
        """Download a file from storage"""
        try:
            self.logger.info(
                "Downloading file from storage",
                file_path=file_path,
                destination=destination_path,
                bucket=self.bucket_name
            )
            
            response = self.supabase.storage.from_(self.bucket_name).download(file_path)
            
            with open(destination_path, 'wb') as f:
                f.write(response)
            
            self.logger.info(
                "File downloaded successfully",
                file_path=file_path,
                destination=destination_path
            )
            
            return {
                "status": "success",
                "path": destination_path,
                "message": "File downloaded successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error downloading file",
                error=str(e),
                file_path=file_path,
                destination=destination_path
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file from storage"""
        try:
            self.logger.info(
                "Deleting file from storage",
                file_path=file_path,
                bucket=self.bucket_name
            )
            
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            self.logger.info(
                "File deleted successfully",
                file_path=file_path
            )
            
            return {
                "status": "success",
                "message": "File deleted successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error deleting file",
                error=str(e),
                file_path=file_path
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> Dict[str, Any]:
        """Get a signed URL for a file"""
        try:
            self.logger.info(
                "Generating signed URL for file",
                file_path=file_path,
                expires_in=expires_in,
                bucket=self.bucket_name
            )
            
            url = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                file_path,
                expires_in
            )
            
            self.logger.info(
                "Signed URL generated successfully",
                file_path=file_path,
                expires_in=expires_in
            )
            
            return {
                "status": "success",
                "url": url,
                "message": "Signed URL generated successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error generating signed URL",
                error=str(e),
                file_path=file_path
            )
            return {
                "status": "error",
                "message": str(e)
            }
    
    @log_execution_time(logger)
    async def list_files(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """List files in storage"""
        try:
            self.logger.info(
                "Listing files in storage",
                prefix=prefix,
                bucket=self.bucket_name
            )
            
            files = self.supabase.storage.from_(self.bucket_name).list(prefix)
            
            self.logger.info(
                "Files listed successfully",
                count=len(files),
                prefix=prefix
            )
            
            return {
                "status": "success",
                "files": files,
                "message": "Files listed successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error listing files",
                error=str(e),
                prefix=prefix
            )
            return {
                "status": "error",
                "message": str(e),
                "files": []
            }
    
    @log_execution_time(logger)
    async def move_file(self, source_path: str, destination_path: str) -> Dict[str, Any]:
        """Move a file in storage"""
        try:
            self.logger.info(
                "Moving file in storage",
                source=source_path,
                destination=destination_path,
                bucket=self.bucket_name
            )
            
            # Download the file
            file_content = self.supabase.storage.from_(self.bucket_name).download(source_path)
            
            # Upload to new location
            self.supabase.storage.from_(self.bucket_name).upload(
                destination_path,
                file_content
            )
            
            # Delete from old location
            self.supabase.storage.from_(self.bucket_name).remove([source_path])
            
            self.logger.info(
                "File moved successfully",
                source=source_path,
                destination=destination_path
            )
            
            return {
                "status": "success",
                "message": "File moved successfully"
            }
            
        except Exception as e:
            self.logger.exception(
                "Error moving file",
                error=str(e),
                source=source_path,
                destination=destination_path
            )
            return {
                "status": "error",
                "message": str(e)
            } 