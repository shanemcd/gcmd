# gcmd Agents

This document tracks the CLI agents, workflows, and conventions for `gcmd`. We'll iterate here as features land.

## Quickstart

- Run help:
  - `uv run gcmd --help`
- List your Google Drive files:
  - `uv run gcmd list`

## Authentication Setup

Before using gcmd commands, you need to set up OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the required APIs:
   - Google Drive API
   - Google Docs API
   - Google Sheets API
   - Google Tasks API
4. Create OAuth 2.0 Client ID credentials (Desktop app type)
5. Download the JSON credentials file
6. Save it to `~/.config/gcmd/credentials.json`

On first use, the CLI will open your browser to authenticate. Credentials are cached in `~/.config/gcmd/token.json`.

## Current Commands

### File Operations
- `list [-q query] [-t type] [-n max] [-v]`: list and search files in Google Drive
- `info <file-id-or-url> [-v] [--show-comments]`: show metadata, permissions, tabs, structure, and comments
- `download <file-id-or-url> [-o output]`: download a file from Google Drive
- `export <file-id-or-url> [-o output] [--all-tabs]`: export Google Doc as markdown or Sheet as CSV

### Tasks Operations
- `tasks [-l list-id] [-n max] [-c] [-v] [--list-all-lists]`: list Google Tasks from your task lists

**Key Features:**
- ✅ **URL Support**: Paste full Google Drive URLs (Docs, Sheets, Slides, Drive files)
- ✅ **Native Markdown Export**: Uses Google's native markdown with formatting (headings, tables, links, bold, italic)
- ✅ **Sheets CSV Export**: Export Google Sheets as CSV files (one file per sheet, with rate limit handling)
- ✅ **Multi-tab Support**: Export each tab as a separate file with `--all-tabs`
- ✅ **Detailed Info**: View permissions, sharing, capabilities, document tabs, and heading structure
- ✅ **Comments**: View all comments and replies with quoted text, authors, and timestamps
- ✅ **Auto-naming**: Exported files use document title and `.exported.md` extension (auto-ignored by git)

**Examples:**
```bash
# List recent files (default 20, sorted by modified date)
uv run gcmd list

# List only Google Docs
uv run gcmd list -t docs

# Search for files by name or content
uv run gcmd list -q "project report"

# List with verbose details
uv run gcmd list -v -n 10

# Show basic file metadata (using URL)
uv run gcmd info "https://docs.google.com/document/d/1abc123xyz/edit"

# Show detailed info with permissions, tabs, structure, and comments
uv run gcmd info -v "https://docs.google.com/document/d/1abc123xyz/edit?tab=t.0"

# Show only comments (without other verbose details)
uv run gcmd info --show-comments "https://docs.google.com/document/d/1abc123xyz/edit"

# Export Google Doc with document title as filename
uv run gcmd export "https://docs.google.com/document/d/1abc123xyz/edit"
# Creates: Document Title.exported.md

# Export all tabs as separate files
uv run gcmd export --all-tabs "https://docs.google.com/document/d/1abc123xyz/edit"
# Creates: Document Title - Tab1.exported.md, Document Title - Tab2.exported.md, etc.

# Export to specific file
uv run gcmd export 1abc123xyz -o document.md

# Export Google Sheet as CSV (creates directory with one CSV per sheet)
uv run gcmd export "https://docs.google.com/spreadsheets/d/1abc123xyz/edit"
# Creates: Spreadsheet Title/ directory with Sheet1.csv, Sheet2.csv, etc.

# Export Sheet to specific directory
uv run gcmd export "https://docs.google.com/spreadsheets/d/1abc123xyz/edit" -o ~/exports/

# Download a regular file
uv run gcmd download "https://drive.google.com/file/d/1abc123xyz/view" -o ~/Downloads/
```

**Note:** All Drive commands accept Google Drive URLs or file IDs. URLs can include tabs, fragments, and query parameters.

**Tasks Examples:**
```bash
# List tasks from your default task list
uv run gcmd tasks

# List tasks with detailed information
uv run gcmd tasks -v

# Include completed tasks
uv run gcmd tasks -c

# List all your task lists
uv run gcmd tasks --list-all-lists

# List tasks from a specific task list
uv run gcmd tasks -l "your-task-list-id"

# Limit number of results
uv run gcmd tasks -n 50
```

