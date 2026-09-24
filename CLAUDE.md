# CLAUDE.md

## Repository state

No build system or test suite yet. Contents:

- `free-ai-bible/` — vendored snapshot of
  https://github.com/abbosaliboev/free-ai-bible (MIT). Markdown directory of
  free AI APIs plus small Python templates (`templates/`) and setup scripts
  (`scripts/`). Provenance in `free-ai-bible/SOURCE.md`; do not edit as if
  it were original work — re-sync from upstream instead.

## Local environment note

The `gstack` skill suite (https://github.com/garrytan/gstack) was installed
into `~/.claude/skills/gstack` for Claude Code in this session. That install
is local to the agent environment, not part of this repository — it is not
tracked here and should not be assumed present in other checkouts or CI.
