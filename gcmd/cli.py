import argparse
import sys
from . import __version__
from .download import export_google_doc_as_markdown, download_file, get_file_metadata
from .list import list_files, search_files, list_google_docs, format_file_list
from .utils import extract_file_id
from .docs import list_document_tabs, get_document_structure, format_tabs_output, format_headings_output, export_all_tabs
from .comments import list_comments, format_comments_output
from .tasks import list_tasks, list_task_lists, format_task_list, format_task_lists
from .sheets import export_spreadsheet_as_csv, list_sheets, format_sheets_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gcmd",
        description="Command-line utilities for Google services (Drive, Docs, Sheets, and more)",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"gcmd {__version__}",
        help="Show the gcmd version and exit",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = False

    # Export subcommand - export Google Docs as markdown or Sheets as CSV
    export_parser = subparsers.add_parser(
        "export",
        help="Export a Google Doc as markdown or Sheet as CSV",
        description="Export a Google Doc to markdown format, or a Google Sheet to CSV files (one per sheet)",
    )
    export_parser.add_argument(
        "file_id_or_url",
        metavar="file_id_or_url",
        help="Google Drive file ID or full URL",
    )
    export_parser.add_argument(
        "-o",
        "--output",
        help="Output file path or directory (default: stdout for single file, current dir for --all-tabs)",
    )
    export_parser.add_argument(
        "--all-tabs",
        action="store_true",
        help="Export all tabs as separate markdown files (Google Docs only)",
    )
    export_parser.set_defaults(func=cmd_export)

    # Download subcommand - download any file
    download_parser = subparsers.add_parser(
        "download",
        help="Download a file from Google Drive",
        description="Download a file from Google Drive (for non-Google Doc files)",
    )
    download_parser.add_argument(
        "file_id_or_url",
        metavar="file_id_or_url",
        help="Google Drive file ID or full URL",
    )
    download_parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: current directory with original name)",
    )
    download_parser.set_defaults(func=cmd_download)

    # Info subcommand - show file metadata
    info_parser = subparsers.add_parser(
        "info",
        help="Show file metadata",
        description="Display metadata for a Google Drive file",
    )
    info_parser.add_argument(
        "file_id_or_url",
        metavar="file_id_or_url",
        help="Google Drive file ID or full URL",
    )
    info_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed information (permissions, sharing, capabilities, comments)",
    )
    info_parser.add_argument(
        "--show-comments",
        action="store_true",
        help="Show comments (automatically enabled with -v)",
    )
    info_parser.set_defaults(func=cmd_info)

    # List subcommand - list files
    list_parser = subparsers.add_parser(
        "list",
        help="List files from Google Drive",
        description="List files from Google Drive with optional filters",
    )
    list_parser.add_argument(
        "-q",
        "--query",
        help="Search query (searches in name and content)",
    )
    list_parser.add_argument(
        "-t",
        "--type",
        help="Filter by type (docs, sheets, folders, or MIME type)",
    )
    list_parser.add_argument(
        "-n",
        "--max-results",
        type=int,
        default=20,
        help="Maximum number of results (default: 20)",
    )
    list_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed information",
    )
    list_parser.add_argument(
        "--order-by",
        default="modifiedTime desc",
        help="Sort order (default: modifiedTime desc)",
    )
    list_parser.set_defaults(func=cmd_list)

    # Tasks subcommand - list Google Tasks
    tasks_parser = subparsers.add_parser(
        "tasks",
        help="List Google Tasks",
        description="List tasks from Google Tasks",
    )
    tasks_parser.add_argument(
        "-l",
        "--list-id",
        default="@default",
        help="Task list ID (default: @default for your default task list)",
    )
    tasks_parser.add_argument(
        "-n",
        "--max-results",
        type=int,
        default=100,
        help="Maximum number of tasks to return (default: 100)",
    )
    tasks_parser.add_argument(
        "-c",
        "--show-completed",
        action="store_true",
        help="Include completed tasks",
    )
    tasks_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed task information",
    )
    tasks_parser.add_argument(
        "--list-all-lists",
        action="store_true",
        help="Show all task lists instead of tasks",
    )
    tasks_parser.set_defaults(func=cmd_tasks)

    return parser


