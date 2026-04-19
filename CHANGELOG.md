# Changelog

## 0.0.1 — 2026-04-19

### Added
- Initial project scaffolding with `uv` and SQLModel + SQLite
- Memory model with `Scope` (global / agent) and `Layer` (hot / cold)
- Strategy pattern for memory reads and rebuild triggers
- `MaxN` strategy as the default implementation
- Pytest test suite with session fixture and seed helpers
- CI workflow with coverage threshold (50% minimum)
- PyPI publish workflow triggered by GitHub releases
