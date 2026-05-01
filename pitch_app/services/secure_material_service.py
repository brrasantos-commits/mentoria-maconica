"""
Secure Material Service - Serve materials without allowing downloads
"""
import os
import mimetypes
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from pitch_app.services.config import MATERIALS_DIR


def get_material_path(material_id: int, filename: str) -> Path:
    """
    Get the full path to a material file
    
    Args:
        material_id: Material ID
        filename: Material filename
        
    Returns:
        Path to the material file
        
    Raises:
        HTTPException: If file not found or path traversal detected
    """
    # Prevent path traversal attacks
    if ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")
    
    file_path = MATERIALS_DIR / filename
    
    # Ensure file exists and is within materials directory
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Material não encontrado")
    
    if not file_path.is_relative_to(MATERIALS_DIR):
        raise HTTPException(status_code=400, detail="Acesso negado")
    
    return file_path


def stream_material(file_path: Path, disable_download: bool = True) -> StreamingResponse:
    """
    Stream a material file with optional download protection
    
    Args:
        file_path: Path to the material file
        disable_download: If True, prevents browser from downloading the file
        
    Returns:
        StreamingResponse with the file content
    """
    # Determine content type
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "application/octet-stream"
    
    # For PDFs and videos, force inline display
    if content_type in ["application/pdf", "video/mp4", "video/webm", "video/quicktime"]:
        content_type = content_type  # Keep original
    
    def file_iterator():
        """Generator to stream file in chunks"""
        with open(file_path, "rb") as f:
            chunk_size = 8192  # 8KB chunks
            while chunk := f.read(chunk_size):
                yield chunk
    
    headers = {}
    
    if disable_download:
        # Force inline display (no download)
        headers["Content-Disposition"] = f'inline; filename="{file_path.name}"'
        
        # Additional security headers to prevent download
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # For PDFs, add additional protection
        if content_type == "application/pdf":
            headers["Content-Security-Policy"] = "default-src 'self'"
    else:
        # Allow download
        headers["Content-Disposition"] = f'attachment; filename="{file_path.name}"'
    
    return StreamingResponse(
        file_iterator(),
        media_type=content_type,
        headers=headers
    )


def get_secure_material_response(
    material_id: int,
    filename: str,
    allow_download: bool = False
) -> StreamingResponse:
    """
    Get a secure streaming response for a material
    
    Args:
        material_id: Material ID
        filename: Material filename
        allow_download: If True, allows downloading the file
        
    Returns:
        StreamingResponse with the material content
    """
    file_path = get_material_path(material_id, filename)
    return stream_material(file_path, disable_download=not allow_download)

# Made with Bob
