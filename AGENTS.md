# gdrive-utils Agents

This document tracks the CLI agents, workflows, and conventions for `gdrive-utils`. We'll iterate here as features land.

## Quickstart

- Run help:
  - `uv run gdrive-utils --help`
- Run a sample command:
  - `uv run gdrive-utils hello Shane`

## Authentication Setup

Before using Drive commands, you need to set up OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the Google Drive API and Google Docs API
4. Create OAuth 2.0 Client ID credentials (Desktop app type)
5. Download the JSON credentials file
6. Save it to `~/.config/gdrive-utils/credentials.json`

On first use, the CLI will open your browser to authenticate. Credentials are cached in `~/.config/gdrive-utils/token.json`.

## Current Commands

### Basic Commands
- `hello [name]`: simple smoke test to verify the CLI wiring and environment

### File Operations
- `list [-q query] [-t type] [-n max] [-v]`: list and search files in Google Drive
- `info <file-id>`: show metadata for a Google Drive file
- `download <file-id> [-o output]`: download a file from Google Drive
- `export <file-id> [-o output]`: export a Google Doc as markdown (text format)

**Examples:**
```bash
# List recent files (default 20, sorted by modified date)
uv run gdrive-utils list

# List only Google Docs
uv run gdrive-utils list -t docs

# Search for files by name or content
uv run gdrive-utils list -q "project report"

# List with verbose details
uv run gdrive-utils list -v -n 10

# Show file metadata
uv run gdrive-utils info 1abc123xyz

# Export a Google Doc to markdown (stdout)
uv run gdrive-utils export 1abc123xyz

# Export a Google Doc to a file
uv run gdrive-utils export 1abc123xyz -o document.md

# Download a regular file
uv run gdrive-utils download 1abc123xyz -o ~/Downloads/
```

**Note:** To get a file ID, open the file in Google Drive and copy the ID from the URL:
`https://docs.google.com/document/d/FILE_ID_HERE/edit`

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
  - ~~`export <doc-id> --format md`: export Google Doc as markdown~~ ✅ **DONE** (currently text/plain)
  - `export <doc-id> --format pdf|html`: additional export formats
  - Enhanced markdown export with better formatting
- Administration
  - `perm-audit [--folder <id|path>] [--recursive]` summarize external shares
  - `quota` view usage by owner, mime-type, folder

## Auth & Configuration

### Current Implementation ✅

OAuth user authentication with browser-based flow:
- Credentials file: `~/.config/gdrive-utils/credentials.json` (OAuth client ID from Google Cloud Console)
- Token cache: `~/.config/gdrive-utils/token.json` (auto-generated after first auth)
- Scopes: Drive readonly, file access, and metadata

### Future Plans

Service Account support and additional configuration:
1. Flags: `--auth oauth|service`, explicit project/env selectors
2. Environment variables and `.env` (optional)
3. Config file: `~/.config/gdrive-utils/config.toml`

Secrets (tokens, refresh tokens, service account keys) are stored securely; never commit them.

## Conventions

- Execution: prefer `uv run gdrive-utils ...` for local development
- Console name: `gdrive-utils`, package: `gdrive_utils`
- Output: default human-readable; `--json` to emit structured JSON
- Exit codes: non-zero on errors; subcommands return actionable messages
- Logging: `--verbose`/`--quiet` planned; `--version` implemented

## Roadmap

1. ✅ Bootstrap CLI
2. ✅ Implement OAuth flow with browser authentication
3. ✅ Add `info`, `download`, and `export` commands
4. 🚧 Test with real Google Drive files
5. ⏭️ Add `list` and `search` commands
6. ⏭️ Add `upload` command
7. ⏭️ Enhanced markdown export with better formatting
8. ⏭️ Add `share`/`perm-audit` with safety rails

## Notes

- For design discussions, capture decisions here with rationale and examples
- Keep examples copy-pastable and tested regularly
