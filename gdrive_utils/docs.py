"""
Google Docs API functionality for detailed document inspection.
"""

import json
from typing import List, Dict, Optional
from googleapiclient.errors import HttpError

from .client import get_docs_service


def get_document_details(document_id: str, include_tabs: bool = True) -> dict:
    """
    Get detailed document information including tabs, structure, and content.
    
    Args:
        document_id: Google Docs document ID
        include_tabs: If True, include all tabs content in the response
        
    Returns:
        dict: Document details including tabs, body, headers, footers, etc.
    """
    service = get_docs_service()
    
    try:
        # includeTabsContent parameter is required to get all tabs
        document = service.documents().get(
            documentId=document_id,
            includeTabsContent=include_tabs
        ).execute()
        return document
    except HttpError as e:
        raise Exception(f"Failed to get document details: {e}")


def list_document_tabs(document_id: str) -> List[Dict]:
    """
    List all tabs in a Google Doc.
    
    Args:
        document_id: Google Docs document ID
        
    Returns:
        List of tab information dictionaries
    """
    document = get_document_details(document_id)
    
    tabs = document.get('tabs', [])
    if not tabs:
        # Older documents might not have explicit tabs, just return the body
        return [{
            'tabId': 'default',
            'title': document.get('title', 'Untitled'),
            'index': 0,
            'isDefault': True
        }]
    
    tab_list = []
    for idx, tab in enumerate(tabs):
        # Tab properties might be at different levels
        tab_properties = tab.get('tabProperties', {})
        
        # Try to get the title from various possible locations
        title = (
            tab_properties.get('title') or 
            tab_properties.get('displayName') or
            tab.get('title') or
            tab.get('displayName') or
            f'Tab {idx + 1}'
        )
        
        tab_info = {
            'tabId': tab_properties.get('tabId') or tab.get('tabId', f'tab_{idx}'),
            'title': title,
            'index': tab_properties.get('index', idx),
        }
        
        # Add any additional metadata
        if 'childObjectId' in tab:
            tab_info['childObjectId'] = tab['childObjectId']
        
        tab_list.append(tab_info)
    
    return tab_list


def get_document_structure(document_id: str) -> Dict:
    """
    Get the structure of a document including headings and outline.
    
    Args:
        document_id: Google Docs document ID
        
    Returns:
        Dictionary with document structure information
    """
    document = get_document_details(document_id)
    
    # Extract headings and structure
    body = document.get('body', {})
    content = body.get('content', [])
    
    headings = []
    for element in content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            style = paragraph.get('paragraphStyle', {})
            named_style = style.get('namedStyleType', '')
            
            if named_style.startswith('HEADING_'):
                # Extract heading text
                elements = paragraph.get('elements', [])
                text = ''.join([
                    e.get('textRun', {}).get('content', '')
                    for e in elements
                    if 'textRun' in e
                ])
                
                level = named_style.replace('HEADING_', '')
                headings.append({
                    'level': level,
                    'text': text.strip(),
                    'style': named_style
                })
    
    return {
        'title': document.get('title', 'Untitled'),
        'documentId': document.get('documentId'),
        'headings': headings,
        'revisionId': document.get('revisionId'),
    }


def format_tabs_output(tabs: List[Dict]) -> str:
    """
    Format tabs list for display.
    
    Args:
        tabs: List of tab dictionaries
        
    Returns:
        Formatted string
    """
    if not tabs:
        return "No tabs found."
    
    output = []
    for tab in tabs:
        output.append(f"  📄 {tab['title']} (ID: {tab['tabId']})")
    
    return "\n".join(output)


def dump_document_raw(document_id: str, output_file: Optional[str] = None) -> str:
    """
    Dump raw document JSON for debugging.
    
    Args:
        document_id: Google Docs document ID
        output_file: Optional file to write JSON to
        
    Returns:
        JSON string of document
    """
    document = get_document_details(document_id)
    json_str = json.dumps(document, indent=2)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(json_str)
        return output_file
    else:
        return json_str


def export_tab_as_markdown(document_id: str, tab_id: str) -> str:
    """
    Export a specific tab from a Google Doc as plain text.
    
    Note: Google's native markdown export doesn't support per-tab export.
    This extracts plain text only. For full markdown formatting, export
    the entire document without --all-tabs.
    
    Args:
        document_id: Google Docs document ID
        tab_id: The tab ID to export
        
    Returns:
        Plain text content of the tab
    """
    from .client import get_drive_service
    import io
    from googleapiclient.http import MediaIoBaseDownload
    
    # Unfortunately, Google Drive API doesn't support exporting individual tabs
    # We have to extract text from the Docs API structure
    doc_service = get_docs_service()
    
    try:
        document = doc_service.documents().get(
            documentId=document_id,
            includeTabsContent=True
        ).execute()
        
        # Find the specific tab
        tabs = document.get('tabs', [])
        target_tab = None
        for tab in tabs:
            tab_props = tab.get('tabProperties', {})
            if tab_props.get('tabId') == tab_id:
                target_tab = tab
                break
        
        if not target_tab:
            raise Exception(f"Tab {tab_id} not found in document")
        
        # Use a simple recursive function to extract all text
        def extract_text(elements):
            text = []
            for element in elements:
                if 'textRun' in element:
                    text.append(element['textRun'].get('content', ''))
                elif 'paragraph' in element:
                    text.extend(extract_text(element['paragraph'].get('elements', [])))
                elif 'table' in element:
                    for row in element['table'].get('tableRows', []):
                        for cell in row.get('tableCells', []):
                            text.extend(extract_text(cell.get('content', [])))
            return text
        
        content = target_tab.get('documentTab', {}).get('body', {}).get('content', [])
        return ''.join(extract_text(content))
        
    except HttpError as e:
        raise Exception(f"Failed to export tab: {e}")


def export_all_tabs(document_id: str, output_dir: str = ".") -> List[str]:
    """
    Export all tabs from a Google Doc as separate text files.
    
    Args:
        document_id: Google Docs document ID
        output_dir: Directory to save the files
        
    Returns:
        List of file paths that were created
    """
    from pathlib import Path
    import re
    
    # Get all tabs
    tabs = list_document_tabs(document_id)
    
    # Get document title for base filename
    document = get_document_details(document_id)
    doc_title = document.get('title', 'document')
    
    # Sanitize filename
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', doc_title)

    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)
    
    exported_files = []
    
    for tab in tabs:
        tab_id = tab['tabId']
        tab_title = tab['title']
        
        # Sanitize tab title for filename
        safe_tab_title = re.sub(r'[<>:"/\\|?*]', '_', tab_title)
        
        # Create filename with "exported" to match .gitignore pattern
        if len(tabs) == 1:
            filename = f"{safe_title}.exported.md"
        else:
            filename = f"{safe_title} - {safe_tab_title}.exported.md"
        
        filepath = output_path / filename
        
        try:
            # Export the tab as markdown
            content = export_tab_as_markdown(document_id, tab_id)
            
            # Write to file
            filepath.write_text(content)
            exported_files.append(str(filepath))
            
        except Exception as e:
            print(f"Warning: Failed to export tab '{tab_title}': {e}")
    
    return exported_files


def format_headings_output(headings: List[Dict]) -> str:
    """
    Format headings list for display.
    
    Args:
        headings: List of heading dictionaries
        
    Returns:
        Formatted string
    """
    if not headings:
        return "No headings found."
    
    output = []
    for heading in headings:
        level = heading['level']
        indent = "  " * (int(level) if level.isdigit() else 1)
        output.append(f"{indent}• {heading['text']}")
    
    return "\n".join(output)

