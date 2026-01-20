"""
Google Drive API client module.
"""

from googleapiclient.discovery import build
from googleapiclient.discovery import Resource

from .auth import get_authenticated_credentials


def get_drive_service() -> Resource:
    """
    Get an authenticated Google Drive service instance.
    
    Returns:
        Resource: Google Drive API service
    """
    creds = get_authenticated_credentials()
    service = build("drive", "v3", credentials=creds)
    return service


def get_docs_service() -> Resource:
    """
    Get an authenticated Google Docs service instance.

    Returns:
        Resource: Google Docs API service
    """
    creds = get_authenticated_credentials()
    service = build("docs", "v1", credentials=creds)
    return service


def get_tasks_service() -> Resource:
    """
    Get an authenticated Google Tasks service instance.

    Returns:
        Resource: Google Tasks API service
    """
    creds = get_authenticated_credentials()
    service = build("tasks", "v1", credentials=creds)
    return service


def get_sheets_service() -> Resource:
    """
    Get an authenticated Google Sheets service instance.

    Returns:
        Resource: Google Sheets API service
    """
    creds = get_authenticated_credentials()
    service = build("sheets", "v4", credentials=creds)
    return service