## Proposed Agents and Workflows

These are candidate subcommands we can design and prioritize. We'll refine flags, outputs, and invariants as we implement.

- Files
  - ~~`list`: list files/folders (filters by name, type, owner, shared-with)~~ ✅ **DONE**
  - ~~`search <query>`: search by name or full-text~~ ✅ **DONE** (integrated into list -q)
  - ~~`info <file-id>`: show metadata and permissions~~ ✅ **DONE**
- Transfer
  - `upload <src> [--dest <folder>] [--mime <type>] [--recursive]`
  - ~~`download <file-id> [--dest <dir>]`: download a file~~ ✅ **DONE**
  - `sync <src> <drive-folder>`: one-way sync with include/exclude patterns
- Sharing & Org
  - `share <file-id|path> --user <email> --role <reader|writer|commenter>`
  - `unshare <file-id|path> [--user <email>]`
  - `move <file-id|path> --dest <folder>`
  - `trash <file-id|path>` and `restore <file-id>`
- Docs/Sheets Exports
  - ~~`export <doc-id> --format md`: export Google Doc as markdown~~ ✅ **DONE** (uses Google's native markdown export)
  - ~~`export <doc-id> --all-tabs`: export multi-tab documents~~ ✅ **DONE**
  - ~~`export <sheet-id>`: export Google Sheets as CSV~~ ✅ **DONE** (auto-detects Sheets, exports one CSV per sheet)
  - `export <doc-id> --format pdf|html`: additional export formats
  - `export <sheet-id> --format xlsx`: export Google Sheets as Excel
- Administration
  - `perm-audit [--folder <id|path>] [--recursive]` summarize external shares
  - `quota` view usage by owner, mime-type, folder
- Tasks
  - ~~`tasks [-l list-id] [-n max] [-c]`: list tasks from Google Tasks~~ ✅ **DONE**
  - `task-create <title> [--notes <notes>] [--due <date>]`: create a new task
  - `task-update <task-id> [--title <title>] [--status <status>]`: update a task
  - `task-delete <task-id>`: delete a task

## Auth & Configuration

### Current Implementation ✅

OAuth user authentication with browser-based flow:
- Credentials file: `~/.config/gcmd/credentials.json` (OAuth client ID from Google Cloud Console)
- Token cache: `~/.config/gcmd/token.json` (auto-generated after first auth)
- Scopes: Drive readonly, Sheets readonly, file access, metadata, and Tasks readonly

### Future Plans

Service Account support and additional configuration:
1. Flags: `--auth oauth|service`, explicit project/env selectors
2. Environment variables and `.env` (optional)
3. Config file: `~/.config/gcmd/config.toml`

Secrets (tokens, refresh tokens, service account keys) are stored securely; never commit them.

## Conventions

- Execution: prefer `uv run gcmd ...` for local development
- Console name: `gcmd`, package: `gcmd`
- Output: default human-readable; `--json` to emit structured JSON (planned)
- Exit codes: non-zero on errors; subcommands return actionable messages
- Logging: `--verbose` for detailed output; `--version` implemented
- File naming: exported Docs use `.exported.md` extension (auto-ignored by git); Sheets export to CSV files in a named directory
- URL support: all commands accept full Google Drive URLs or file IDs

## Roadmap

1. ✅ Bootstrap CLI
2. ✅ Implement OAuth flow with browser authentication
3. ✅ Add `info`, `download`, and `export` commands
4. ✅ Add `list` and `search` commands
5. ✅ URL support for all commands (accept full Google Drive URLs)
6. ✅ Native markdown export with full formatting
7. ✅ Multi-tab document support (view tabs, export individually)
8. ✅ Detailed file info (permissions, sharing, capabilities, structure)
9. ✅ Google Tasks integration (`tasks` command)
10. ✅ Google Sheets CSV export (auto-detection, one CSV per sheet)
11. ⏭️ Add `upload` command
12. ⏭️ Add `share`/`perm-audit` with safety rails
13. ⏭️ JSON output mode (`--json`)
14. ⏭️ Google Sheets Excel export
15. ⏭️ Additional export formats (PDF, HTML)
16. ⏭️ Task create/update/delete operations

## Notes

- For design discussions, capture decisions here with rationale and examples
- Keep examples copy-pastable and tested regularly
