# Claude Context for gdrive-utils

This file provides context for Claude when working on the `gdrive-utils` project.

## Important Context Files

@AGENTS.md - **READ THIS FIRST** - Contains CLI commands, workflows, conventions, and complete roadmap

## Quick Reference

- **Run CLI**: `uv run gdrive-utils [command]`
- **Package**: `gdrive_utils` (underscore)
- **Console script**: `gdrive-utils` (hyphen)
- **Entry point**: `gdrive_utils.cli:main`

## Development Guidelines

- Use `uv run` for local development
- Keep AGENTS.md updated as features are added
- Follow all conventions outlined in AGENTS.md
- Test commands after implementing them
- Exported files use `.exported.md` extension (auto-ignored by git)
- Never commit credentials, tokens, or downloaded files

