# DCG (Destructive Command Guard) Rules

DCG provides pre-execution safety by blocking dangerous commands before they run.

## Installation

DCG should be installed via the base ACFS installation:
```bash
dcg install
dcg doctor  # Verify installation
```

## Default Packs

DCG comes with two core packs enabled by default:

- `core.filesystem` - Protects against destructive file operations (rm -rf, etc.)
- `core.git` - Protects against destructive git operations (force push, hard reset, etc.)

## Recommended Configuration

Create `~/.config/dcg/config.toml`:

```toml
# DCG Configuration
# Enable additional packs based on your workflow

[packs]
# Core (enabled by default)
core.filesystem = true
core.git = true

# Enable strict git rules for production repos
# strict_git = true

# Database protection (enable if using databases)
# database.postgresql = true
# database.mysql = true

# Cloud protection (enable if using cloud CLIs)
# cloud.aws = true
# cloud.gcp = true
# cloud.azure = true

# Container protection
# containers.docker = true
# containers.compose = true
```

## Common Commands

```bash
# Test if a command would be blocked
dcg test 'rm -rf /'

# Test with explanation
dcg test 'git push --force' --explain

# List available packs
dcg packs

# One-time bypass (use with caution)
dcg allow-once <code>

# Health check
dcg doctor
```

## Integration with ACFS

DCG integrates with Claude Code via a PreToolUse hook. When installed, it automatically intercepts dangerous commands before they execute.

The hook is registered in `~/.claude/settings.json` or per-project in `.claude/settings.local.json`.
