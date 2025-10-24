"""
Comments functionality for Google Drive files.
"""

from typing import List, Dict
from googleapiclient.errors import HttpError

from .client import get_drive_service


def list_comments(file_id: str, include_deleted: bool = False) -> List[Dict]:
    """
    List all comments on a Google Drive file.
    
    Args:
        file_id: Google Drive file ID
        include_deleted: Include deleted comments
        
    Returns:
        List of comment dictionaries
    """
    service = get_drive_service()
    
    try:
        results = service.comments().list(
            fileId=file_id,
            fields="comments(id,content,author,createdTime,modifiedTime,resolved,deleted,replies,quotedFileContent,anchor)",
            includeDeleted=include_deleted
        ).execute()
        
        comments = results.get("comments", [])
        return comments
        
    except HttpError as e:
        raise Exception(f"Failed to list comments: {e}")


def format_comments_output(comments: List[Dict]) -> str:
    """
    Format comments for display.
    
    Args:
        comments: List of comment dictionaries
        
    Returns:
        Formatted string
    """
    if not comments:
        return "No comments found."
    
    output = []
    
    for comment in comments:
        author = comment.get("author", {})
        author_name = author.get("displayName", "Unknown")
        
        content = comment.get("content", "").strip()
        created = comment.get("createdTime", "")
        resolved = comment.get("resolved", False)
        deleted = comment.get("deleted", False)
        
        # Get anchor/quoted text if available
        quoted = comment.get("quotedFileContent", {})
        quoted_text = quoted.get("value", "")
        
        # Format status
        status = ""
        if deleted:
            status = " [DELETED]"
        elif resolved:
            status = " [RESOLVED]"
        
        output.append(f"\n{'='*70}")
        output.append(f"💬 {author_name}{status}")
        output.append(f"{'='*70}")
        output.append(f"Created: {created}")
        
        if quoted_text:
            output.append(f"\nQuoted text:")
            output.append(f'  "{quoted_text}"')
        
        output.append(f"\n{content}")
        
        # Show replies if any
        replies = comment.get("replies", [])
        if replies:
            output.append(f"\n  Replies ({len(replies)}):")
            for reply in replies:
                reply_author = reply.get("author", {})
                reply_author_name = reply_author.get("displayName", "Unknown")
                reply_content = reply.get("content", "").strip()
                reply_created = reply.get("createdTime", "")
                
                output.append(f"\n  ↳ {reply_author_name} ({reply_created}):")
                output.append(f"    {reply_content}")
    
    output.append(f"\n{'='*70}\n")
    output.append(f"Total comments: {len(comments)}")
    
    return "\n".join(output)

