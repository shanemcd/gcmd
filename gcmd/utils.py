"""
Utility functions for gcmd.
"""

import re
from typing import Optional


def extract_file_id(file_id_or_url: str) -> str:
    """
    Extract file ID from a Google Drive URL or return the ID if already provided.
    
    Supports various Google Drive URL formats:
    - https://docs.google.com/document/d/FILE_ID/edit
    - https://docs.google.com/spreadsheets/d/FILE_ID/edit
    - https://docs.google.com/presentation/d/FILE_ID/edit
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/open?id=FILE_ID
    - FILE_ID (just the ID itself)
    
    Args:
        file_id_or_url: Either a file ID or a full Google Drive URL
        
    Returns:
        str: The extracted file ID
        
    Raises:
        ValueError: If the URL format is not recognized or ID cannot be extracted
    """
    # If it's already a file ID (no slashes or special chars), return as-is
    if not any(char in file_id_or_url for char in ['/', ':', '?', '#']):
        return file_id_or_url.strip()
    
    # Try different URL patterns
    patterns = [
        # https://docs.google.com/document/d/FILE_ID/edit
        r'docs\.google\.com/(?:document|spreadsheets|presentation)/d/([a-zA-Z0-9-_]+)',
        # https://drive.google.com/file/d/FILE_ID/view
        r'drive\.google\.com/file/d/([a-zA-Z0-9-_]+)',
        # https://drive.google.com/open?id=FILE_ID
        r'drive\.google\.com/open\?id=([a-zA-Z0-9-_]+)',
        # https://drive.google.com/drive/folders/FILE_ID (for folders)
        r'drive\.google\.com/drive/folders/([a-zA-Z0-9-_]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, file_id_or_url)
        if match:
            return match.group(1)
    
    # If no pattern matched, raise an error
    raise ValueError(
        f"Could not extract file ID from: {file_id_or_url}\n"
        f"Supported formats:\n"
        f"  - File ID: 1abc123xyz\n"
        f"  - Google Docs: https://docs.google.com/document/d/FILE_ID/edit\n"
        f"  - Google Sheets: https://docs.google.com/spreadsheets/d/FILE_ID/edit\n"
        f"  - Google Slides: https://docs.google.com/presentation/d/FILE_ID/edit\n"
        f"  - Google Drive: https://drive.google.com/file/d/FILE_ID/view"
    )


def format_file_size(size_bytes: Optional[int]) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB", "500 KB")
    """
    if size_bytes is None:
        return "N/A"
    
    size = int(size_bytes)
    
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"

