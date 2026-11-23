# CLAUDE.md — Data Center Policy Tracker

A static, sourced public record of data-center policy in the US and selected
countries: the White House Ratepayer Protection Pledge and where it shows up
at sites, local moratoriums, laws/orders/rules, community benefit agreements,
utility large-load tariffs and rate cases, elections, operators' published
commitments, and the sites themselves. GitHub Pages serves `docs/`; there is
no runtime backend.

This file is loaded on every session, so it holds only what applies to most
changes. Detail lives in the companions below — load the one whose trigger
matches before you start. Everything here and there is a recommendation the
owner can override, not a hard rule; the owner's word in chat wins.

## Load before…

| Before you… | Read |
|---|---|
| change a view, navigation, Home, typography, sub-tabs, accordions, modals, maps | [notes/agent/interface.md](notes/agent/interface.md) + [DESIGN.md](DESIGN.md) |
| add or edit records (companies, claims, projects, moratoriums, tariffs, rate cases, policies, signatories, international, elections) | [notes/agent/data-rules.md](notes/agent/data-rules.md) |
| write a guard test, a checker, an e2e test, or review/merge a PR | [notes/agent/lessons.md](notes/agent/lessons.md) |
| run a data refresh, validation pass or research run | [notes/agent/refresh.md](notes/agent/refresh.md), [REFRESH.md](REFRESH.md), `.claude/skills/daily-refresh/` |
| want the generic coding-best-practices rules this repo started from | [notes/agent/principles.md](notes/agent/principles.md) |
| work as an agent in this repo (commands, review loop) | [AGENTS.md](AGENTS.md) |

Those files were moved out of this one verbatim on 2026-11-23; references
elsewhere to "CLAUDE.md > <section>" now resolve there.

## Interface direction (owner, 2026-11-21; Home ledger 2026-11-23)

- Off-white paper, graphite ink, one deep blue accent; one system sans family.
  Status colours carry meaning only (enacted/approved green, pending amber,
  failed/rejected red). No gradients, photography, ornamental charts,
  oversized heroes, shadows or rounded "cards" as decoration.
- **No eyebrows.** Nothing small and labelly sits above a heading — a record's
  kind, operator or place goes on a meta line under the title.
  `test_no_eyebrow_labels_on_home` covers Home; hold every view to it.
- **No over-explaining.** A plain heading and the data. Keep a sentence only
  when it changes what the reader understands (a promise vs an obligation,
  adoption vs effectiveness, a cohort boundary). "Conference postponed."
  "Source." "No date announced."
- One navigation row: Overview, the nine record tabs, then Updates, Compare
  and Plans at the end. Labels are identical everywhere a tab is named (tab,
  Home row, heading, llms.txt).
- Home is a ledger: search, then five top lines (The Pledge, Moratoriums,
  Community benefits, Policy, Power Costs), each a large tabular figure, one
  status sentence and the newest or next dated item; then Latest / Coming up.
  The figures come from `toplines` in `data/home.json` (built by
  `refresh.py::_build_toplines`) under the same rule the tab uses, and
  `test_home_card_numbers_match_their_tab` checks that.
- Character comes from the ink rules (3px page rule, 2px above a ledger),
  large tabular figures and two data marks (assessed pledge sites by status;
  moratoriums enacted per month). Add a mark only when it carries a number
  the reader needs.
- Every tab opens on its own top line (a stat row or a status sentence)
  before any control.
- Exact quotations, visible sources, explicit unknowns ("Not stated"),
  curator-owned judgments, consistent terms, accessibility and stable links
  are mandatory.

## Interaction cost is measured

`python3 tools/interaction_cost.py` walks reader tasks from a cold Home on
mobile, tablet and desktop, counting taps, swipes, side-swipes and typed
queries, grouped into reader journeys (`JOURNEYS`), and reports which Home
top lines are visible on the first screen. Results go to
`uat/interaction_costs.json`; budgets in `uat/interaction_budgets.json` are
enforced by `tests/e2e/test_interaction_cost.py`. Lower a budget when a path
gets cheaper; raise one only with a note in `uat.md`. Run it after any layout
or navigation change and report the before/after in the PR.

