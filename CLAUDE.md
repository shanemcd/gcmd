# Claude Context for gdrive-utils

This file provides context for Claude when working on the `gdrive-utils` project.

## Project Overview

`gdrive-utils` is a Python CLI tool for working with Google Drive. It provides utilities for file management, uploads, downloads, sharing, and administrative tasks.

## Important Context Files

@AGENTS.md - Contains CLI commands, workflows, conventions, and roadmap

## Quick Reference

- **Run CLI**: `uv run gdrive-utils [command]`
- **Package**: `gdrive_utils` (underscore)
- **Console script**: `gdrive-utils` (hyphen)
- **Entry point**: `gdrive_utils.cli:main`

## Development

- Use `uv run` for local development
- Keep AGENTS.md updated as features are added
- Follow the conventions outlined in AGENTS.md
- Test commands after implementing them

## Key Principles

1. Default to human-readable output, support `--json` for structured data
2. Exit with non-zero codes on errors
3. Support both OAuth and Service Account authentication
4. Store secrets securely (never in version control)
5. Provide clear error messages and help text

