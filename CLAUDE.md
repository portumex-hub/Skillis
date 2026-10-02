# CLAUDE.md

## Repository state

`portumex-hub/Skillis` holds design deliverables for the Divino Peccato
restaurant project. No build system or test suite.

- `menu/` — printable menu (Letter, 6 pages). `build_menu.py` reads final
  prices from column AC ("PVP final con IVA") of the `Mezcla de Ventas` sheet
  in the business-plan Excel and writes `divino_peccato_menu.html`; the PDF is
  rendered from that HTML with Playwright/Chromium. Styles in `menu.css`,
  fonts (Fraunces, Jost — OFL) in `menu/fonts/`.
  Rebuild: `pip install openpyxl && python3 menu/build_menu.py <excel.xlsx> menu/logo_divino_peccato.png`

## Local environment note

The `gstack` skill suite (https://github.com/garrytan/gstack) was installed
into `~/.claude/skills/gstack` for Claude Code in this session. That install
is local to the agent environment, not part of this repository — it is not
tracked here and should not be assumed present in other checkouts or CI.
