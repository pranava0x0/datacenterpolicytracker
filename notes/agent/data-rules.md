# Data and editorial rules

Moved verbatim from CLAUDE.md on 2026-11-23. Read before adding or editing records: companies, claims, projects, moratoriums, tariffs, rate cases, policies, signatories, international records or elections.

## Project intent (v1.5+: blueprint framing)

Dashboard surfacing the **community-benefit commitments** major data-center operators have published — and how those commitments are playing out on the ground at real sites. Use it as a **blueprint of solutions** for future data-center projects: what's possible to ask for, what's working in practice, and where the gaps still are.

Two stakeholders:
- **Policymakers / community advocates** evaluating what to ask for in permit, tax-abatement, or PPA negotiations.
- **Researchers / journalists / project developers** comparing what's been offered + delivered across companies, looking for the playbook patterns to replicate.

**Editorial frame (v1.5).** Reframed from prior "neither hit piece nor puff piece" framing to a positive blueprint orientation: lead with the solutions/commitments being offered, treat on-the-ground feedback as case-study evidence ("here's what happened when X tried Y"), not as adversarial pushback. **Keep** all data including critical responses — they're load-bearing for "lessons learned" and showing where commitments fell short. **Don't** delete or hide negative-stance feedback; it's the field-evidence that makes the blueprint usable rather than aspirational. **Don't** soften verbatim quotes to make them sound nicer — quote-as-published is still the rule.

The earlier "neither hit piece nor puff piece" framing was load-bearing in v1.0–v1.4; v1.5 deliberately lets the framing slide toward solutions/blueprint while preserving the underlying data integrity. If a future contributor wants to revert to the strict balanced framing, the dataset supports it — only the hero copy + tab labels + summary verbiage need to change.

## Architectural intent

- **Static-first.** Connectors emit JSON to `docs/data/`; frontend is vanilla JS hosted on GitHub Pages; no runtime backend.
- **Single source of truth in [schema.py](../../schema.py).** Pydantic models with `extra="forbid"` so any drift in the curated JSON fails fast at refresh time, not at runtime in the browser.
- **Theme constants live in one place.** Currently `THEMES` in [schema.py](../../schema.py) (Python) + the `THEMES` constant in [docs/app.js](../../docs/app.js) (frontend). A test (`test_themes_match_frontend`) reads both and asserts they're identical so they can't drift silently. **Don't** add a theme to one without the other.
- **Two payloads, not one.** `companies.json` + `claims.json` (small — preloads on first paint for the comparison view). `projects.json` + `responses.json` (lazy-loads when the user opens the Project Explorer tab). Keeps first paint snappy; the project view is heavier because of the map and per-project detail rendering.
- **Map only on the project view.** **Don't** pull Leaflet's CSS/JS in on the comparison-only view. The frontend code-splits — the map module loads only when the Project Explorer tab is activated.
- **Color tokens are CSS-var-driven.** Per-company brand-adjacent color (NOT exact brand colors — we're not affiliated and don't want to imply endorsement), per-stance color (positive / mixed / negative) — single palette in `:root`, dark-mode override in `[data-theme="dark"]`. **Don't** hard-code colors in JS; read via `getComputedStyle()`.
- **No connector-side aggregation.** Connectors emit raw records; aggregation (claim counts per theme, project counts per company) happens at frontend ingest. Keeps the JSON close to source and lets the frontend re-aggregate as filters change.


## Companies in scope (v1.4)

**Eight original hyperscalers** (locked, `REQUIRED_HYPERSCALERS` in tests): Meta, Google, Microsoft, OpenAI, Anthropic, xAI, Oracle, Amazon (AWS).

