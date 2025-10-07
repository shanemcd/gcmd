# gdrive-utils

A Python CLI tool for working with Google Drive. Download files, export Google Docs as markdown, and manage your Drive files from the command line.

## Features

- 🔐 OAuth authentication with browser-based login
- 📄 Export Google Docs as markdown
- 💾 Download files from Google Drive
- 📊 View file metadata
- 🚀 Fast and easy to use

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/shanemcd/gdrive-utils.git
cd gdrive-utils

# Run with uv (no installation needed)
uv run gdrive-utils --help
```

## Setup

Before using Drive commands, you need to set up OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the **Google Drive API** and **Google Docs API**
4. Create **OAuth 2.0 Client ID** credentials (Desktop app type)
5. Download the JSON credentials file
6. Save it to `~/.config/gdrive-utils/credentials.json`

On first use, the CLI will open your browser to authenticate. Credentials are cached in `~/.config/gdrive-utils/token.json`.

## Usage

### List and Search Files

```bash
# List recent files (default 20, sorted by modified date)
uv run gdrive-utils list

# List only Google Docs
uv run gdrive-utils list -t docs

# Search for files by name or content
uv run gdrive-utils list -q "project report"

# List with verbose details
uv run gdrive-utils list -v -n 10

# List only folders
uv run gdrive-utils list -t folders
```

### Export Google Doc as Markdown

```bash
# Export to stdout
uv run gdrive-utils export 1abc123xyz

# Export to file
uv run gdrive-utils export 1abc123xyz -o document.md

# Export to directory (uses original filename)
uv run gdrive-utils export 1abc123xyz -o ~/Documents/
```

### Download Files

```bash
# Download to current directory
uv run gdrive-utils download 1abc123xyz

# Download to specific path
uv run gdrive-utils download 1abc123xyz -o ~/Downloads/myfile.pdf
```

### View File Info

```bash
uv run gdrive-utils info 1abc123xyz
```

### Finding File IDs

File IDs are in the URL when you open a file in Google Drive:

```
https://docs.google.com/document/d/1abc123xyz/edit
                                   ^^^^^^^^^^
                                   This is the file ID
```

## Commands

- `list [-q query] [-t type] [-n max] [-v]` - List and search files
- `info <file-id>` - Show file metadata
- `export <file-id> [-o output]` - Export Google Doc as markdown
- `download <file-id> [-o output]` - Download a file
- `hello [name]` - Simple test command

## Development

See [AGENTS.md](AGENTS.md) for detailed documentation on commands, workflows, and roadmap.

See [CLAUDE.md](CLAUDE.md) for context when working with Claude AI.

## License

MIT

