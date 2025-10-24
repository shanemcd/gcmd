# gcmd

A Python CLI tool for working with Google services. Download files, export Google Docs as markdown, manage your Drive files, and more from the command line.

## Features

- 🔐 **OAuth authentication** with browser-based login
- 📄 **Export Google Docs** as markdown with full formatting (headings, tables, links, bold, italic)
- 📑 **Multi-tab support** - export each tab as a separate file
- 🔍 **Search and list** files with filtering by type and query
- 📊 **Detailed file info** - view metadata, permissions, sharing, document structure, tabs, and comments
- 💬 **Comments access** - view all comments and replies with quoted text and timestamps
- 💾 **Download files** from Google Drive
- 🔗 **URL support** - paste full Google Drive URLs instead of file IDs
- 🚀 **Fast and easy to use**

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/shanemcd/gcmd.git
cd gcmd

# Run with uv (no installation needed)
uv run gcmd --help
```

## Setup

Before using Drive commands, you need to set up OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the **Google Drive API** and **Google Docs API**
4. Create **OAuth 2.0 Client ID** credentials (Desktop app type)
5. Download the JSON credentials file
6. Save it to `~/.config/gcmd/credentials.json`

On first use, the CLI will open your browser to authenticate. Credentials are cached in `~/.config/gcmd/token.json`.

## Usage

### List and Search Files

```bash
# List recent files (default 20, sorted by modified date)
uv run gcmd list

# List only Google Docs
uv run gcmd list -t docs

# Search for files by name or content
uv run gcmd list -q "project report"

# List with verbose details
uv run gcmd list -v -n 10

# List only folders
uv run gcmd list -t folders
```

### Export Google Docs as Markdown

Google Docs are exported using Google's native markdown export, preserving formatting like headings, tables, links, bold, and italic text.

```bash
# Export with document title as filename (recommended)
uv run gcmd export "https://docs.google.com/document/d/1abc123xyz/edit"
# Creates: Document Title.exported.md

# Export all tabs as separate files
uv run gcmd export --all-tabs "https://docs.google.com/document/d/1abc123xyz/edit"
# Creates: Document Title - Tab1.exported.md, Document Title - Tab2.exported.md, etc.

# Export to specific file
uv run gcmd export 1abc123xyz -o document.md

# Export to directory (uses document title)
uv run gcmd export 1abc123xyz -o ~/Documents/

# Export all tabs to specific directory
uv run gcmd export --all-tabs 1abc123xyz -o ~/Documents/
```

**Note:** Files with `.exported.md` extension are automatically ignored by git (see `.gitignore`).

### Download Files

```bash
# Download to current directory
uv run gcmd download 1abc123xyz

# Download to specific path
uv run gcmd download 1abc123xyz -o ~/Downloads/myfile.pdf
```

### View File Info

View detailed information including metadata, permissions, sharing status, document structure, and comments.

```bash
# Basic info
uv run gcmd info "https://docs.google.com/document/d/1abc123xyz/edit"

# Detailed info with permissions, capabilities, tabs, structure, and comments
uv run gcmd info -v "https://docs.google.com/document/d/1abc123xyz/edit"

# Show only comments and replies
uv run gcmd info --show-comments "https://docs.google.com/document/d/1abc123xyz/edit"
```

The verbose output shows:
- File metadata (name, type, size, dates)
- Owner and last modifier
- All permissions (users, groups, domains, public links)
- Your capabilities (can edit, comment, share, download, etc.)
- Document tabs (for multi-tab Google Docs)
- Document outline with all headings
- Comments and replies with quoted text and timestamps

### URL Support

You can use full Google Drive URLs instead of file IDs:

```bash
# Any of these formats work:
uv run gcmd info "https://docs.google.com/document/d/1abc123xyz/edit"
uv run gcmd info "https://docs.google.com/document/d/1abc123xyz/edit?tab=t.0"
uv run gcmd info "https://drive.google.com/file/d/1abc123xyz/view"
uv run gcmd info "1abc123xyz"  # Or just the ID
```

## Commands

- `list [-q query] [-t type] [-n max] [-v]` - List and search files in Google Drive
- `info <file-id-or-url> [-v] [--show-comments]` - Show file metadata, permissions, structure, and comments
- `export <file-id-or-url> [-o output] [--all-tabs]` - Export Google Doc as markdown
- `download <file-id-or-url> [-o output]` - Download a file from Google Drive

**All commands support:**
- Full Google Drive URLs (Docs, Sheets, Slides, Drive files)
- File IDs extracted from URLs
- Plain file IDs

**Info command options:**
- `-v, --verbose` - Show detailed info including permissions, tabs, structure, and comments
- `--show-comments` - Show only comments (without other verbose details)

## Development

See [AGENTS.md](AGENTS.md) for detailed documentation on commands, workflows, and roadmap.

See [CLAUDE.md](CLAUDE.md) for context when working with Claude AI.

## License

MIT