def cmd_export(args: argparse.Namespace) -> int:
    """Handle the 'export' subcommand."""
    try:
        file_id = extract_file_id(args.file_id_or_url)

        # Get file metadata to determine type
        metadata = get_file_metadata(file_id)
        mime_type = metadata.get("mimeType", "")

        # Handle Google Sheets - export as CSV
        if mime_type == "application/vnd.google-apps.spreadsheet":
            output_dir = args.output or "."
            print(f"Exporting spreadsheet to: {output_dir}", file=sys.stderr)

            exported_files = export_spreadsheet_as_csv(file_id, output_dir)

            print(f"\n✓ Successfully exported {len(exported_files)} sheet(s):", file=sys.stderr)
            for filepath in exported_files:
                print(f"  - {filepath}", file=sys.stderr)

            return 0

        # Handle Google Docs - export as markdown
        elif mime_type == "application/vnd.google-apps.document":
            # Check if we should export all tabs
            if args.all_tabs:
                output_dir = args.output or "."
                print(f"Exporting all tabs to: {output_dir}", file=sys.stderr)

                exported_files = export_all_tabs(file_id, output_dir)

                print(f"\n✓ Successfully exported {len(exported_files)} tab(s):", file=sys.stderr)
                for filepath in exported_files:
                    print(f"  - {filepath}", file=sys.stderr)

                return 0
            else:
                # Single file export (original behavior)
                result = export_google_doc_as_markdown(file_id, args.output)
                if result != "stdout":
                    print(f"Exported to: {result}", file=sys.stderr)
                return 0

        else:
            raise Exception(
                f"Unsupported file type: {mime_type}. "
                f"Export supports Google Docs (markdown) and Google Sheets (CSV)."
            )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_download(args: argparse.Namespace) -> int:
    """Handle the 'download' subcommand."""
    try:
        file_id = extract_file_id(args.file_id_or_url)
        result = download_file(file_id, args.output)
        print(f"Downloaded to: {result}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    """Handle the 'info' subcommand."""
    try:
        file_id = extract_file_id(args.file_id_or_url)
        metadata = get_file_metadata(file_id, detailed=args.verbose)
        
        # Basic information
        print(f"\n{'='*70}")
        print(f"FILE INFORMATION")
        print(f"{'='*70}\n")
        
        print(f"Name: {metadata.get('name')}")
        print(f"ID: {metadata.get('id')}")
        print(f"Type: {metadata.get('mimeType')}")
        
        if metadata.get('size'):
            size_mb = int(metadata['size']) / (1024 * 1024)
            print(f"Size: {size_mb:.2f} MB")
        
        print(f"\nCreated: {metadata.get('createdTime')}")
        print(f"Modified: {metadata.get('modifiedTime')}")
        
        if metadata.get('webViewLink'):
            print(f"\nWeb Link: {metadata.get('webViewLink')}")
        
        # Detailed information
        if args.verbose:
            print(f"\n{'='*70}")
            print(f"DETAILED INFORMATION")
            print(f"{'='*70}\n")
            
            # Owner information
            owners = metadata.get('owners', [])
            if owners:
                print(f"Owner(s):")
                for owner in owners:
                    print(f"  - {owner.get('displayName', 'Unknown')} ({owner.get('emailAddress', 'N/A')})")
            
            # Last modifier
            last_modifier = metadata.get('lastModifyingUser', {})
            if last_modifier:
                print(f"\nLast Modified By: {last_modifier.get('displayName', 'Unknown')} ({last_modifier.get('emailAddress', 'N/A')})")
            
            # Sharing info
            print(f"\nShared: {metadata.get('shared', False)}")
            if metadata.get('starred'):
                print(f"Starred: Yes")
            
            if metadata.get('description'):
                print(f"\nDescription: {metadata.get('description')}")
            
            # Version
            if metadata.get('version'):
                print(f"\nVersion: {metadata.get('version')}")
            
            # Permissions
            permissions = metadata.get('permissions', [])
            if permissions:
                print(f"\n{'='*70}")
                print(f"PERMISSIONS ({len(permissions)} total)")
                print(f"{'='*70}\n")
                for perm in permissions:
                    perm_type = perm.get('type', 'unknown')
                    role = perm.get('role', 'unknown')
                    
                    if perm_type == 'user':
                        email = perm.get('emailAddress', 'N/A')
                        display_name = perm.get('displayName', email)
                        print(f"  👤 {display_name} ({email}): {role}")
                    elif perm_type == 'group':
                        email = perm.get('emailAddress', 'N/A')
                        print(f"  👥 Group ({email}): {role}")
                    elif perm_type == 'domain':
                        domain = perm.get('domain', 'N/A')
                        print(f"  🏢 Domain ({domain}): {role}")
                    elif perm_type == 'anyone':
                        print(f"  🌍 Anyone with link: {role}")
            
            # Capabilities
            capabilities = metadata.get('capabilities', {})
            if capabilities:
                print(f"\n{'='*70}")
                print(f"CAPABILITIES")
                print(f"{'='*70}\n")
                
                key_caps = ['canEdit', 'canComment', 'canShare', 'canDownload', 'canCopy', 'canDelete']
                for cap in key_caps:
                    if cap in capabilities:
                        status = "✓ Yes" if capabilities[cap] else "✗ No"
                        cap_name = cap.replace('can', '')
                        print(f"  {cap_name}: {status}")
            
            # For Google Docs, show tabs and structure
            if metadata.get('mimeType') == 'application/vnd.google-apps.document':
                try:
                    print(f"\n{'='*70}")
                    print(f"DOCUMENT STRUCTURE")
                    print(f"{'='*70}\n")
                    
                    # Get tabs
                    tabs = list_document_tabs(file_id)
                    if tabs:
                        print(f"Tabs ({len(tabs)}):")
                        print(format_tabs_output(tabs))
                    
                    # Get document structure (headings)
                    structure = get_document_structure(file_id)
                    headings = structure.get('headings', [])
                    if headings:
                        print(f"\nHeadings ({len(headings)}):")
                        print(format_headings_output(headings))
                    
                except Exception as doc_error:
                    print(f"\nNote: Could not retrieve document structure: {doc_error}")
        
        # Show comments if requested (or if verbose)
        if args.verbose or args.show_comments:
            try:
                comments = list_comments(file_id)
                if comments:
                    print(f"\n{'='*70}")
                    print(f"COMMENTS")
                    print(format_comments_output(comments))
                else:
                    print(f"\n{'='*70}")
                    print(f"COMMENTS")
                    print(f"{'='*70}\n")
                    print("No comments on this file.")
                    print(f"\n{'='*70}\n")
            except Exception as comment_error:
                print(f"\nNote: Could not retrieve comments: {comment_error}")
        
        print(f"\n{'='*70}\n")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Handle the 'list' subcommand."""
    try:
        # Map type shortcuts to MIME types
        mime_type = None
        if args.type:
            type_map = {
                "docs": "application/vnd.google-apps.document",
                "sheets": "application/vnd.google-apps.spreadsheet",
                "slides": "application/vnd.google-apps.presentation",
                "folders": "application/vnd.google-apps.folder",
            }
            mime_type = type_map.get(args.type.lower(), args.type)

        files = list_files(
            query=args.query,
            mime_type=mime_type,
            max_results=args.max_results,
            order_by=args.order_by,
        )

        output = format_file_list(files, verbose=args.verbose)
        print(output)

        if files:
            print(f"\nFound {len(files)} file(s)", file=sys.stderr)

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_tasks(args: argparse.Namespace) -> int:
    """Handle the 'tasks' subcommand."""
    try:
        # Show all task lists if requested
        if args.list_all_lists:
            task_lists = list_task_lists(max_results=args.max_results)
            output = format_task_lists(task_lists)
            print(output)

            if task_lists:
                print(f"Found {len(task_lists)} task list(s)", file=sys.stderr)

            return 0

        # Otherwise, show tasks from the specified list
        tasks = list_tasks(
            tasklist_id=args.list_id,
            max_results=args.max_results,
            show_completed=args.show_completed,
        )

        output = format_task_list(tasks, verbose=args.verbose)
        print(output)

        if tasks:
            print(f"Found {len(tasks)} task(s)", file=sys.stderr)

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if hasattr(args, "func"):
        return int(args.func(args))

    # No subcommand: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

