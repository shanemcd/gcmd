# Claude Context for gcmd

This file provides context for Claude when working on the `gcmd` project.

## Important Context Files

@AGENTS.md - **READ THIS FIRST** - Contains CLI commands, workflows, conventions, and complete roadmap

## Quick Reference

- **Run CLI**: `uv run gcmd [command]`
- **Package**: `gcmd` (no underscore)
- **Console script**: `gcmd` (no hyphen)
- **Entry point**: `gcmd.cli:main`

## Development Guidelines

- Use `uv run` for local development
- Keep AGENTS.md updated as features are added
- Follow all conventions outlined in AGENTS.md
- Test commands after implementing them
- Exported files use `.exported.md` extension (auto-ignored by git)
- Never commit credentials, tokens, or downloaded files

