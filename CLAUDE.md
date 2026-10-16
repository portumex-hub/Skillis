# CLAUDE.md

## Repository state

`portumex-hub/Skillis` holds Claude Code skills for the owner's projects. There
is no application code, build system, or test suite yet.

## Instagram agent skills

`.claude/skills/ig-*` is a vendored copy of
https://github.com/Jakeschincariol/instagram-agent-skill (MIT, commit
`d03c56b`, license in `.claude/skills/LICENSE-instagram-agent-skill`). They load
automatically as project skills (`/ig-reel`, `/ig-caption`, `/ig-viral`, ...).
To update, re-copy `skills/ig-*` from upstream and bump the commit above.

The skills look for the user's voice file at `~/.claude/instagram/voice.md`.
The repo copy lives at `.claude/instagram/voice.md`; when that home path is
missing (e.g. a fresh cloud session), read the repo copy instead.

The Python helpers are stdlib-only text tools. `/ig-viral` also needs `yt-dlp`,
which is not installed by default.

## Local environment note

The `gstack` skill suite (https://github.com/garrytan/gstack) was installed
into `~/.claude/skills/gstack` for Claude Code in an earlier session. That
install is local to the agent environment, not part of this repository — it is
not tracked here and should not be assumed present in other checkouts or CI.
