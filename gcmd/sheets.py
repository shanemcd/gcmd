"""
Google Sheets API functionality for spreadsheet operations.
"""

import io
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

from .client import get_sheets_service, get_drive_service


def get_spreadsheet_metadata(spreadsheet_id: str) -> Dict:
    """
    Get metadata for a Google Spreadsheet including all sheet names.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID

    Returns:
        dict: Spreadsheet metadata including sheets
    """
    service = get_sheets_service()

    try:
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="spreadsheetId,properties.title,sheets.properties"
        ).execute()
        return spreadsheet
    except HttpError as e:
        raise Exception(f"Failed to get spreadsheet metadata: {e}")


def list_sheets(spreadsheet_id: str) -> List[Dict]:
    """
    List all sheets (tabs) in a Google Spreadsheet.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID

    Returns:
        List of sheet information dictionaries with sheetId, title, and index
    """
    metadata = get_spreadsheet_metadata(spreadsheet_id)

    sheets = []
    for sheet in metadata.get('sheets', []):
        props = sheet.get('properties', {})
        sheets.append({
            'sheetId': props.get('sheetId'),
            'title': props.get('title', 'Untitled'),
            'index': props.get('index', 0),
        })

    return sorted(sheets, key=lambda x: x['index'])


def export_sheet_as_csv(spreadsheet_id: str, sheet_id: int, max_retries: int = 5) -> str:
    """
    Export a single sheet from a Google Spreadsheet as CSV.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        sheet_id: The sheet's gid (sheet ID)
        max_retries: Maximum number of retry attempts for rate limiting

    Returns:
        str: CSV content as string
    """
    import time

    service = get_drive_service()

    # Build the export URL manually
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"

    last_error = None
    for attempt in range(max_retries):
        try:
            # Use the Drive API's http property directly
            http = service._http
            response, content = http.request(url)

            if response.status == 200:
                return content.decode('utf-8')
            elif response.status == 429:
                # Rate limited - wait and retry
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"Rate limited, retrying in {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
                last_error = Exception(f"Rate limited (HTTP 429)")
            else:
                raise Exception(f"Failed to export sheet: HTTP {response.status}")

        except HttpError as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    raise Exception(f"Failed to export sheet as CSV after {max_retries} attempts: {last_error}")


def export_spreadsheet_as_csv(
    spreadsheet_id: str,
    output_dir: Optional[str] = None,
    sheet_names: Optional[List[str]] = None,
    delay_between_sheets: float = 1.0
) -> List[str]:
    """
    Export a Google Spreadsheet to CSV files, one per sheet.

    Creates a directory named after the spreadsheet and exports each sheet
    as a separate CSV file within that directory.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        output_dir: Base output directory (default: current directory)
        sheet_names: Optional list of specific sheet names to export (default: all)
        delay_between_sheets: Delay in seconds between sheet exports to avoid rate limiting

    Returns:
        List of file paths that were created
    """
    import time
    # Get spreadsheet metadata
    metadata = get_spreadsheet_metadata(spreadsheet_id)
    spreadsheet_title = metadata.get('properties', {}).get('title', 'spreadsheet')

    # Sanitize the spreadsheet title for use as directory name
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', spreadsheet_title)

    # Create output directory
    base_path = Path(output_dir).expanduser() if output_dir else Path.cwd()
    output_path = base_path / safe_title
    output_path.mkdir(parents=True, exist_ok=True)

    # Get all sheets
    sheets = list_sheets(spreadsheet_id)

    # Filter sheets if specific names requested
    if sheet_names:
        sheets = [s for s in sheets if s['title'] in sheet_names]
        if not sheets:
            raise Exception(f"No sheets found matching: {sheet_names}")

    exported_files = []
    total_sheets = len(sheets)

    for idx, sheet in enumerate(sheets, 1):
        sheet_title = sheet['title']
        sheet_id = sheet['sheetId']

        # Sanitize sheet title for filename
        safe_sheet_title = re.sub(r'[<>:"/\\|?*]', '_', sheet_title)
        filename = f"{safe_sheet_title}.csv"
        filepath = output_path / filename

        # Add delay between sheets to avoid rate limiting (skip first sheet)
        if idx > 1 and delay_between_sheets > 0:
            time.sleep(delay_between_sheets)

        try:
            print(f"Exporting sheet {idx}/{total_sheets}: {sheet_title}...", file=sys.stderr)

            # Export the sheet
            content = export_sheet_as_csv(spreadsheet_id, sheet_id)

            # Write to file
            filepath.write_text(content, encoding='utf-8')
            exported_files.append(str(filepath))

        except Exception as e:
            print(f"Warning: Failed to export sheet '{sheet_title}': {e}", file=sys.stderr)

    return exported_files


def format_sheets_output(sheets: List[Dict]) -> str:
    """
    Format sheets list for display.

    Args:
        sheets: List of sheet dictionaries

    Returns:
        Formatted string
    """
    if not sheets:
        return "No sheets found."

    output = []
    for sheet in sheets:
        output.append(f"  📊 {sheet['title']} (ID: {sheet['sheetId']})")

    return "\n".join(output)
