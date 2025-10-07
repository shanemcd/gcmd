"""
List and search functionality for Google Drive files.
"""

from typing import Optional, List, Dict
from googleapiclient.errors import HttpError

from .client import get_drive_service


def list_files(
    query: Optional[str] = None,
    mime_type: Optional[str] = None,
    max_results: int = 20,
    order_by: str = "modifiedTime desc",
    include_trashed: bool = False,
) -> List[Dict]:
    """
    List files from Google Drive with optional filters.
    
    Args:
        query: Search query string (searches name and full text)
        mime_type: Filter by MIME type
        max_results: Maximum number of results to return
        order_by: Sort order (e.g., "modifiedTime desc", "name", "createdTime desc")
        include_trashed: Include trashed files
        
    Returns:
        List of file dictionaries with metadata
    """
    service = get_drive_service()
    
    # Build the query
    query_parts = []
    
    if not include_trashed:
        query_parts.append("trashed = false")
    
    if query:
        # Search in name and full text
        query_parts.append(f"(name contains '{query}' or fullText contains '{query}')")
    
    if mime_type:
        query_parts.append(f"mimeType = '{mime_type}'")
    
    q = " and ".join(query_parts) if query_parts else None
    
    try:
        results = service.files().list(
            q=q,
            pageSize=max_results,
            orderBy=order_by,
            fields="files(id,name,mimeType,size,createdTime,modifiedTime,webViewLink,owners)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        files = results.get("files", [])
        return files
        
    except HttpError as e:
        raise Exception(f"Failed to list files: {e}")


def search_files(query: str, max_results: int = 20) -> List[Dict]:
    """
    Search for files by name or content.
    
    Args:
        query: Search query string
        max_results: Maximum number of results
        
    Returns:
        List of matching files
    """
    return list_files(query=query, max_results=max_results)


def list_google_docs(max_results: int = 20) -> List[Dict]:
    """
    List only Google Docs.
    
    Args:
        max_results: Maximum number of results
        
    Returns:
        List of Google Docs
    """
    return list_files(
        mime_type="application/vnd.google-apps.document",
        max_results=max_results
    )


def list_google_sheets(max_results: int = 20) -> List[Dict]:
    """
    List only Google Sheets.
    
    Args:
        max_results: Maximum number of results
        
    Returns:
        List of Google Sheets
    """
    return list_files(
        mime_type="application/vnd.google-apps.spreadsheet",
        max_results=max_results
    )


def list_folders(max_results: int = 20) -> List[Dict]:
    """
    List only folders.
    
    Args:
        max_results: Maximum number of results
        
    Returns:
        List of folders
    """
    return list_files(
        mime_type="application/vnd.google-apps.folder",
        max_results=max_results
    )


def format_file_list(files: List[Dict], verbose: bool = False) -> str:
    """
    Format file list for display.
    
    Args:
        files: List of file dictionaries
        verbose: Show additional details
        
    Returns:
        Formatted string
    """
    if not files:
        return "No files found."
    
    output = []
    for file in files:
        file_id = file.get("id", "")
        name = file.get("name", "Untitled")
        mime_type = file.get("mimeType", "")
        
        # Simplify MIME type display
        type_display = mime_type
        if mime_type.startswith("application/vnd.google-apps."):
            type_display = mime_type.split(".")[-1].title()
        elif "/" in mime_type:
            type_display = mime_type.split("/")[-1].upper()
        
        if verbose:
            size = file.get("size")
            size_display = ""
            if size:
                size_mb = int(size) / (1024 * 1024)
                size_display = f" ({size_mb:.2f} MB)"
            
            modified = file.get("modifiedTime", "")
            owners = file.get("owners", [])
            owner_name = owners[0].get("displayName", "") if owners else ""
            
            output.append(
                f"[{type_display}] {name}\n"
                f"  ID: {file_id}\n"
                f"  Modified: {modified}{size_display}\n"
                f"  Owner: {owner_name}\n"
            )
        else:
            output.append(f"[{type_display:12}] {file_id:44} {name}")
    
    return "\n".join(output)

