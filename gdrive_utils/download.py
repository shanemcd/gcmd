"""
Download and export functionality for Google Drive files.
"""

import io
import sys
from pathlib import Path
from typing import Optional

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

from .client import get_drive_service


def get_file_metadata(file_id: str, detailed: bool = False) -> dict:
    """
    Get metadata for a file.
    
    Args:
        file_id: Google Drive file ID
        detailed: If True, fetch additional metadata (permissions, owners, etc.)
        
    Returns:
        dict: File metadata
    """
    service = get_drive_service()
    try:
        # Basic fields
        fields = "id,name,mimeType,size,createdTime,modifiedTime,webViewLink"
        
        # Add detailed fields if requested
        if detailed:
            fields += ",owners,lastModifyingUser,sharingUser,permissions,shared,description,starred,trashed,parents,version,viewedByMeTime,capabilities"
        
        file_metadata = service.files().get(
            fileId=file_id,
            fields=fields,
            supportsAllDrives=True
        ).execute()
        return file_metadata
    except HttpError as e:
        raise Exception(f"Failed to get file metadata: {e}")


def export_google_doc_as_markdown(file_id: str, output_path: Optional[str] = None, use_title: bool = True) -> str:
    """
    Export a Google Doc as markdown.
    
    Args:
        file_id: Google Drive file ID
        output_path: Optional output file path. If not provided and use_title=True, uses document title.
        use_title: If True and output_path is None, use document title as filename in current directory.
        
    Returns:
        str: Path to the downloaded file or "stdout" if printed
    """
    service = get_drive_service()
    
    try:
        # First, get file metadata to get the name
        metadata = get_file_metadata(file_id)
        file_name = metadata.get("name", "document")
        mime_type = metadata.get("mimeType", "")
        
        if mime_type != "application/vnd.google-apps.document":
            raise Exception(
                f"File is not a Google Doc (mime type: {mime_type}). "
                f"Use the 'download' command for other file types."
            )
        
        # Export as markdown using Google's native markdown export
        request = service.files().export_media(
            fileId=file_id,
            mimeType="text/markdown"
        )
        
        # Download the content
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%", file=sys.stderr)
        
        # Get the content
        content = fh.getvalue().decode("utf-8")

        # Sanitize filename to avoid path traversal issues
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', file_name)

        # Determine output path
        if output_path:
            output_file = Path(output_path).expanduser()
            # If it's a directory, use the file name
            if output_file.is_dir():
                output_file = output_file / f"{safe_filename}.md"
            elif not output_file.suffix:
                output_file = output_file.with_suffix(".md")
        elif use_title:
            # Use document title as filename in current directory with "exported" suffix
            output_file = Path(f"{safe_filename}.exported.md")
        else:
            # Print to stdout
            print(content)
            return "stdout"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)
        return str(output_file)
            
    except HttpError as e:
        raise Exception(f"Failed to export document: {e}")


def download_file(file_id: str, output_path: Optional[str] = None) -> str:
    """
    Download a non-Google Doc file.
    
    Args:
        file_id: Google Drive file ID
        output_path: Optional output file path. If not provided, uses the file's name.
        
    Returns:
        str: Path to the downloaded file
    """
    service = get_drive_service()
    
    try:
        # Get file metadata
        metadata = get_file_metadata(file_id)
        file_name = metadata.get("name", "file")
        mime_type = metadata.get("mimeType", "")
        
        # Google Docs, Sheets, Slides need to be exported, not downloaded
        if mime_type.startswith("application/vnd.google-apps."):
            raise Exception(
                f"This is a Google {mime_type.split('.')[-1].title()}. "
                f"Use 'export' command with appropriate format."
            )

        # Sanitize filename to avoid path traversal issues
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', file_name)

        # Download the file
        request = service.files().get_media(fileId=file_id)

        # Determine output path
        if output_path:
            output_file = Path(output_path).expanduser()
            if output_file.is_dir():
                output_file = output_file / safe_filename
        else:
            output_file = Path(safe_filename)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        fh = io.FileIO(str(output_file), "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%", file=sys.stderr)
        
        fh.close()
        return str(output_file)
        
    except HttpError as e:
        raise Exception(f"Failed to download file: {e}")