**Non-hyperscaler entities** added when both gates are met: (1) the entity has announced a project at hyperscaler scale (≥1 GW), and (2) the entity publishes its own community-impact framing (so we have first-party claims to quote). Tracked entities:
- **Wonder Valley** (O'Leary Digital, Box Elder County UT) — added v1.1.
- **QTS** (Blackstone subsidiary) — added v1.4. The Cedar Rapids IA campus is the canonical "Ratepayer Protection Pledge" reference site (QTS pays 100% of its energy costs so grid upgrades don't shift to existing utility ratepayers); the Richmond VA campus (RIC5) is the first-ever data center to receive FAST-41 federal-permitting coverage. Both are first-party-substantive enough to clear the gates; v1.0–v1.3 had QTS on the explicit "out of scope" list, but v1.4 reverses that based on the substance of QTS's published commitments.
- **CoreWeave, Crusoe, Prologis** — added in the v2 expansion (see the Signatory registry section below); all three cleared the two-gate test as compute/colocation developers operating at hyperscaler scale.
- **SB Energy (SoftBank Group), Brookfield** — added 2026-07-30, tied to DOE's federal-land AI data center program (Portsmouth OH, Paducah KY respectively). Same two-gate test, same process. **NextEra Energy is deliberately NOT a separate slug** despite DOE/company releases naming it as the Paducah project's power-generation partner: DOE, Brookfield, and NextEra's own releases are explicit that Brookfield leases/develops/operates the data center while NextEra only builds/owns the paired generation. NextEra is independently a Ratepayer Pledge signatory (2026-07-23 expansion) and Brookfield is not — collapsing the two into one company record would let NextEra's signatory status bleed onto Brookfield's `ratepayer_pledge_signatory` flag. **The precedent for a multi-party consortium: track only the confirmed data-center developer/operator as the company; name power/utility partners in the `Project.notes`, not as additional company slugs.**
- **Amentum was considered for the same DOE federal-land program (Savannah River Site) and NOT added — a gate-2 lesson worth keeping.** It has an announced 1GW project (clears gate 1) and two first-party, named-executive quotes (Heller, Whitney) — enough material that it was added, then removed on review. Re-reading those quotes: both are about Amentum's engineering/nuclear-operations capability and national-security positioning, with zero community-impact content (no jobs figure, no ratepayer language, no environmental commitment, no engagement framing). **Having first-party quotes to attach is not the same as clearing gate 2** — the quotes have to actually be ABOUT community impact, not merely sourced from the company. Don't re-add Amentum on the strength of these two quotes alone; it needs either a standing community-impact page or a first-party statement that actually addresses jobs/tax/energy/water/grants/infrastructure/education/engagement for the host community.

The slugs (`wonder-valley`, `qts`, `crusoe`, `coreweave`, `prologis`, `sb-energy`, `brookfield`) live in `COMPANY_SLUGS` + the `CompanySlug` Literal in [schema.py](../../schema.py); `TestSeedCoverage.OPTIONAL_ENTITIES` in [tests/test_seed_data.py](../../tests/test_seed_data.py) is the test-side ledger. When adding a new non-hyperscaler entity:
1. Add the slug to all four locations above (schema Literal + COMPANY_SLUGS tuple, app.js COMPANY_SLUGS array, OPTIONAL_ENTITIES set).
2. Add a `--co-<slug>` CSS color in both light and dark `:root` blocks.
3. Add the company entry to `data/seed/companies.json` with a curated `summary`.
4. Before shipping: re-read every first-party quote you're about to attach and confirm it's actually ABOUT community impact (jobs, tax revenue, energy, water, community grants, infrastructure, education, or engagement) — not just sourced from the company. "We have quotes" and "gate 2 is cleared" are not the same claim (the Amentum lesson above).

Hyperscaler-adjacent colocation operators not yet tracked (Equinix, Digital Realty) remain **out of scope** unless they meet the same two-gate test. The QTS addition is the precedent for evaluating future operators; the SB Energy/Brookfield addition is the precedent for evaluating a DOE-adjacent or multi-party one; the Amentum non-addition is the precedent for what "clearing gate 2" actually requires.

## Source publication date vs capture date (v1.4)

`Claim.captured_at` is the date the **curator** recorded the claim. `Claim.published_at` (Optional, added v1.4) is the **source's** own publication date — the day the press release went out, the news article was filed, the FERC order was issued. Frontend displays `published_at` if present, falling back to `captured_at`. The two often differ by days or years (e.g., a Dec 2024 Meta press release captured in May 2026).

The merge script in `.agent_outputs/merge_v14.py` auto-extracts publication dates from URLs that include `/YYYY/MM/DD/` path segments — common shape for newsroom CMSes (news.microsoft.com, fox8live.com, bendbulletin.com, ppc.land, etc.). Agent-supplied `published_at` always wins over auto-extraction. **Don't** fabricate publication dates for evergreen company pages without one — leave `published_at` null and the curator's `captured_at` is what gets shown.

`CommunityResponse.date` is already the publication / event date by convention — no schema change needed there.

## `Project.at_a_glance` per-theme summary (v1.4)

Optional `dict[str, str]` field on `Project` mapping canonical theme keys (jobs, tax_revenue, energy, water, community_grants, infrastructure, education, engagement) to one-line plain-English phrases — e.g., `{"water": "Air-cooled, low water use", "jobs": "5,000 construction / 500 ops"}`. Surfaced in the project Overview tab's "At a glance" section.

When `at_a_glance` is **set** for a theme, the curator-written copy wins. When it's **not set**, the frontend auto-derives from the project's project-tied claims:
- If any claim for the theme has a structured `metric`, format the top 1–2 metrics joined by ` · `.
- Otherwise truncate the first claim's `statement` to ~90 chars.

Field validator in [schema.py](../../schema.py) rejects unknown theme keys at refresh time. **Don't** invent themes here that aren't in the canonical 8 — adding a theme is still a deliberate schema migration (CLAUDE.md > "Theme taxonomy"). The auto-derivation path means most projects need no manual `at_a_glance` work; reach for the override only when the auto-summary buries something important (e.g., a notable air-cooling design that the metrics don't surface).

## Theme taxonomy (frozen for v1)

A small fixed vocabulary every claim gets mapped to so the comparison view is meaningful:

1. **Jobs** — construction, operational, indirect/induced.
2. **Tax revenue** — local property/sales tax contributions, abatement framing.
3. **Energy** — renewable PPAs, efficiency claims, grid investment.
4. **Water** — usage, recycling, watershed restoration.
5. **Community grants** — direct philanthropy / community funds.
6. **Infrastructure** — roads, fiber, utilities investment beyond the site fence.
7. **Education** — STEM programs, scholarships, workforce training.
8. **Engagement** — community input during siting, transparency commitments.

Adding a 9th theme requires a [BACKLOG.md](../../BACKLOG.md) entry + migration of all existing claim records. **Don't** add a theme inline — the comparison view's value depends on a stable cross-company vocabulary; ad-hoc theme additions silently break the matrix narrative for older claims that pre-date the new theme.

## Data model

Four record types in [schema.py](../../schema.py), all with required `source_url` + `captured_at`:

- **`Company`** — `slug` (e.g. `"meta"`), `name`, `hq`, `dedicated_page_url` (their published community-impact page if one exists), `last_reviewed`.
- **`Claim`** — `id`, `company_slug`, `theme` (one of the 8 above), `statement` (the original quote, NOT paraphrased), `source_url`, `source_title`, `captured_at`, optional `metric` (e.g. `{"value": 1000, "unit": "jobs", "kind": "construction"}` for structured comparison).
- **`Project`** — `id`, `company_slug`, `name`, `city`, `state`, `country`, `lat`, `lon`, `status` (`announced` / `construction` / `operational`), `announced_year`, `claimed_investment_usd`, `claimed_jobs`, `notes`, `source_url`.
- **`CommunityResponse`** — `id`, `project_id`, `date`, `stance` (`positive` / `mixed` / `negative`), `constituency` (`residents` / `local_government` / `ngo` / `academic` / `journalist` / `regulator`), `summary` (1–2 sentences, neutral phrasing), `source_url`, `source_title`.

All four payload types live in `data/seed/` (the curator's working copy) and are mirrored to `docs/data/` on `refresh.py` for the frontend to fetch. **Don't** edit the `docs/data/*.json` files directly — they're build outputs; edit the seed and re-run.

## Editorial / sourcing rules

- **Quote claims; don't paraphrase.** A company's "we will" matters; restating as "they claim X" loses the original wording that's often the most-quoted-by-critics part. The `statement` field is for the verbatim quote; the surrounding UI provides any framing.
- **Every record carries a source URL and capture date.** No exceptions. If a claim has no source, it doesn't ship. Schema enforces this; the frontend renders a "view source" link on every card.
- **A live source_url is not the same as a verified claim (v1.19 lesson).** `source_url` returning 200 only proves the link works — it doesn't prove the page actually contains the specific fact being cited. This bit a 2026-07-14 refresh twice: a WebSearch tool's synthesized answer aggregates facts across *all* of that search's results, not just the one URL picked as `source_url` — two figures ("largest data center campus in Texas," a "$7B+ collateral" figure) made it into records because they were in the search tool's summary, not because they were confirmed present in the specific article cited as the source. Before shipping a WebSearch-derived fact, fetch the exact `source_url` directly and confirm the claim is actually there — don't trust the search synthesis as a stand-in for the citation. `scripts/validate_moratoriums.py` already automates exactly this check for moratoriums (fetch source, search for verbatim/near-verbatim claim text); the same discipline applies manually to Claims/Projects/Tariffs, which don't have an equivalent script yet.
- **A headline's loaded word ("ban", "moratorium") is not the underlying legal action — check for the jurisdiction's own denial (2026-07-27 lesson).** Two separate Loudoun County VA records were seeded describing a permanent "ban," both wrong. Loudoun's own FAQ states outright that a blanket moratorium is "not legally permissible" under Virginia law; what actually happened both times was a zoning-ordinance change moving data centers from by-right to special-exception review — real, but not a ban. Both records were removed rather than reworded (same treatment as CLAUDE.md's other "fix/remove, don't just swap the URL" precedent). The second occurrence of the identical failure shape is the signal it's worth a standing rule, not just a one-off fix: when a headline uses a strong restrictive word for a jurisdiction, look for that jurisdiction's own clarifying statement before trusting the headline's word choice.
- **A source's own news-index/channel page, fetched directly, surfaces recency that keyword search misses (2026-07-27 lesson).** Three rounds of broad WebSearch for new data center announcements (general, company-scoped, and DCD-domain-scoped) all came back with nothing genuinely new — every lead, cross-checked against the seed, turned out already-tracked or a stale recap of months-old news (see the 2026-07-14 "generic aggregator" lesson above, recurring). WebFetch-ing DataCenterDynamics' own listing page directly (`datacenterdynamics.com/en/news/?term=construction-site-selection`) returned an actual dated headline list and surfaced 3 real new projects plus the Loudoun catch above — none of which any keyword query reconstructed. A search snippet samples a source; a listing enumerates it. When a "is there anything new?" search pass comes back stale or empty, try the source's own index/channel URL directly before concluding the pass was exhaustive.
- **What counts as "first-party" (v1.6.1 expansion).** First-party means the statement comes from the company or a named executive — not the venue.
  - **Always first-party:** company-published material (sustainability page, blog post, press release, regulatory filing, S-1 / annual report).
  - **Acceptable as first-party:** a news article that contains a direct verbatim quote from a named company executive (e.g., *"'We will pay our way for electricity,' Brad Smith told Bloomberg."*). The quote is first-party even if the venue is a third-party outlet — the `source_title` should name both the speaker and the outlet (e.g., `"Bloomberg — Smith on Microsoft's Cheyenne pledge"`).
  - **NOT acceptable:** a news article paraphrasing the company without quotation marks. ("Microsoft says it will pay…" without a quote attached.) Skip rather than paraphrase.
  - **NOT acceptable:** an analyst report or NGO summary describing the company's commitment. Those are `CommunityResponse` records, not `Claim` records.
  - **NOT acceptable:** something an executive said in a context where they were not speaking for the company (a personal podcast take that wasn't picked up as a corporate position).
- **Stance is editorial, not algorithmic.** Stance tagging on community responses is a human judgment call — the rubric is in [DESIGN.md](../../DESIGN.md). **Don't** try to LLM-classify stance; it's the most adversarial part of the editorial frame and a wrong tag undermines the whole dashboard.
- **Constituency matters.** A negative stance from a state regulator is a different signal than a negative stance from a Twitter thread; the `constituency` field lets users weight accordingly.
- **Capture dates over "current" framing.** Company pages change frequently; a claim is always presented as "as of YYYY-MM-DD" in the UI. Re-capture quarterly. Old captures stay in the dataset (append-only) so historical drift is visible.
- **News-source diversity.** For each negative-stance project, prefer at least two independent sources from different outlets before flagging. Single-source claims get a `single_source: true` marker in the response record and a small badge in the UI.
- **Don't aggregate to a "trust score."** Surfacing a numeric "greenwashing index" would be both editorially indefensible and operationally fragile. Show the data; let users judge.

## Data acquisition strategy

v1 is **curated**, not auto-scraped. Each company's claims and projects are seeded from publicly-known sources by a human reviewer, validated against the schema, and shipped as JSON. This trades coverage for accuracy — the dashboard's value is editorial selection, not exhaustiveness. ~10 claims and ~3 projects per company is the v1 target; not 100 of each.

v2 will introduce **connector-based refresh** for the company pages that publish stable URLs (Meta's data centers page at `metadatacenters.com`, Google's data centers page, Microsoft's Datacenter Community Pledge). Connectors live under `connectors/` with the same base-class pattern as adjacent projects: rate-limited HTTP, disk cache, normalize to schema, idempotent re-runs. **Ad-hoc news / community-response sources stay curated** — no automated sentiment classification (see editorial rules above).

## What's explicitly OUT of scope (v1)

- Real-time scraping or alerts.
- Social-media sentiment mining (too noisy; constituency tagging would be meaningless).
- Predictive scoring of "trustworthy" vs "greenwashing" claims.
- Non-US data centers (US sites have richer public-record coverage; revisit in v2).
- Hyperscaler-adjacent colocation operators (Equinix, Digital Realty, etc.).
- Per-claim "delivered vs promised" verification (would need 5–10 years of historical claims to compare meaningfully).
- Automated stance classification on community responses.

## Delivered-vs-promised assessments on Claims (v1.13)

The dashboard's blueprint framing implicitly assumed commitments translate to delivery; v1.13 adds a `delivered` Optional sub-object on `Claim` so the curator can attach independent-reporting evidence of how a commitment actually played out. Four-status vocabulary, frozen for v1: `delivered` / `partial` / `contested` / `shortfall`. Schema in [schema.py](../../schema.py) (`Delivered` class + `DELIVERED_STATUSES` Literal); frontend mirror is `DELIVERED_STATUSES` + `DELIVERED_LABELS` in [docs/app.js](../../docs/app.js), guarded by `test_delivered_statuses_match` parity tests. Render lives in `renderDeliveredPanel()`, appended to `renderClaimCard()` only when `c.delivered` is set.

Four drift-safe rules:

- **Absence is editorially valuable.** A claim WITHOUT a delivered assessment means "the curator hasn't done the work yet," NOT "implied delivery." **Don't** auto-fill any default status; **don't** add a 5th "unknown" status to fill rows. Leave the panel off and the claim card reads exactly as it did pre-v1.13.
- **Status is a curator judgment call**, exactly like `Stance` on `CommunityResponse`. **Don't** try to LLM-classify it. Use `shortfall` only with strong corroboration (≥2 independent sources or a clear, citable regulator/court finding). `contested` is the right choice when the company maintains delivery and a credible third party documents shortfall — surface both, don't pick a side.
- **Summary is NEUTRAL synthesis** — not a quote, not adversarial framing. Cite the underlying evidence in `source_url`. Existing `claim.source_url` is the company's quote source; `claim.delivered.source_url` is the assessment source — they will almost always differ.
- **Adding a 5th status requires a BACKLOG entry + migration**, exactly like adding a theme. Add to `DELIVERED_STATUSES` tuple + `DeliveredStatus` Literal + `DELIVERED_LABELS` dict (Python), then the same three constants in `app.js`, then per-status color tokens in `:root` and `[data-theme="dark"]` blocks. The `test_delivered_status_vocabulary_frozen` test guards the four-status assumption.

A test (`test_at_least_one_of_each_delivered_status`) asserts the seed dataset ships with at least one example of each of the four statuses so the legend reads with all four colors backed by real records. **Don't** silently delete all examples of a status — the legend would render an empty chip.

The CSS palette mirrors stance hues (delivered ↔ positive, shortfall ↔ negative, partial / contested ↔ mixed-adjacent) so reading the dashboard's color signal stays consistent across the Claims tab and the Community tab.

## Moratorium source audit script (v1.18)

`scripts/validate_moratoriums.py` — audit trail validator for `data/seed/moratoriums.json`. For each record it fetches the `source_url` and up to three resource URLs (gov/official URLs fetched first), then searches the page text for seven verifiable claims: `bill_number`, `sponsors`, `vote`, `enacted_date`, `enacted_by`, `failure_reason`, `session`. Each found claim includes a **verbatim snippet** from the source page — the audit trail linking the record field to the source document.

Usage:
```
python scripts/validate_moratoriums.py                        # all 59 records
python scripts/validate_moratoriums.py --id maine-state-2026-04  # single record
python scripts/validate_moratoriums.py --cached               # offline, use cache only
python scripts/validate_moratoriums.py --dry-run              # schema check, no fetches
python scripts/validate_moratoriums.py --fail-on-unverified   # CI gate (exit 1)
```

Outputs `moratorium_audit_report.json` (per-record JSON trail) and appends to `ISSUES.md` for records missing a `.gov` source or with unverified critical claims. Both output files are `.gitignore`d — they're run artifacts, not source. Fetched pages are cached in `.moratorium_cache/` (also `.gitignore`d); delete the directory to force a re-fetch.

**Data quality rules enforced by `tests/test_validate_moratoriums.py`** (offline, no network):
- All `failed` records must have a `failure_reason`
- All `enacted` records must have an `enacted_date`
- No duplicate IDs
- All records have the required schema fields

## Moratorium comprehensiveness + accuracy pass (v1.20)

Big expansion + integrity pass. Moratoriums **59 → 91** (33 verified new records
across state/county/city), ratepayer scorecard **26 → 37 assessed sites**.

- **Validator v2 (`--links-only`).** `scripts/validate_moratoriums.py` now has a
  fast, deterministic link-liveness mode: a browser-UA `requests` fetcher
  (falls back to urllib) that follows redirects and classifies every URL as
  **live** (2xx) / **blocked** (403/429/SSL/timeout — real site, bot-walls us) /
  **dead** (404/410/DNS/refused). Only `dead` is actionable; this stops the
  urllib fetcher's 403/SSL false-negatives from reading as broken links.
  `--fail-on-dead-link` is the CI gate; writes `moratorium_link_report.json`
  (git-ignored). A companion **`--completeness`** mode (pure-schema, no network)
  flags records **missing a bill/ordinance #, gov link, vote, or sponsors** — the
  "still missing bill #s / links / specific language" gaps a curator fills before
  shipping (`--fail-on-incomplete` gate). Wrapped in the **`validate-moratoriums`
  skill** (`.claude/skills/validate-moratoriums/`). **The audit's job is link liveness +
  gov-source presence — deterministic and repeatable. Claim-text verification
  stays best-effort** (JS-rendered gov pages defeat any plain fetcher). Use
  WebFetch (gets through bot-walls) to actually fix links; the script can't.
- **Accuracy is a curation act, not just a link check.** The audit surfaced two
  records whose central claim was *false*, not just dead-linked: a Loudoun County
  "ban" (the county only moved data centers by-right→special-exception; no
  moratorium — **removed**) and a Connecticut "2-year >15 MW moratorium" (the real
  bills were a tax-incentive repeal + a co-location rule — **summary corrected**).
  When a source contradicts the record, fix/remove the record, don't just swap the
  URL. Also stripped **55 fabricated/dead `.gov` "resource" links** (a prior gen
  pass hallucinated plausible `.gov` paths). Net honest tradeoff: no-gov-source
  count *rose* (47) because fake gov links were removed — surfaced for future
  curation, not hidden. **Don't fabricate a `.gov` URL to satisfy the gov check.**
- **Moratorium Nation CSV** (`mjbommar.github.io/moratorium-data-2026`) is the
  richest lead source (222 rows) but carries **no per-row source URL** — mine it as
  a work-list, verify a live primary per row, never bulk-import (see BACKLOG).
- **Summary charts (`renderMoratoriumCharts`).** Pure DOM+CSS (no chart lib), so
  they re-theme on the dark swap via CSS vars — no `getComputedStyle` snapshot.
  Three charts above the table: a stacked-column **timeline** (`_morTimelineChart`,
  quarter buckets by `enacted_date||effective_date||captured_at`), and horizontal
  bar sets for **concerns** and **jurisdiction level**. New `--moratorium-{enacted,
  proposed,failed}` tokens (literal in BOTH `:root` blocks per DESIGN.md 12.12),
  reusing the tariff/stance green/amber/red language.
- **Timeline: one combined bar per quarter; jurisdiction level is a FILTER, not a
  second visual encoding.** `colour = status` is the only visual scale. Level lives in
  a segmented toggle (`.mor-toggle`, `MOR_TIMELINE_LEVELS`): **All / City-County /
  State / Federal**, each showing its record count. We tried encoding level as fill
  texture (city solid vs. hatched) and then as parallel bars — both made a small
  chart carry too much, and the parallel version doubled the axis width (see the
  clipping bug below). A toggle is the cheaper answer: one bar, one scale, level on
  demand. If a level split is ever needed *inside* a bar again, add a texture —
  **never** a second colour ramp.
- **The axis range AND y-scale derive from the FULL dataset, never the filtered
  subset.** This is what makes the toggle honest: quarters don't shift when you
  filter (it reads as filtering *in place*), and bar heights stay comparable between
  levels. Rescaling per filter would render Federal's **single** record as a
  full-height bar — as tall as a 58-record quarter. It must read as the sliver it is
  (`test_shared_yscale_keeps_federal_a_sliver`). Segment heights use `Math.max(2, …)`
  so slivers stay visible rather than rounding to nothing.
  What the toggle actually surfaces: **cities enact, states propose and fail** — the
  State view is mostly amber/red where the City/County view is green.
- **`overflow-x: auto` on a time-series chart silently eats the newest data.**
  (Learned when the levels were parallel bars: doubling the bars per quarter pushed
  the axis past the container.) The plot scrolled and **clipped the 2026 surge
  off-screen with no affordance** — it read as "the data is missing," and it shipped
  that way. The safeguards below stay in place regardless of bar count, because a
  long-enough axis will always outgrow a narrow viewport:
  (1) size so the full axis **fits** (a `max-width:560px` media query narrows the
  columns); (2) keep the **scrollbar visible**
  (`scrollbar-width: thin` + a styled `::-webkit-scrollbar`) — a hidden scrollbar is
  how data disappears quietly; (3) **park `scrollLeft` on the most RECENT** column
  after render, so whatever clips is the near-empty past, never the current surge.
  Do the park twice — once inline and once in `requestAnimationFrame` — because a
  chart rendered while its tab is still `display:none` has **zero `scrollWidth`**, so
  the inline call is a silent no-op. Guarded by
  `test_recent_quarters_never_clipped_on_narrow_viewport`.
  Measure clipping with `getBoundingClientRect` against the plot's rect —
  **not** `offsetLeft`, which is relative to the nearest *positioned* ancestor (the
  plot isn't one) and will lie to you.

## New York: an executive order and a bill are SEPARATE records (v1.20)

NY carries **two** moratorium records and they must not be conflated:
- `ny-state-eo62-2026-07` — **Executive Order No. 62**, signed 2026-07-14: the
  nation's **first statewide data center moratorium**. DEC holds pending discretionary
  permits in abeyance for data centers **≥ 50 MW**, until DPS delivers a final Generic
  Environmental Impact Statement. State environmental permitting only — **local permits
  are not covered**. Exempts manufacturing, research (incl. quantum), accredited
  education (incl. Empire AI) and medical care. Empire State Development must post a
  "Community Investment Framework" within 60 days. Primary source is the `.gov` EO text.
- `ny-state-2026-06` — the **legislature's bill**: the Responsible Data Center
  Development Act, **S10642 / A11560** (**20 MW**, 1 year), passed both chambers
  2026-06-04 and **still unsigned** as of 2026-07-26; Hochul issued the EO instead.
  Stays `proposed`.
  **Corrected 2026-07-26:** this section, and the record's own summary, previously
  cited "S7992/A7234". **S7992 is an unrelated New York labor-relations bill** —
  same failure shape as the Oregon HB4016 record (a real bill number attached to
  the wrong subject). REFRESH.md's status-re-check checklist already carried the
  fix ("NY's S7992 was superseded by S10642 after an Assembly substitution") but
  neither the data nor this file was updated to match. When a checklist records a
  renumbering, **grep the seed and the docs for the old number in the same pass** —
  a learning that only lands in the playbook doesn't correct the record.

Lesson: an executive order and a bill are different instruments with different
thresholds and different fates. When a governor "acts," check *which* instrument —
don't flip the bill record to `enacted` because an EO landed the same day.
- **PDF export redesign.** `exportMoratoriumsToPDF` builds a typographed document
  (`.mpdf-*` scoped `<style>`): serif display cover + kicker/dek, color-topped stat
  tiles, mini-bar summaries, a zebra directory table with status pills, and
  per-record detail cards each with a **sources list** (primary + resources, full
  URLs). html2canvas rasterizes, so colors are **hardcoded light-theme hex** (it
  won't resolve app CSS vars) and `scale: 1.6` + `jpeg 0.9` + `jsPDF compress`
  keeps a ~90-record export near ~9 MB instead of ~18 MB at scale 2.

## Ratepayer: individual-vs-general basis + conflict surfacing (v1.20)

Answers the two questions "was this site claimed individually or only company-wide?"
and "has any report come out that conflicts with meeting the pledge?"

- **Claim-basis badge (`rpClaimBasis`/`rpBasisBadgeHtml`).** Derived from whether a
  site-specific `evidence_claim_id` backs the record: **individual** ("Claimed
  individually") vs **company-wide** ("Company-wide pledge only"). Rendered in the
  always-visible card header. `affirmed` and `contested`-with-evidence read as
  individual; `pledge_only` reads as company-wide.
- **Conflicting reports (`rpConflictingReports`/`rpConflictsHtml`).** Surfaces
  negative `CommunityResponse`s about ratepayer cost-shift on **any** card
  (affirmed / pledge_only / contested) — a header **"⚠ Ratepayer concern"** flag +
  an expandable block listing each finding with its source. **Matching is
  id-based-first: a response whose id contains `ratepayer` is a curated conflict**
  (both the Synapse contested-site responses and the added regulator/report
  conflicts use that convention), with a keyword fallback (`RP_CONFLICT_KEYWORDS`).
  Keyword-only matching missed the Georgia PSC conflict ("shift costs onto
  residential customers" has no exact keyword) — the id tag is the reliable signal.
  Summaries note when a finding is **system/utility-wide** (Georgia Power fleet,
  Dominion cluster) rather than pinned to the one site — don't overclaim
  site-specific dispute.
- **Strict first-party bar for `affirmed`.** An `affirmed` Claim must be the
  *company's* words. A utility ESA quote (Minnesota Power's COO on the Google
  Hermantown site) is **not** first-party to the company → recorded as
  `pledge_only`, not `affirmed`. A named-company-exec quote in a trade outlet, or a
  quote attributed to the company itself, **is** first-party (Google's Wilbarger
  exec quote; Microsoft's Pecos statement) → `affirmed`.
- **New assessments:** 10 previously-unassessed pledge-era sites (7 affirmed w/
  backing Claims + 3 pledge_only) + one new post-pledge site (`microsoft-pecos-tx`,
  affirmed) + 3 conflict responses (Louisiana/Meta-Hyperion→meta-richland-la,
  Georgia-PSC→google-lagrange-ga, Dominion/JLARC→google-chesterfield-va).

## Signatory registry — the breadth tier (v2)

On 2026-07-23 the pledge went from 8 organizations to 200+. `Signatory` +
`signatories.json` track them. **Two tiers, deliberately:**

- **`Company`** — depth. 13 slugs, each with curated claims, projects, a written
  summary. Adding one still requires the two-gate editorial test.
- **`Signatory`** — breadth. Every roster row, carrying only what the roster
  publishes (name, category, domain, track, date). `matched_company_slug`
  bridges the two.

**Don't** expand `companies.json` to hold the roster. It breaks the company
rule, explodes `COMPANY_SLUGS`, and implies we have researched 279
cooperatives. The thin record is the honest shape.

`scripts/build_signatories.py` builds the seed from the White House page
(`--cached` to parse the cache, `--diff` to preview adds/removals). Idempotent:
an unchanged page produces a byte-identical file, so any diff means the roster
actually moved. **It never auto-deletes** — a removal is news; `--diff` surfaces
it for a curator.

Two integrity lessons from building it:

- **The source page disagrees with itself.** On 2026-07-25 its filter chips
  advertised 281 organizations / 69 utilities while the list underneath held
  279 / 68. Both are stored — ours derived from the list, theirs verbatim in
  `roster_counts_stated` — and `drift_note` states the gap in reader-facing
  words, surfaced in the UI (`#rp-drift-note`). **Don't** silently pick one;
  reconciling a source's self-contradiction is inventing a fact.
- **Two distinct co-ops share a name.** "Southeastern Electric Cooperative"
  appears twice on different domains. The first parser deduped by slug and
  silently dropped one. It now disambiguates by domain and *raises* rather than
  dropping a row it cannot tell apart. Any dedupe over an external list needs
  the same shape: disambiguate or fail, never drop.

Governors are signatory records too (`category: "governor"`, `state` required,
sourced to the RGA release) so the state panel gets its governor row for free —
but their `notes` must record that they signed an **addendum**, not the
corporate pledge, and `test_governors_are_not_conflated_with_corporate_signatories`
enforces it.

`utility_aliases` maps tariff `utility` strings onto roster rows. **Exact
matches only, hand-curated** — AEP Ohio and AEP Texas are different companies
and no fuzzy matcher is trusted to know that. Where a holding company signed
and the tariff names its subsidiary (Berkshire → NV Energy, Exelon → ComEd,
WEC → We Energies, MDU → Montana-Dakota), the record's `notes` says so rather
than flattening the two. Coverage is 20/25 tariffs; the 5 unmatched are four
statewide frameworks and one federal FERC case — genuinely unmatchable, and
reported rather than forced.

Vocab mirrors to app.js as `SIGNATORY_CATEGORIES` / `SIGNATORY_TRACKS` (+ label
maps), parity-tested. Note the deliberate split from the source page: it files
all data-center companies under one "DATA CENTER" chip; we re-tag the seven
March-round buyers as `hyperscaler` because a company buying power and a
developer building the shell answer different questions here.

**The roster keeps growing after the event, and the builder now knows it
(2026-09-21).** A re-pull two months after the 07-25 snapshot found 44 new
organizations, 2 spelling corrections on the source page ("Digital Reality"
→ "Digital Realty"; "East Central Electric Oklahoma Cooperative" → "East
Central Oklahoma Electric") and the page advertising *fewer* organizations
(321) than its list held (323). Three things the builder does about it:

- **New rows go on the schema's `rolling` track with `signed_date: null`** and
  a note naming the snapshot that first showed them. The roster publishes no
  join dates, and the old behaviour — every non-March/DOE row gets the July 23
  cohort date — would have stamped a fabricated date on all 44. A row already
  on the previous snapshot keeps that snapshot's track and date; the
  hyperscaler/DOE overrides still win. `test_a_row_new_to_the_roster_is_a_
  rolling_add_with_no_guessed_date` and its siblings pin this, and the fixed-
  point test proves a rolling add stays rolling on the next rebuild.
- **Same domain on a removed + added pair is a RENAME**, reported as such by
  `--diff` and carried over (original track + date, plus a note) rather than
  surfacing as an unexplained departure and a brand-new signatory.
- **`UTILITY_ALIASES` in the builder is the single source of truth for
  aliases.** The v3 rate-case pass added six aliases (Ameren, NiSource,
  NorthWestern, and extra NV Energy / Duke / Entergy spellings) to the seed
  JSON only, so the next rebuild would have silently dropped them and broken
  every rate-case join. Synced back into the builder; add aliases there, then
  rebuild. This is the "hand-written list that mirrors a registry rots" lesson
  from the top of this file, in the one file that IS the registry.

The Home activity feed carries a data-derived item for rolling adds (dated to
the snapshot, wording says the join dates are unpublished), and the expansion
item now reports the cohort as it stood on July 23 rather than today's total.
Dating individual rolling adds from their own press releases is a BACKLOG
lead, not something to guess at.

## Roster-driven eligibility (v2 — supersedes the flat pledge date)

**A site is assessable only if its operator had already signed when the site was
announced.** Before v2 this compared every project against the single White
House date, which mislabels the July cohort: a CoreWeave site announced in May
2026 predates CoreWeave's own signature by two months and cannot be measured
against a pledge that company had not yet made.

Both sides read per-company join dates from the roster:
- `refresh.py` — `_signatory_dates(signatories)` → `_is_ratepayer_eligible(p, signed_dates)`
- `app.js` — `projectPledgeDate(p)` → `isPrePledgeProject(p)`

`projectPledgeDate` falls back to the White House date while the roster payload
is still in flight, so a cold deep-link doesn't briefly render every site as
non-signatory.

The pre-pledge bucket now carries **two** reasons, and `prePledgeNote()` says
which: a 2024 Meta site predates a pledge that existed before we tracked it; a
May 2026 CoreWeave site predates *its own operator's* signature. The second is
not a gap in follow-through — it is outside the window. **Don't** collapse them
back into one label.

## `Moratorium.state_code` (v2)

Explicit field, backfilled for all 102 records. The spec expected to parse a
`", TX"` suffix off `jurisdiction`; **no record has one** — `jurisdiction` is a
bare place name ("Baltimore", "Cave City") and the id only sometimes carries a
code. 81 were derivable from the id or a state-name lookup; **20 needed hand
verification against each record's own source**, because city names are
ambiguous (Madison, Smithfield and St. Charles each exist in several states).

A payload validator rejects any non-federal record without one. That matters
because the failure mode is silent: a missing code doesn't error anywhere, the
record just stops appearing in its state's panel, which reads as "no
moratoriums here" rather than as a data gap.

## The pledge's five commitments are quoted, and were paraphrased (v2.2)

`PLEDGE_PRINCIPLE_DESCRIPTIONS` in app.js now holds the **verbatim** body text
from the White House pledge, re-fetched and re-verified 2026-07-28. It held
paraphrases until then, and two had drifted in the direction that flatters the
pledge:

- **`separate_rate`** claimed companies pay "for the power and infrastructure
  brought online, used or not." The source body says only that they will
  *negotiate separate rate structures*. The pay-anyway framing is that section's
  **title** — we were quoting the headline back as if it were the commitment.
  Same failure shape as the Loudoun "ban" lesson: a headline's strong word is
  not the underlying action.
- **`grid_resilience`** dropped the source's "whenever possible" hedge on backup
  generation, turning a qualified commitment into an unconditional one.

`test_commitment_text_is_verbatim_from_the_pledge` pins all five strings, so
re-tightening them into snappier lines is a deliberate edit to the test file.
If a layout needs them shorter, shorten the layout — `PLEDGE_PRINCIPLE_SHORT`
already exists for exactly that. The band's footnote now reads "titles **and
text** quoted verbatim".

Titles were already verbatim and stay so, modulo case: the source uses Title
Case, the dashboard renders sentence case throughout, and
`test_commitment_titles_are_the_pledges_headings` compares casefolded.

`PLEDGE_PRINCIPLES` / `PLEDGE_PRINCIPLE_LABELS` were mirrored Python↔JS with
**no parity test** — the only mirrored vocabulary here that lacked one. Now
guarded by `test_pledge_principles_match` / `test_pledge_principle_labels_match`.

Note the pledge's five commitments and the dashboard's eight `THEMES` are
**different axes** and are not being reconciled: THEMES is the community-benefit
taxonomy (jobs, water, education…), the commitments are ratepayer-cost
obligations. Don't map one onto the other.

## Rate cases — the proceeding layer under the tariffs (v3)

`RateCase` + `data/seed/rate_cases.json` (edit the seed directly, then
`python3 refresh.py`). **`scripts/build_rate_cases.py` was deleted 2026-10-18**:
the daily routine had been editing the seed, so the builder fell 3 records and
7 revisions behind, and one re-run would have silently reverted them. A
generator and hand edits to its output can't both be the source of truth. A tariff is the
instrument; a rate case is the fight: the docketed PUC/PSC/FERC proceeding where
who-pays-for-data-center-load actually gets decided. Separate record type
because several cases exist in states with no tracked tariff, one tariff can
accumulate proceedings over its life, and `next_milestone` needs a home.

- **`next_milestone` is regulator-announced steps only, never a guess** — the
  schema description says so and the Home "What's next" list renders it
  verbatim. A milestone with only a season/quarter stays in the text field;
  `next_milestone_date` is for a specific announced day.
- **Statuses `pending|approved|rejected` render with the tariff palette**
  (pending shares the `proposed` amber) via `RATE_CASE_BADGE_CLASS`; the
  badge-class map is parity-tested against the status vocab so an unmapped
  status can't silently fall back to a colorless badge (the `badge-reason-*`
  failure shape).
- **Deferred-tier payload**, like `responses.json`: fetched by
  `loadRatepayerView` after first render, never preloaded — first paint stays
  at 8 requests. `tests/test_perf_budget.py`'s DEFERRED list records it.
- **Cross-refs validated at refresh time**: `related_tariff_id` must exist in
  tariffs, `related_project_ids` in projects. `coverage.json` now carries
  per-state `rate_cases` counts (federal `US` rows excluded from state cells).
- **Verify sources by fetching, and .gov order PDFs by reading them.** Two
  orders were text-extracted (zlib-decompress the PDF streams, grep the Tj/TJ
  text operators) to confirm dates/thresholds/parties before shipping: MO
  ET-2025-0184 (75 MW, issued 2025-11-24, effective 2025-12-04, Amazon/Google
  as signatory intervenors) and IN Cause 46362 (Amazon special contract dated
  2025-09-18). A state PUC **legal notice in a local paper is a dated primary
  source** — the PUCN notice for Docket 26-06023 is where 'Callisto
  Enterprises, LLC ("Google")' is the Commission's own identification.
- **Search synthesis will hand you the wrong docket.** "Georgia Power's 2025
  rate case, docket 44280" came back from search; fetching the PSC docket page
  showed 44280 is the **2022** rate case (still Open — the 2025 freeze
  stipulation extends that plan). Same v1.19 lesson, docket-shaped: fetch the
  docket page before storing a docket number.
- **.gov press URLs rot fast; dockets don't.** The MO PSC press release
  (pr-26-40) and DeKalb's agenda PDF both 404'd within months of publication.
  Cite the EFIS/docket-system URL (or the order document itself) as
  `source_url`; press releases go in `resources` if anywhere.
- **Nevada's PUCN docket system is `puc-onbase.nv.gov`, and its document API
  is the primary source (2026-09-22).** `nv-energy-callisto-esa` (Docket
  24-06014) had been flipped to `approved` and reverted TWICE on aggregator-only
  sourcing. The third pass searched the portal itself (saved as
  `pucn_search_24-06014.json`): it lists STIPULATION 4/28/2025, DRAFT ORDER
  5/7/2025, ORDER 5/14/2025, then compliance filings — and the order PDF,
  fetched from the portal's `/api/Document/<id>/` endpoint, says the Commission
  "accepts the Stipulation and grants the Application as modified." The ESA was
  approved in **May 2025**; the aggregator had the year wrong, which is why no
  2026 order could ever be found. The record now cites the order document
  itself. Rule: for NV dockets, list the docket's documents on the portal and
  cite the order; for any docket, an approval with no order document is not an
  approval.
- **`utility_aliases` now joins three surfaces** — tariff, rate-case, and
  project `serving_utility` strings all resolve through the same hand-curated
  map (`test_utility_aliases_resolve_to_real_records` widened accordingly; the
  dead-alias guard rejected a speculative bare "NIPSCO" immediately, which is
  the guard working). The aggregate **By utility** rollup groups by resolved
  roster row, else verbatim string; display shows the roster (parent) name
  only when a group genuinely spans multiple operating utilities (Duke IN +
  Carolinas), keeps the operating name for single-string rows (SWEPCO stays
  SWEPCO), never fuzzy-matches.

## Policies & Agreements tab (v3.1, 2026-09-23)

`Policy` + `data/seed/policies.json`, tab `#policies` (between Tariffs and
Sites). Spec and research plan: [notes/specs/SPEC_POLICIES_TAB.md](../../notes/specs/SPEC_POLICIES_TAB.md).
Holds the instruments between a moratorium (a pause) and a tariff (who pays
for power): executive orders, statutes and regulations that set conditions,
local ordinances, site-level community benefit / host / development / PILOT
agreements, and companies' own published community plans.

- **One record type, `instrument` field** (`executive_order | legislation |
  regulation | local_ordinance | benefit_agreement | company_plan`). A state
  framework that requires a CBA and the CBA a county then signs share every
  field that matters, and one directory with a type filter shows "what was
  required" beside "what was won". Don't split it into two types.
- **`benefit_themes` reuses the frozen 8 THEMES**; `community_benefits_framework`
  (bool, `CBF` badge) marks records that require, create or are a CBA,
  community fund or host payment. That flag is the thing readers came for.
- **`key_terms` must each be literally on `source_url`.** A term the agent
  flagged as "secondary reporting, not confirmed on this source" gets cut,
  not kept with a caveat.
- **`scope: company` is only for a `company_plan`**, and every plan names its
  `company_slugs`. A company's pledge for ONE host community (xAI's "Our
  Commitment to Memphis", Brookfield at Paducah) is a `company_plan` scoped to
  that city: it is the company's own words, not a negotiated agreement, so
  don't file it as `benefit_agreement`.
- **`value_usd` is the value of committed community benefits.** Not total
  project investment ($17B, $100B slipped in on the first pass), not a
  projected ROI, and not a sum the curator computed from several terms.
- **Pure pauses stay on the Moratoriums tab; everything else lives here.**
  Governor directives that pause *tax-incentive applications* (IL, OH, AZ
  2026) are policies: they pause a subsidy, not development. The PA EO
  2026-05 (conditional permitting) moved here on 2026-09-23.
  `test_non_pauses_are_not_filed_as_moratoriums` rejects a moratorium record
  whose own `policy_type` says it isn't one. `related_moratorium_id` exists
  for a genuine overlap; don't duplicate a record across the two tabs.
- **A homepage citation is how fabricated records survive.** The same pass
  found the moratorium tab's "Washington SB 5982 (2024)" was a Department of
  Health bill, and "Oklahoma HB 2992 (2024)" was really a 2026 law, with
  invented sponsors and votes. Both cited a bare homepage
  (`datacenterbans.com/`, `app.leg.wa.gov/`), which "resolves" while proving
  nothing. Checking the bill number on the legislature's own site took one
  fetch each. `HOMEPAGE_SOURCED_MORATORIUMS` (tests/test_policies.py) lists
  the 22 moratorium records that still cite only a homepage and lets that
  list only shrink. Policies may not cite a bare homepage at all.
- **`delivered` on a Policy reuses `Delivered`** (in-effect records only).
  The evidence bar is *independent* evidence that a payment was made or a
  grant awarded: the recipient government's own record of receipt, or an
  announcement naming recipients. A company page restating the pledge, a
  page older than the agreement, or spending not tied to the agreement is
  not evidence. Four of seven research findings failed that bar on review.
  Absence means not yet assessed.
- Statuses reuse the tariff palette through `POLICY_STATUS_BADGE_CLASS`,
  whose *values* are checked against styles.css (the RATE_CASE_BADGE_CLASS
  lesson). The payload is promise-memoized (tab + state panel both load it)
  and never on first paint. The state panel now has **six** sections.
- **The state modal lives inside the Pledge view.** `openStatePanel()` called
  while another view is active opens an invisible modal. e2e tests must
  `activateView('ratepayer')` first. The `#state/XX` deep link already does.

## Per-signatory deep dives — plan only, not built

[notes/specs/SPEC_SIGNATORY_PAGES.md](../../notes/specs/SPEC_SIGNATORY_PAGES.md) proposes `#signatory/<id>`
pages for all 302 roster rows, a stored `SignatoryCuration` work ledger, and a
REFRESH.md "Signatory sweep". **Nothing in it is implemented.** The load-bearing
constraint it works around: 291 of the 302 rows hold only what the roster
publishes, so a page titled "deep dive" over six fields is a lie told by layout
— curation state has to be stored and rendered, not implied. Read it before
starting any per-signatory work.

## `project_page_url` is distinct from `source_url` (v1.1)

`Project.project_page_url` (Optional[HttpUrl], schema.py) is the canonical project page on the company's official site (e.g. `https://datacenters.atmeta.com/2021/03/hello-georgia/` for `meta-newton-ga`). `Project.source_url` is where THIS RECORD was sourced — often a press release or news article. They overlap when the project page is also the announcement source (Meta does this); they diverge when the source is a Reuters / Bloomberg / company-blog post that links *out* to the project page. The detail panel's Overview tab renders both as separate KV rows ("Project page" + "Record source"). When adding a project, fill `project_page_url` if a canonical project page exists; leave null if not (e.g., Stargate Abilene has no public OpenAI page yet that returns 200 to scrapers).

## Physical / operational project fields (v1.2)

Four new optional fields on `Project` capture the physical scale and tenant arrangement of each campus:

- **`acreage`** (Optional[float], acres) — physical site size. Cumulative across phases for sites that have expanded (e.g. Meta Richland 2,250 ac, AWS Project Rainier 1,200 ac). Null when the site is too distributed for a single canonical figure (e.g. AWS Loudoun spans 50+ parcels).
- **`power_mw`** (Optional[float], megawatts) — total announced electrical capacity. Latest known number — pre-Cox-scaleback Wonder Valley would have been 7,500 MW (7.5 GW); the seed uses the post-scaleback 1,500 MW (1.5 GW) figure. Null when the company hasn't disclosed (Microsoft Quincy and Mt. Pleasant are intentionally null — neither has a clean Microsoft-disclosed total).
- **`gpu_count`** (Optional[int]) — total announced AI accelerators (NVIDIA H100/H200/GB200, AMD MI300, AWS Trainium 2, Google TPU). **Almost always null for owner-operator hyperscaler sites** — Meta, Google, MS, AWS owner-operator campuses don't publish GPU counts. Where it IS public: Stargate Abilene (450K GB200), Project Rainier (500K Trainium2), Memphis Colossus (230K H100/H200/GB200).
- **`offtaker`** (Optional[str]) — the workload owner. For owner-operator sites this is the operating company itself ("Meta", "Google", "Microsoft", "AWS"). The field's real value is in **colocation arrangements**: `oracle-abilene-tx` shows `OpenAI` (Oracle hosts, OpenAI uses); `aws-new-carlisle-in` shows `Anthropic` (AWS operates Project Rainier, Anthropic is the primary tenant). Null for `wonder-valley-box-elder-ut` because the developer hasn't named tenants.

Frontend formatters in [docs/app.js](../../docs/app.js): `formatAcreage` (rounds to whole acres ≥10, one decimal below), `formatPower` (auto-converts ≥1000 MW to GW with one decimal), `formatGpuCount` (compresses to "K" / "M"). The Overview tab renders all four under the existing investment/jobs rows; null values use the standard `setKv()` "Not disclosed" placeholder. **Don't** display the offtaker as a separate badge if it equals the company — the redundancy is fine in the KV grid (always present, easy to scan), but a badge would just be noise for the 12 owner-operator sites where they match.

## International tab (v6, 2026-10-19, owner-directed)

Spec and decisions: [notes/specs/SPEC_INTERNATIONAL.md](../../notes/specs/SPEC_INTERNATIONAL.md)
(owner answers are at the top). Research inputs: `notes/specs/international/`.
Tab `#world`, placed last; country pages at `#country/XX`.

- **One lazy payload, partitioned.** Every non-US record lives in
  `data/seed/international.json` (`InternationalPayload`). The US payloads
  reject a non-US record and the international payload rejects a US one, so
  US code paths keep assuming a `state`. The file is never on first paint
  (`tests/test_perf_budget.py` DEFERRED).
- **Jurisdiction:** `country` (ISO 3166-1; `EU` for supranational) and
  `subdivision` (ISO 3166-2, from `SUBDIVISIONS`). `federal` means the US
  government only. Another country's government is `national`, and an EU rule
  is `scope: supranational`. The registries (COUNTRIES, SUBDIVISIONS,
  LANGUAGES, CURRENCIES, TRANSLATION_SOURCE_LABELS, MORATORIUM_FORMALITY_LABELS)
  are mirrored in app.js and parity-tested in `tests/test_international.py`.
- **Quotes stay in the original language.** `Claim.statement` and
  `Policy.key_terms` are verbatim in `statement_lang` / `source_lang`. The
  English goes in `statement_translation` / `key_terms_translation`, labelled
  `machine` / `human` / `official`. A machine translation is always labelled
  "Machine translation (AI)".
- **Money as stated.** Use `Money {amount, currency, as_stated}`. Never set
  `claimed_investment_usd` or `value_usd` on an international record. The
  "≈ US$" line is display-only, computed from `FX_USD_PER_UNIT` in app.js
  (Federal Reserve G.5A 2025 annual averages). CLP and ARS are not in G.5A, so
  they get no approximation.
- **Operators abroad become companies** with `international_only: true`
  (Nscale, SEGRO, Goodman). They do **not** clear gate 2 of the two-gate test:
  none publishes a community-impact page. The owner decided on 2026-10-19 to
  add international operators as companies anyway, so don't remove them on
  gate-2 grounds the way Amentum was. That exception covers international-only
  operators only; US company additions still need both gates.
  **Update (wave 2, owner):** an international operator that also runs US
  sites goes on the US tab. Nscale (Monarch, Mason County WV) and Goodman
  (LAX01 Vernon CA) are `international_only: false`, with US projects and no
  US claims. `TestSeedCoverage.GATE2_OWNER_EXCEPTIONS` records the
  exception. SoftBank Corp., NEXTDC and XTX Markets were added as
  international-only operators. atNorth and GRECO MI are held back in
  `notes/specs/international/wave2/deferred_needs_company.json`: atNorth's HQ
  couldn't be verified, and GRECO's figures were not probe-matched. The US Companies tab and the Home count skip
  them, and `companiesBySlug` still resolves them. Their sites are owned by
  `country:XX` refresh units, not `company:` units.
- **`heat_reuse` principle** is mainly practiced abroad. The Frameworks card
  for any principle with no US records says "See it abroad →".
- **Verification for non-English pages:** WebFetch returns a *summary*, not
  page text. Every verbatim must be a `scripts/probe.py` HIT. probe now
  decodes UTF-8, which fixed accented Spanish and French phrases missing. Read
  PDFs with macOS PDFKit (`osascript -l JavaScript`). Wave 1's 44 quotes are
  all HITs.
- **Nine tabs on a phone.** The ninth tab wrapped the bar to a third row and
  pushed every view down about 44px; the interaction budgets caught it.
  `test_phone_tab_bar_stays_two_rows` guards 360/375/390px. Phones also get
  two-column Home cards.
- **Daily routine:** `country:XX` units, 120-day cadence, English sources
  only. Non-English findings become BACKLOG leads (see the daily-refresh
  skill).

## Elections (2026-11-04)

`data/seed/elections.json` has validated race/measure records, separately sourced
results, outgoing officeholders and candidate statements. `docs/elections.js`
is lazy-loaded with its payload. `#elections/<id>` opens a record; preserve that
ID on a failed load so Retry opens the requested evidence. Reported winners
are not certified or already serving. Advisory measures never create legal
moratorium links. Source revalidation checks each nested quotation against its
own URL; a successful result source cannot validate another candidate's words.

A missing MW field does not establish that all facility sizes are covered:
area thresholds and alternative criteria belong in the sourced scope summary.
The detail panel therefore says “See scope below” for missing MW values.

## Unpublished signing dates (2026-11-04)

A rolling signatory can have no published signing date. Once the roster loads,
`projectPledgeDate()` must preserve null; the original-event fallback applies
only before roster loading. Unassessed sites with unknown timing remain visible
with that qualification, including CSV exports. A new company membership flag
requires checking every date/eligibility consumer, not just roster parity.
