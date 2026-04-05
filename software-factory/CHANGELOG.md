# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Claude Code-like interface with full filesystem access
- Directory navigation commands (`/cd`, `/pwd`)
- Automatic backup system before file edits
- Unlimited undo/redo functionality
- Smart intent detection for clarifying questions
- Interactive file editing with diff preview
- Multi-agent workflow (Architect → Developer → Auditor)
- Semantic caching with ChromaDB
- Cost tracking and governance
- Comprehensive CLI with slash commands

### Changed
- Removed Docker dependency for local execution
- Enhanced file manager to work in any directory
- Improved error handling and graceful degradation
- Updated documentation structure

### Fixed
- Cache corruption issues with response validation
- Windows path resolution for subprocess execution
- Infinite retry loops with recursion limits
- Intent detection for casual conversation

## [1.0.0] - 2026-04-05

### Initial Release
- Basic multi-agent architecture
- OpenRouter integration
- Vector memory with ChromaDB
- Sandboxed code execution
- Interactive CLI interface

---

## Version History

- **1.0.0** (2026-04-05) - Initial release with core features
- **Unreleased** - Major enhancements for Claude Code-like experience
