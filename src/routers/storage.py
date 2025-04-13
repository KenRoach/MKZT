import os
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.services.storage_service import FileMetadata, storage_service
from src.utils.auth import get_current_user

router = APIRouter(prefix="/storage", tags=["storage"])

class FileResponse(BaseModel):
    """Response model for file operations."""
    success: bool
    message: str
    data: Optional[FileMetadata] = None

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    path: str = Form(...),
    make_public: bool = Form(True),
    current_user = Depends(get_current_user)
):
    """
    Upload a file to Supabase Storage.
    
    Args:
        file: File to upload
        path: Storage path (e.g., 'merchants/images')
        make_public: Whether to make the file publicly accessible
        current_user: Current authenticated user
        
    Returns:
        FileResponse with upload results
    """
    try:
        # Read file content
        content = await file.read()
        
        # Upload to Supabase Storage
        metadata = await storage_service.upload_file(
            file_data=content,
            filename=file.filename,
            content_type=file.content_type,
            path=path,
            make_public=make_public
        )
        
        return FileResponse(
            success=True,
            message="File uploaded successfully",
            data=metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

@router.get("/download/{path:path}")
async def download_file(
    path: str,
    current_user = Depends(get_current_user)
):
    """
    Download a file from Supabase Storage.
    
    Args:
        path: Full path to the file in storage
        current_user: Current authenticated user
        
    Returns:
        FileResponse with file content
    """
    try:
        # Download from Supabase Storage
        content, content_type = await storage_service.download_file(path)
        
        # Create temporary file
        temp_path = f"/tmp/{os.path.basename(path)}"
        with open(temp_path, "wb") as f:
            f.write(content)
        
        return FileResponse(
            path=temp_path,
            media_type=content_type,
            filename=os.path.basename(path)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )

@router.delete("/{path:path}", response_model=FileResponse)
async def delete_file(
    path: str,
    current_user = Depends(get_current_user)
):
    """
    Delete a file from Supabase Storage.
    
    Args:
        path: Full path to the file in storage
        current_user: Current authenticated user
        
    Returns:
        FileResponse with deletion results
    """
    try:
        # Delete from Supabase Storage
        success = await storage_service.delete_file(path)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        return FileResponse(
            success=True,
            message="File deleted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )

@router.get("/list/{path:path}", response_model=List[FileMetadata])
async def list_files(
    path: str,
    prefix: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    List files in a Supabase Storage path.
    
    Args:
        path: Base path to list files from
        prefix: Optional prefix to filter files
        current_user: Current authenticated user
        
    Returns:
        List of FileMetadata objects
    """
    try:
        # List files from Supabase Storage
        files = await storage_service.list_files(path, prefix)
        
        return files
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )

@router.get("/signed-url/{path:path}")
async def get_signed_url(
    path: str,
    expiration: int = 3600,
    current_user = Depends(get_current_user)
):
    """
    Generate a signed URL for temporary access to a file.
    
    Args:
        path: Full path to the file in storage
        expiration: URL expiration time in seconds
        current_user: Current authenticated user
        
    Returns:
        Signed URL string
    """
    try:
        # Generate signed URL
        url = await storage_service.get_signed_url(path, expiration)
        
        return {"url": url}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating signed URL: {str(e)}"
        )

@router.post("/copy", response_model=FileResponse)
async def copy_file(
    source_path: str = Form(...),
    destination_path: str = Form(...),
    current_user = Depends(get_current_user)
):
    """
    Copy a file within Supabase Storage.
    
    Args:
        source_path: Path of the source file
        destination_path: Path for the destination file
        current_user: Current authenticated user
        
    Returns:
        FileResponse with copy results
    """
    try:
        # Copy file in Supabase Storage
        metadata = await storage_service.copy_file(source_path, destination_path)
        
        return FileResponse(
            success=True,
            message="File copied successfully",
            data=metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error copying file: {str(e)}"
        )

@router.post("/move", response_model=FileResponse)
async def move_file(
    source_path: str = Form(...),
    destination_path: str = Form(...),
    current_user = Depends(get_current_user)
):
    """
    Move a file within Supabase Storage.
    
    Args:
        source_path: Path of the source file
        destination_path: Path for the destination file
        current_user: Current authenticated user
        
    Returns:
        FileResponse with move results
    """
    try:
        # Move file in Supabase Storage
        metadata = await storage_service.move_file(source_path, destination_path)
        
        return FileResponse(
            success=True,
            message="File moved successfully",
            data=metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error moving file: {str(e)}"
        ) 