## Editorial and sourcing (load-bearing)

- **Quote, don't paraphrase.** `Claim.statement` and `Policy.key_terms` are
  verbatim from `source_url`. A news paraphrase without quotation marks is not
  first-party; skip it. Full first-party rules: data-rules.md.
- **Every record has a source URL and a capture date.** A live link is not a
  verified claim: fetch the exact page and confirm the words are there
  (`scripts/probe.py --evidence`). A search tool's synthesis is not a source.
- **A homepage citation proves nothing.** Bulk-generated records with real
  bill numbers and invented narratives have shipped before; one fetch of the
  legislature's or docket's own page catches them.
- **A headline's strong word is not the legal action** ("ban", "moratorium").
  Look for the jurisdiction's own statement.
- **Judgments are curated, never classified by a model**: stance, delivered
  status, ratepayer status, agreement features. Absence means "not yet
  assessed", never an implied grade.
- **No scores or trust indexes.** Show the data; let readers judge.
- **Event dates are not capture dates.** Refreshes are not news.
- **Append-only.** Fix or remove a wrong record; don't just swap its URL.

## Architecture

- `schema.py` is the contract (Pydantic, `extra="forbid"`). Edit
  `data/seed/*.json`, then `python3 refresh.py`, which validates,
  cross-references and writes `docs/data/*.json` plus the `.preview.js`
  adapters, `home.json`, `links.json`, `llms.txt` and `sitemap.xml`. Never
  hand-edit `docs/data/` or `ISSUES.md` (generated).
- Frozen vocabularies are mirrored Python ↔ `docs/app.js` and parity-tested
  (THEMES, statuses, pledge principles, tariff elements, agreement features,
  record kinds…). Adding a value is a BACKLOG entry plus both mirrors.
- **Derive, don't list.** A hand-written list beside the registry it mirrors
  rots silently, worst inside tests meant to catch drift. Iterate the
  registry (`refresh.PAYLOAD_FILES`, `VIEWS`, `SUBTAB_GROUPS`).
- First paint is index.html, styles.css, app.js, companies.json and
  home.json. Every other payload is lazy per view and promise-memoized
  (`let _xPromise`). `tests/test_perf_budget.py` gates it: make a payload
  lazy rather than raising the ceiling.
- Colours are CSS tokens with literal values in both `:root` and
  `[data-theme="dark"]`; sizes are the `--fs-*` scale
  (`tests/test_type_scale.py`). JS never hard-codes a colour.
- The `[hidden]` trap: any `display:` rule on an element toggled with
  `hidden` needs the global `[hidden] { display: none !important }`.
- Deep links: every view has a hash, every record a URL (`RECORD_ROUTES`).
  Read sub-keys from the hash before `activateView` (it rewrites the hash).
  Nothing may push or replace history while `state._routing` is set.

## Working here

- Python: `../../../.venv/bin/python` from a worktree (system Python 3.9 needs
  `eval_type_backport`). Unit tests: `python -m pytest --ignore=tests/e2e -n 4`.
  E2E: `python -m pytest tests/e2e -n 4` (~80 s). Run both before a PR.
- Preview: `python3 tools/build_preview.py --verify` → `.preview/dashboard.html`.
  Headless screenshots at 390×844 and 1366×900 settle a UI change.
- Tests that wait on content inside a closed `<details>` or a hidden sub-tab
  need `state="attached"`, or click the disclosure first.
- Before adding a CDN asset, dependency or Action, scan the advisory feed at
  https://pranava0x0.github.io/vibe-coding-security/llms-ctx.txt. Keep SRI on
  every third-party script (html2pdf, Leaflet).
- Bugs and fixes go in commit messages; leads and deferred work in
  `BACKLOG.md`; reusable lessons in the matching companion file.
- Attribution: AI involvement is disclosed in plain text in each commit body
  and PR description ("Models and agents: …"). Never a `Co-Authored-By` AI
  trailer or a tool-branded footer (owner's global rule).
