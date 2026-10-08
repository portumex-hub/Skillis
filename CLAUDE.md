# CLAUDE.md

## Repository state

Early-stage repo. Current contents:

- `requirements.txt` — Python deps. The Outscraper SDK is installed from the
  official repo (`outscraper/outscraper-python`), pinned to tag `v6.0.5`.
- `scripts/google_reviews.py` — pulls Google Maps reviews via Outscraper and
  writes them to `output/reviews.csv` (gitignored).
- `.env.example` — required env vars. The real `OUTSCRAPER_API_KEY` must never
  be committed; set it as an environment secret.

Setup:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

No test suite yet. Outscraper bills per returned record — keep `--limit` low
when testing.

## Local environment note

The `gstack` skill suite (https://github.com/garrytan/gstack) was installed
into `~/.claude/skills/gstack` for Claude Code in an earlier session. That
install is local to the agent environment, not part of this repository — it is
not tracked here and should not be assumed present in other checkouts or CI.
