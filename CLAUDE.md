# CLAUDE.md

## Repository state

Early-stage repo. Current contents:

- `requirements.txt` — Python deps. The Outscraper SDK is installed from the
  official repo (`outscraper/outscraper-python`), pinned to tag `v6.0.5`.
- `scripts/google_reviews.py` — pulls Google Maps reviews via Outscraper and
  writes them to `output/reviews.csv` (gitignored).
- `scripts/prospect_pipeline.py` — F&B prospecting: Outscraper search + reviews
  (optional website contacts) → Claude (`claude-opus-5-5`, structured output) scores
  each place 0–100 against `prospecting/icp.md` / `prospecting/oferta.md` and drafts
  a first message → approval-queue CSV in `output/`. It never sends anything.
- `scripts/export_approved.py` — exports only rows marked `aprobado = si`, split into
  an Instantly/Lemlist email CSV and a manual-send list.
- `prospecting/make_scenario.md` — the same flow as two Make scenarios
  (draft, then send-approved).
- `.env.example` — required env vars. Real API keys must never
  be committed; set them as environment secrets.

Setup:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

No test suite yet. Hard rule from the owner: no prospect message is sent without
their explicit approval — keep the approval gate in any new sending path.
Outscraper bills per returned record — keep `--limit` low
when testing.

## Local environment note

The `gstack` skill suite (https://github.com/garrytan/gstack) was installed
into `~/.claude/skills/gstack` for Claude Code in an earlier session. That
install is local to the agent environment, not part of this repository — it is
not tracked here and should not be assumed present in other checkouts or CI.
