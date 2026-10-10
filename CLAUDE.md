@AGENTS.md

## Claude Code specifics
- Skills installed as a plugin are namespaced under universal-modder.
- FAL MCP is disabled in this fork; .mcp.json has no provider credentials.
- A SessionStart hook puts um on PATH. In a clone, .claude/settings.json adds
  the same PATH hook, and .claude/skills mirrors skills/.
- Image work uses the disposable-vision skill and its authenticated Codex worker.
