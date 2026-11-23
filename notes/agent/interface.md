# Interface history and rules

Moved verbatim from CLAUDE.md on 2026-11-23. Read before changing a view, navigation, typography, the Home digest, sub-tabs, accordions or modals. Newer sections supersede older ones; the current direction is in CLAUDE.md and DESIGN.md.

## Draft banner (v1.4)

A thin top strip (`.draft-banner` in [docs/styles.css](../../docs/styles.css), `<div class="draft-banner">` at the top of `<body>` in [docs/index.html](../../docs/index.html)) signals to readers that the dataset is under active curation. The banner says "Draft · Data collection in progress · Last refresh: YYYY-MM-DD". The date is a `<span id="draft-date">` so it can be wired to a build-time stamp later if we want — for now it's hardcoded to the current refresh date. **Don't** remove the banner without explicit user direction; it sets reader expectations about completeness ("if your favorite site isn't here, it's because we haven't gotten to it yet, not because it doesn't matter"). Test `test_draft_banner_present` guards visibility + content.

## Two views

**Company Comparison view (default landing).** A thematic matrix of benefit claims across the eight companies. Rows = companies, columns = themes (see Theme Taxonomy below). Cell content shows claim count + a representative claim quote. Surfaces patterns at a glance: which companies have formalized pledges vs ad-hoc claims, which themes are universal vs niche, which companies surface community engagement as a theme at all.

**Project Explorer view.** Individual data center sites. Each project carries: company, location (city/state, lat/lon), status (`announced` / `construction` / `operational`), claimed investment, claimed jobs, the company's stated benefits for that site, AND any documented community responses (positive, mixed, negative) with constituency tags. Geo-tagged on a map; filterable by company, theme, stance, status.

## Project-detail tab strip (v1.1)

The project pop-out in the Explorer view is split into three tabs — Overview / Claims / Community — generated from `DETAIL_TABS = ["overview", "claims", "responses"]` in [docs/app.js](../../docs/app.js). Three drift-safe rules:

- **Iterate `DETAIL_TABS` everywhere.** `setActiveDetailTab()`, `wireDetailTabs()`, and any future code that enumerates tabs MUST loop over the constant — same drift-safe iteration pattern as `THEMES`. When a 4th tab ships, drop it into the array and the wiring picks it up for free.
- **Last-clicked tab persists within session, resets on reload.** Module-level `_lastDetailTab` (default `"overview"`) records the user's last explicit click; `resetDetailTabs()` restores it on every `selectProject()`. **Don't** snap back to Overview on every selection — a user scanning Claims across multiple projects shouldn't have to re-click on every project. **Don't** persist to `localStorage` either: a returning user reloading the page should land on the structured Overview, not whatever lighter pane they last visited.
- **Tab-count badges hide via `[hidden]`.** `updateDetailTabCounts(claims, responses)` sets `badge.hidden = (count === 0)`. The `[hidden]` global rule has `!important` so the inline `display: inline-block` on `.dtab-count` doesn't override. Test `test_count_badges_hidden_when_no_data` guards against the trap regression.

## Playwright `wait_for_selector` on hidden-by-default panes (v1.1)

The Community pane is `[hidden]` by default (Overview is the landing tab). Tests that target elements inside that pane MUST pass `state="attached"` to `wait_for_selector`, e.g. `page.wait_for_selector("#d-responses .response-card", state="attached")`. Default `state="visible"` would time out because the parent's `display: none` removes children from the bounding box. Same lesson as adjacent projects — when you waited for visibility but the selector targets a `[hidden]`-conditional element, the wait races a CSS transition or an attribute toggle and flakes on slow runners. Locator `count()` and attribute reads work fine without the wait — they query the DOM, not the layout box.

## Ratepayer Protection Pledge view (v1.15, substantially revised in v2 — read the v2 section below first)

A **third top-level tab** (`view-ratepayer`) built around a real-world anchor: the White House Ratepayer Protection Pledge, signed 2026-03-04 at the White House by seven hyperscalers (Amazon, Google, Meta, Microsoft, OpenAI, Oracle, xAI); QTS became the eighth signatory via the DOE companion track on 2026-04-24 (`RATEPAYER_PLEDGE_DOE_DATE`). The view answers "who signed, and is it showing up at the data centers they've announced since?" — top-level stat tiles, a signatory roster, and a per-site scorecard. Unassessed signatory sites are split date-aware by `isPrePledgeProject()` in app.js into two sections: "Pledge-era sites awaiting assessment" (`#rp-unassessed`: announced on/after the pledge, or year-only 2026 — a bare year can't be placed either side of March 4, so it stays pledge-era rather than being mislabeled) and "Sites announced before the pledge" (`#rp-pre-pledge`). The CSV export labels the buckets `not-yet-assessed` / `pre-pledge`. Bucketing is company-agnostic (White House date) — no dated QTS site currently lands in the Mar 4 – Apr 24 DOE-track window; revisit if one does. Lazy-loads the projects/responses payload (NOT Leaflet — that stays Explorer-only) via the shared `loadProjectData()` extracted from `loadExplorerData()`. Deep-linkable at `#ratepayer`.

Two data structures back it, both in [schema.py](../../schema.py):
- **`Company.ratepayer_pledge_signatory`** (bool, default False) — **v2: now a MIRROR of `signatories.json`, not a hand-maintained list.** Eleven tracked companies are signatories as of 2026-07-23 (the original seven, QTS via DOE, plus CoreWeave / Crusoe / Prologis from the expansion). Still **fixed historical fact, not a curator judgment** — don't flip it for companies that publish their own commitment but didn't sign (Anthropic stays False). Flip it only when the roster says so. `test_signatory_flags_match_the_roster` asserts the two agree; `test_the_original_eight_are_still_signatories` keeps the March/DOE cohort from being dropped. The old `test_exactly_the_eight_signatories_flagged` hardcoded the set, which is exactly what let the flag sit stale through an expansion that tripled it — **don't reintroduce a hardcoded roster in a test.**
- **`Project.ratepayer`** (Optional `Ratepayer` sub-object) — a curated per-site assessment with a 3-status vocab: `affirmed` (site-specific pay-our-own-way commitment exists; `evidence_claim_id` points at the backing verbatim Claim) / `pledge_only` (signatory + post-pledge, no site-specific commitment captured) / `contested` (third party documents the site shifting costs despite the pledge). Frozen for v1.

Drift-safe rules (same spirit as the delivered block):
- **Only attach `ratepayer` to signatory projects announced on/after THEIR OPERATOR'S signing date** (v2; it was a flat 2026-03-04 before). Pre-pledge or non-signatory sites get nothing — `test_assessed_projects_belong_to_signatories` and `test_assessed_projects_announced_on_or_after_pledge` enforce the cohort boundary. Absence is honest.
- **`pledge_only` is NOT a failing grade.** It means "covered by the national signature, nothing site-specific captured." Don't write it as criticism; don't attach an `evidence_claim_id` to it (`test_pledge_only_assessments_have_no_evidence_claim`).
- **`affirmed` MUST cite a real, project-owned claim** in `evidence_claim_id`. refresh.py's cross-ref pass validates the id exists AND belongs to the same project; `test_affirmed_assessments_cite_a_real_owned_claim` mirrors it.
- **No forced one-of-each-status.** Unlike delivered, only `affirmed` + `pledge_only` are required (`test_at_least_one_affirmed_and_one_pledge_only`); the frontend legend (`renderRatepayerLegend`) only renders chips for statuses actually present in the cohort. The first `contested` examples landed 2026-06-11: the three post-pledge Amazon Mississippi sites (`amazon-clinton-ms`, `amazon-vicksburg-ms`, `aws-ridgeland-ms`), based on the May 2026 Synapse Energy Economics report (commissioned by Earthjustice / Environmental Advocates Mississippi; covered by Mississippi Today and independently by Vicksburg Daily News) estimating ~$38M in data-center-related costs already charged to Entergy Mississippi residential ratepayers — while Amazon/Entergy maintain full-cost payment and invoke the pledge. That's the canonical `contested` shape: surface both sides, don't pick one. Each contested site keeps its `evidence_claim_id` (the company's affirmation is the other half of the dispute), flips the `delivery_infra` principle to `not_met` with a dispute-aware note, and carries a paired negative `CommunityResponse` (constituency `ngo`) citing the report coverage. **Don't** mark `contested` from criticism of a rate *structure* alone (e.g. NIPSCO GenCo skepticism in Indiana) — it requires documented cost-shifting at/serving the site.
- **Status vocab mirrors to `app.js`** as `RATEPAYER_STATUSES` + `RATEPAYER_LABELS`, guarded by `test_ratepayer_statuses_match` / `test_ratepayer_labels_keys_match`. Adding a status = BACKLOG entry + the Python/JS constants + `--ratepayer-<status>` color tokens in both `:root` blocks, same drill as delivered/themes.

The roster's non-signatory flagging (Anthropic surfaces as "Own commitment") is **frontend-derived** via a keyword scan (`RATEPAYER_CLAIM_KEYWORDS` in app.js) over each company's claims — it's a discovery affordance, not a stored field, so it stays in sync as claims land. The `"100% of the grid"` keyword was added when QTS moved into the signatory group so Anthropic's "pay for 100% of the grid upgrades" keeps the non-signatory group populated (the flag surfaces the *clearest* non-signatory commitments, it isn't a census). The CSS palette reuses the delivered hues: `affirmed ↔ delivered green`, `pledge_only ↔ partial blue-grey`, `contested ↔ amber`.

## Ratepayer card source links (v1.17 fix)

Every ratepayer card (assessed, pledge-era unassessed, and pre-pledge) renders an always-visible **"Sources:" footer** via `rpCardSourcesHtml(p)` in app.js. Before v1.17, only `affirmed`/`contested` sites surfaced a link — and only after expanding two nested `<details>` — so the 18 `pledge_only` sites and all pre-pledge sites read as having *no* evidence at all. The helper dedupes by URL and links, in order: the site-specific evidence claim's `source_url` (when present) → the project's `project_page_url` → the project's `source_url` (always present, schema-required) → the pledge proclamation (`RATEPAYER_PLEDGE_URL`). Because the project's own `source_url` is always present, the footer is **robust to the claims payload not being loaded yet** (the deep-link race), unlike the evidence blockquote which needs `state.claims`. The roster also links each row (signatories → the pledge; "Own commitment" companies → their `dedicated_page_url`). `test_ratepayer_cards_have_sources_helper` guards that the helper exists and is called in both card renderers. **Don't** bury the source links back inside the collapsible evidence `<details>` — the always-visible footer is the fix.

## Non-signatory companies toggle (v1.21; roster changed in v2)

**v2 note:** CoreWeave, Crusoe and Prologis signed on 2026-07-23 and are no longer covered by this toggle. Only **Anthropic and Wonder Valley** remain genuine non-signatories. The membership is derived from the roster, so it corrects itself — but any prose naming the non-signatories will not, so check it after an expansion.

The Ratepayer view has a **"Show non-signatory companies" checkbox** (hidden `#rp-non-signatory-section`, unchecked by default) that reveals sites from companies that never signed the pledge at all — `ratepayerNonSignatoryProjects()` in app.js, the inverse filter of `ratepayerSignatories()`. These sites reuse `renderPrePledgeCard()` (same card, same source-footer helper) labeled "Not a pledge signatory" instead of getting their own render path. **Don't** attach a `ratepayer` assessment to any of these sites — the frozen rule (`_is_ratepayer_eligible` in refresh.py, `isPrePledgeProject` in app.js) is signatory + post-pledge-date only; this toggle is a comparison affordance, not a scope change to what gets assessed. See DESIGN.md's "Opt-in reveal" pattern — reuse this shape (hidden section + labeled checkbox) rather than a new tab for future adjacent-but-out-of-scope data asks.

**`refresh.py`'s audit had a signatory-blind bug (fixed 2026-07-15):** `_audit_missing_commitments` flagged "missing ratepayer" for every operational/construction project regardless of company, over-flagging ~18 non-signatory records (CoreWeave, Crusoe) that should never carry an assessment. Fixed by mirroring `isPrePledgeProject`'s signatory + date check in a new `_is_ratepayer_eligible` helper before generating `ISSUES.md`. If the medium-gap ratepayer count spikes again after adding a new company, check whether `_is_ratepayer_eligible` needs to account for it. **In v2 that helper takes a `{slug: signed_date}` map built from `signatories.json` (`_signatory_dates`) rather than a set of slugs** — see "Roster-driven eligibility" below.

## State utility tariffs view (v1.17)

A **fifth top-level tab** (`view-tariffs`, `#tariffs`) tracking state-regulated large-load / data-center electricity tariffs, scored against the design-element taxonomy from the DOE / Berkeley Lab (LBL) technical brief *"Electricity Rate Designs for Large Loads"* (Jan 2025). Modeled on the moratorium tab: stat tiles → LBL-element coverage breakdown (clickable, like the moratorium "reason breakdown") → filterable directory table → detail pop-out. Lazy-loads `data/tariffs.json` (NOT Leaflet). Data model is `Tariff` + `TariffsPayload` in [schema.py](../../schema.py); refresh.py mirrors seed→docs like the other payloads.

- **`TARIFF_PARAMETERS` is the frozen LBL taxonomy** — 17 design elements in 5 groups (`TARIFF_PARAMETER_GROUPS`): Eligibility & Applicability, Contract Size, Contract Duration & Exit, Energy Source, Other. Mirrored to `app.js` as `TARIFF_PARAMETERS` / `TARIFF_PARAMETER_LABELS` / `TARIFF_PARAMETER_GROUP_OF`, guarded by `test_tariff_parameters_match` (+ label/group parity). Adding an element = BACKLOG entry + the Python/JS constants + group mapping, same drill as THEMES/delivered. The store is **sparse**: a tariff only lists elements it addresses (`{status: included|partial, detail, source_url?}`); the detail pop-out iterates the full 17 and renders the gaps as "Not addressed", so "met or not" shows without storing a row for every absence.
- **Status vocab `TARIFF_STATUSES` = `approved` / `proposed` / `rejected`** (the user's "passed/proposed/rejected"). `test_all_three_statuses_present` asserts ≥1 of each so the directory reads with all three. The one `rejected` example is the **federal** FERC Talen/Amazon Susquehanna co-location ISA (Docket ER24-2172, rejected Nov 2024) — the LBL brief itself references co-location (FERC AD24-11-000), so it's on-topic even though it's not a state tariff; it's flagged as federal in its `summary`/`tariff_type`.
- **Source discipline.** Every tariff carries `source_url` + `source_title`; `additional_terms` and `legislation` each carry their own URLs. Sources were **link-checked (200) before commit** per the active-links rule; two bot-blocked URLs (mississippitoday.org homepage, a ferc.gov news page) were repointed to live equivalents. `test_prioritizes_gov_sources` asserts ≥60% of primary sources are .gov/LBL. The 11 LBL-appendix tariffs use the LBL brief PDF as a guaranteed-live `source_url` where no confirmed PUC docket URL was available — the brief is the authoritative DOE source documenting them, and `docket_number` carries the case ID regardless.
- **`legislation`** links state laws that authorize/influenced a tariff (Ohio HB 15 → AEP Ohio; Texas SB 6 → the PUCT large-load rule; Virginia SCC initiatives → the GS-5 rate class). Builder script that encodes the dataset: `.agent_outputs/build_tariffs.py` (idempotent; re-run to regenerate `data/seed/tariffs.json`, then `python refresh.py`). Coverage is curated, not all-50-state — many states have no data-center tariff yet, an honest absence the footnote calls out.
- **`jurisdiction_level`** (`state` | `federal`, default `state`) segregates the one FERC co-location case (Talen/Amazon Susquehanna) from the state-tariff stats: federal records are EXCLUDED from the "Approved/Proposed/Rejected" tiles and the "States covered" tally, surfaced instead in a separate "Federal cases" tile + a `FED` badge in the directory (`isFederalTariff()` in app.js). Keeps a federal case from reading as a state tariff. Guarded by `test_dataset_is_predominantly_state_level` / `test_federal_cases_are_clearly_federal` + the `TestTariffsView` e2e.
- **`resources` is a typed `SourceResource` list** (`{url: HttpUrl, title}`), NOT `list[dict]` — the detail renderer assumes both fields, so a missing/empty URL must fail at `refresh.py` not silently render a broken link. `additional_terms` / `legislation` are likewise typed sub-models.
- **Colors are design tokens, not hard-coded.** `--tariff-{approved,proposed,rejected,included,partial,federal}[-soft]` live in BOTH the `:root` and `[data-theme="dark"]` blocks (literal values, mirroring `--stance` / `--delivered`). **Don't** alias them via `var(--stance-*)` in `:root` only — a custom property whose value is `var(...)` does NOT propagate the dark override to descendant elements (the alias computes correctly on `:root` but children inherit the light value); use explicit literals in both blocks.
- **Directory rows are keyboard-accessible** (`role="button"`, `tabIndex=0`, Enter/Space → `showTariffDetail`), not mouse-only. `test_row_opens_detail_via_keyboard` guards it.
- **html2pdf (moratorium PDF export) is lazy-loaded** via `loadHtml2Pdf()` in app.js on first export click, NOT a blocking `<script>` in `<head>`. The blocking CDN script made every `page.goto(..., "load")` in the e2e suite wait on cdnjs (a flakiness + SRI-failure source). **Don't** move it back to `<head>`. The SRI hash lives in the `HTML2PDF_SRI` constant.

## Moratorium stat tiles — jurisdiction breakdown (v1.18)

The four stat tiles (Total / Enacted / Proposed / Failed) each show a secondary breakdown line (`<span class="rp-stat-breakdown">`) listing counts by `jurisdiction_type` in order: **city → county → state → federal**. The helper `_jurtypeBreakdown(moratoriums)` in [docs/app.js](../../docs/app.js) filters out zero-count types so only populated levels appear. Order is hardcoded; change the array literal in `_jurtypeBreakdown` if the order preference changes.

## Moratorium detail modal (v1.19)

The moratorium detail was converted from an inline `<aside>` (toggled with `hidden`) to a full modal overlay — same pattern as the tariff detail modal. Structure:

```html
<div id="moratorium-modal" class="moratorium-modal" hidden>
  <div class="moratorium-modal__backdrop" data-moratorium-close aria-hidden="true"></div>
  <aside id="moratorium-detail" class="moratorium-detail moratorium-modal__dialog" role="dialog" aria-modal="true" …>
    …
  </aside>
</div>
```

CSS class `.moratorium-modal` mirrors `.tariff-modal` (fixed overlay, backdrop blur, scroll lock via `body.moratorium-modal-open`). The dialog uses `.moratorium-modal__dialog.moratorium-detail` to override the inline card layout. Animation, focus trap, backdrop-click-to-close, Escape-to-close, and return-focus-on-close all follow the tariff modal pattern exactly — copy that pattern for any future detail panel that needs full-screen treatment.

The modal also surfaces three previously unused fields: `effective_date` (shown when present and distinct from `enacted_date`), `policy_type` (shown when present), and `key_stakeholders` (a grouped chip section; hidden when absent). The "Opposed" stakeholder group gets a subtle red tint via `[data-category="opposed"]` CSS.

**`badge-reason-*` CSS class drift (found + fixed 2026-07-15).** `MoratoriumReasonType` in schema.py is `energy | water | air_quality | noise | transparency | equity`, but `docs/styles.css` still had `.badge-reason-pollution` / `.badge-reason-planning` — an old taxonomy's names, from before the enum was renamed. Neither `air_quality`, `noise`, nor `transparency` had a matching CSS rule, so those badges silently fell back to the base `.badge` style with no color and, worse, no margin — three of the six "Key reasons" chips in the detail modal ran together as one unreadable word. Nothing caught it: unlike THEMES/DELIVERED_STATUSES/RATEPAYER_STATUSES, `key_reasons` has no Python↔JS parity test, and CSS class names aren't type-checked. Fixed by renaming the classes to match the live enum and adding the missing `noise` rule. If a 7th reason value is ever added, grep `docs/styles.css` for `badge-reason-` explicitly — don't assume the type-checker or an existing test will catch a mismatch here.

## Shared export helpers in app.js (v1.19)

All PDF exports across all six tabs use three shared helpers in `docs/app.js`:

- **`_exportToPDF(title, bodyHtml, filename)`** — wraps content in a styled div and calls the lazy-loaded `html2pdf` lib.
- **`_pdfTable(headers, rows)`** — builds an inline-styled HTML table string for use in `_exportToPDF`.
- **`_triggerDownload(csv, filename)`** — creates a Blob, fires `<a>.click()`, and revokes the URL. Filename accepts `"TODAY"` as a literal substring, which is NOT replaced — callers must supply the dated filename directly.

Per-tab export functions:
- `exportComparisonToPDF()` / `downloadMatrixCsv()` (Comparison)
- `downloadExplorerCSV()` / `exportExplorerToPDF()` (Explorer — respects current filters via `_filteredProjects()`)
- `downloadRatepayerCSV()` / `exportRatepayerToPDF()` (Ratepayer)
- `downloadMoratoriumsCSV()` / `exportMoratoriumsToPDF()` (Moratoriums — respects status + type filters)
- `downloadTariffCSV()` / `exportTariffsToPDF()` (Tariffs — respects status + state filters)
- `downloadAggregateCSV()` / `exportAggregateToPDF()` (Aggregate — uses `buildCompanyRollups()` + `buildStateRollups()`)

## `wireBtn` helper (v1.19)

```js
function wireBtn(id, handler) {
  const btn = document.getElementById(id);
  if (!btn || btn.dataset.wired === "1") return;
  btn.dataset.wired = "1";
  btn.addEventListener("click", handler);
}
```

One-liner for wiring a button by id with double-wiring guard. Use this for all new export or action buttons; don't inline the guard repeatedly.

## Launch / preview ritual + performance (v1.20)

The in-app **browser pane renders at a 0×0 viewport in some environments** (blank
no matter what; `navigate` often denied). Don't rely on it. To launch/preview:

- **Interactive, shareable:** `python3 tools/build_preview.py --verify` bundles the
  whole SPA into a self-contained `.preview/dashboard.html` (inlines styles.css,
  embeds every `data/*.json`, patches `fetchJson` to read the embedded data), then
  **publish that file as an Artifact**. Runs fully client-side; only the lazy Leaflet
  map (Explorer) + html2pdf export break under the artifact CSP — every other tab works.
- **Quick visual check:** headless Playwright — self-serve `docs/` with `http.server`,
  click a tab, `screenshot`, `SendUserFile`.
- **Do this on every new commit / PR.** `.githooks/post-commit` auto-rebuilds the
  bundle (needs `git config core.hooksPath .githooks` per clone; `.preview/` is
  git-ignored). The Artifact *publish* is a manual (Claude) step — a git hook can't do it.

**Performance baseline (GitHub Pages, gzipped/CDN):** first paint FCP ~340 ms · 6
requests · ~202 KB. Code-splitting works — first paint loads only index + styles +
app.js + the preloaded `companies.json`/`claims.json`; `projects`/`responses`/
`moratoriums`/`tariffs` lazy-load per tab. No images or web fonts (system stack).
**Keep it that way:** no web fonts, no un-optimized images, keep new heavy data
lazy-per-tab (never preload it). Regression signal: first paint > ~500 KB or > ~12
requests. Optimization ideas in [BACKLOG.md](../../BACKLOG.md).

## Pledge-first landing + civic palette (v2; tab placement revised in v2.1)

`#overview` is the **default view** (`DEFAULT_VIEW_NAME` in app.js, hoisted
above `state` because `state` initializes from it and would otherwise hit the
temporal dead zone). Comparison gained an explicit `#comparison` hash — it had
been the bare-root view, and demoting it without one would have left it
un-linkable.

**v2.1: the landing band moved from header chrome into its own "Overview" tab.**
Originally (v2) the band sat above the tab bar, inside `<header>`, on every
view — which meant the tab bar itself was pushed below the fold on load and
needed a scroll to reach. It now lives in `#view-overview`, a normal `.view`
section in `<main>` selected by `#tab-overview`, the first tab and the new
`DEFAULT_VIEW_NAME`. `#ratepayer` (the pledge's own tab: commitments, coverage,
roster, scorecard) is no longer the default — it's one click away, same as
every other tab. The header is now just the title row + tab bar, so every tab
is reachable without scrolling regardless of which one is active.
`activateView()` triggers the same `loadRatepayerView()` loader for both
`"overview"` and `"ratepayer"`, since the Overview tab's stat tiles / coverage
bar / meters / state strip need the identical projects + signatories +
coverage payload the Ratepayer tab does — there's no separate fetch path to
keep in sync. `.topbar` is not `position: sticky` (only `.tabbar-sticky` is);
that stayed true across both layouts.

**It is not four stat tiles.** An early cut was, and four numbers said nothing
about shape. It now carries a proportional roster bar (the coalition is 63%
rural co-ops), per-commitment meters (how thin the site evidence still is), a
50-state strip (how partial coverage is), and a dated activity feed. Every
figure renders from data — `test_landing_numbers_come_from_data_not_markup`
asserts no roster count is baked into `index.html`, because the roster moves.
*(2026-08-24: deliberately reversed for Home at the user's direction — the
shape graphics moved into the Pledge tab and Home became a numbers-band
briefing. See "Home as a minimal briefing" below.)*

**Palette: cool paper / near-black ink / one deep signal blue.** The first cut
adopted the source page's cream-and-gold and read as a consumer AI product;
this is a public record. What carries the reference is the *structure* — Roman
numeral commitments, letterspaced kickers, display serif. Token names changed:
`--accent-gold` / `--accent-gold-bright` / `--band-gold` are gone, replaced by
`--accent-mark` (text-safe) / `--accent-rule` / `--band-accent`.

**Compute contrast, don't eyeball it.** The source page's ochre is 2.96:1 on its
own cream — below both the 4.5:1 small-text and 3:1 large-text floors. It was
in the spec as `--accent-gold` and would have shipped unusable. Every token in
the current palette was checked before landing.

`--font-display` is a **system serif stack**; the no-web-fonts guardrail is now
enforced by `tests/test_perf_budget.py`, not just documented.

The global `h4` rule sets `text-transform: uppercase` + sans + muted. Any new
display heading using `<h4>` must override all three (`.rp-commit-title`,
`.rp-subhead` do) or it renders as an eyebrow label.

## State panel (v2)

Deep-linkable at `#state/XX`, following the tariff-modal pattern exactly
(backdrop, Escape, focus trap, return-focus). Assembled entirely from records
collected for other views — no new record type backs it.

- It **lazy-loads moratoriums + tariffs on open**, because a visitor can arrive
  from the landing band without ever having opened those tabs, and a panel
  showing "no tariffs" because the payload had not loaded would be a lie.
- **Every section renders even when empty.** AK / MT / SD have a governor
  signature and nothing else; that *is* the answer and is stated, not hidden.
- **Read the state code from the hash BEFORE calling `activateView`** — it
  rewrites the hash to `#ratepayer`, so reading afterwards yields `"yer"`. This
  cost a debugging cycle.
- `"XX"` is the sentinel a few records use for virtual / multi-site
  partnerships with no physical location. It must never become a state chip
  (`NON_GEOGRAPHIC_STATE` in app.js).

## e2e: the comparison pane is hidden by default now (v2)

28 tests broke at once on `wait_for_selector("#matrix-body tr")` — the rows are
in the DOM but the pane is `hidden`, so the default `state="visible"` wait times
out. This is the same trap CLAUDE.md already documents for the Community pane.
Those tests now navigate to `/#comparison`, which is also what a real reader
does. **When you change which view is default, every test that `goto("/")` and
then waits on another view's DOM will fail — route them through the hash rather
than loosening the wait.**

## One section language, one accordion (v2.2)

Every tab had grown its own section chrome. Five heading scales
(`.summary-section > h3` — which had **no CSS rule at all** and just inherited
the global serif h3; `.agg-section-heading` at 1.05rem sans; `.hot-rail-title`
at 1rem sans; `.matrix-help` with no heading; `.rp-section > h3` at 1.1rem) and
**three unrelated `<details>` skins** (`.directory-section` a filled button bar,
`.china-context-section` an accent-left callout, `.rp-roster-details` a bare
bold summary). Six tabs that read as six products.

The Ratepayer view's shape won — display serif at **400** weight, muted 64ch
dek — and everything else is aliased onto it in the SECTION LANGUAGE block in
[styles.css](../../docs/styles.css). Legacy class names were aliased rather than
renamed so no JS selector or test id had to move; the ones that ended up with
**zero** remaining markup (`.summary-section`, `.view-description`,
`.agg-section`, `.agg-section-heading`) were then deleted outright.

**`.acc` is now the only collapsible-section component.** Markup contract:

```html
<details class="acc" [open]>
  <summary><h3 class="acc-title">…</h3><span class="acc-count"></span>
           <span class="acc-chevron" aria-hidden="true"></span></summary>
  <div class="acc-body">…</div>
</details>
```

Five rules that are load-bearing:

- **The heading goes INSIDE the `<summary>`.** `<details>`/`<summary>` supplies
  the expand semantics natively (no `aria-expanded` bookkeeping), and the inner
  `<h3>` keeps the section in a screen reader's heading list. Don't hoist it out.
- **Never put a button in the `<summary>`.** A click anywhere inside a summary
  toggles the panel — the old `.directory-section` shipped its CSV/PDF buttons
  there and collapsed the table out from under the reader on every export
  click. Toolbars go in `.acc-body`; `.table-controls` is styled for exactly
  that.
- **`setAccCount(id, n, singular, plural, note)`** writes the summary chip so a
  *collapsed* panel still says how much is inside. **Only a non-number clears
  it** (`Number.isFinite`); `0` renders as "0 records" — see "Zero is a result;
  missing is not" below. Pass `plural` for anything that doesn't take a bare
  `+s`; the first cut shipped "302 signatorys" and "13 companys". Pass `note`
  for a count sourced from an external list, which must carry its as-of date.
- **`openAccordionsFor(node)` before any programmatic scroll.**
  `goToPledgeTarget()` calls it, because a smooth-scroll to a collapsed section
  lands on a closed bar and reads as a broken link. It walks *all* ancestors, so
  a nested accordion opens too.
- **Collapsing a section breaks every e2e test that waits on its contents.**
  Same hidden-pane trap CLAUDE.md already documents twice (Community pane, v2
  comparison default): children of a closed `<details>` are attached but not
  painted, so `wait_for_selector` needs `state="attached"` and
  `inner_text()` returns `""` — read `text_content()`, or click the summary
  first when the test is about what the reader sees.

**The pledge band is collapsed by default** (`.acc--band`, the dark variant with
band-palette hairline and marker). The five commitments are reference material a
returning reader has already read; the live content below is what they came back
for. `test_commitments_render_as_the_pages_spine` asserts the collapsed default
*and* that expanding works, so flipping it back is a deliberate act.

`#hot-rail` deliberately did NOT become an accordion: it renders only when
contested sites exist, and a collapsible whose whole existence is conditional
reads as a bug when it vanishes.

## Sub-tabs are for alternatives; accordions are for sequences (v2.2; group count superseded by v5)

> v4 (2026-09-23): the Aggregate group is gone with its tab; only
> "Tracked sites" remains. See "IA v4" above.

`.subtabs` / `SUBTAB_GROUPS`. The rule that decides which to reach for:

> **Would a reader ever want two of these on screen at once?**
> Yes → accordion. No → sub-tab.

Sub-tabs exist in exactly **two** places, and `test_only_two_subtab_groups_exist`
guards that number — a third group has to argue against the test above:

- **Ratepayer → "Tracked sites"** — Assessed / Awaiting assessment / Before the
  pledge / Never signed. These were four sibling sections; they are four
  *bucketings of one site list*.
- **Aggregate** — By company / By signatory category / By state. Three rollups
  of the same numbers.

The Moratoriums and Tariffs tabs kept accordions on purpose: you read the charts
**and** the directory. Sub-tabs there would hide half the tab from Ctrl-F and
from the PDF exports, which walk the DOM.

Mechanics, mirroring `DETAIL_TABS`:

- **Everything iterates `SUBTAB_GROUPS`.** Adding a cohort = markup + one array
  entry. Ids are conventional: `subtab-<group>-<key>` / `subpane-<group>-<key>`.
- **`setSubtabCount()`, not `setAccCount()`.** A pill is a bare number;
  "39 sites" is right in an accordion summary and far too wide in a tab.
  The accordion summary above the strip carries the **combined** total, so
  collapsing it doesn't hide the count entirely
  (`test_accordion_summary_totals_every_cohort` pins summary == sum of pills).
- **Panels toggle via the `hidden` attribute**, and `.subtab-panel` sets
  `display: block` — safe only because the global `[hidden]` rule carries
  `!important`. See the `[hidden]` trap.
- **Arrow keys move between tabs**, per the ARIA tablist pattern.
- **Collapsing content into a sub-tab breaks every e2e test that waits on it**,
  same as accordions — four aggregate tests failed at once here. Fix by
  clicking the sub-tab (what a reader does), not by loosening the wait.

**The "Show non-signatory companies" checkbox is gone**, replaced by the
"Never signed" sub-tab. CLAUDE.md previously called that checkbox the documented
opt-in-reveal shape; a sub-tab is the same opt-in (Assessed is the default, you
have to choose the cohort) while sitting where cohorts actually compare. The
scope rule it protected is unchanged and enforced where it always was —
`_is_ratepayer_eligible` / `isPrePledgeProject` still refuse to attach a
`ratepayer` assessment to a non-signatory site.

## The Ratepayer view's own stat row is gone (v2.2)

`#rp-stats` / `renderRatepayerStats()` — "N signatories tracked in depth / sites
assessed / site-specific commitments" — was removed, along with the
"Companies tracked in depth" roster (`#rp-tracked-roster` /
`renderRatepayerRoster()`) under Coverage. Both predated the v2 roster expansion
and reported numbers the Overview landing band now reports better and
roster-wide. `companyHasRatepayerClaim()` and
`RATEPAYER_DOE_TRACK_SIGNATORIES` died with them (the roster record's own
`signed_track` is the source of truth for which track a company signed on).
`RATEPAYER_CLAIM_KEYWORDS` survives — it still backs the company-wide claim
fallback on scorecard cards.

Four e2e tests went with them. **Don't reintroduce a per-view stat row that
restates roster figures**: two places reporting the same count is how the
"11 signatories" tile sat stale through an expansion that tripled the roster.

## IA v4: seven tabs, a playbook, and copy rules (2026-09-23, user-directed)

**Tabs:** Home · The Pledge · Companies · Moratoriums · Tariffs & Rate Cases
· Policy Playbook · Sites. The "By State & Company" tab (`#aggregate`) is
gone. Its tables moved to the tab that owns each one's question:
- the per-company table goes to Companies, replacing a stat strip that
  repeated its total row;
- per state goes to Sites;
- per signer category and per utility go to The Pledge.

`#aggregate` redirects to `#comparison`. `loadAggregateView()` runs for
those three views, never for Home (first paint). The `agg` sub-tab group
died with it, so **one** sub-tab group exists now (`rp-sites`), and
`test_only_one_subtab_group_exists` guards that. Two tabs with overlapping
numbers is the "11 signatories" failure waiting to happen; before adding a
tab, name the one question only it answers.

**Policy Playbook** (`#policies`, was "Policies & Agreements") leads with
`Policy.principles`, a frozen 9-value vocabulary of what a policy asks OF data
centers: pay own grid costs, binding community benefits, conditioned tax
breaks, water, no secret deals, local siting say, new supply for new demand,
environmental review, study. **Environmental review and study were one value
("states review large projects") until the user asked what it meant:** a
permit condition with public comment and an advisory council are different
asks, and one label hid both. When a principle needs a sentence to explain,
it is probably two principles. Rules for the vocabulary:
- **Curator-assigned, primary first, max 3.** A keyword pass over-tagged
  (six principles on one EO, none on others), so every record was assigned
  by hand. Don't regex-classify principles.
- **Not THEMES.** THEMES is what companies *give*; principles are what
  governments *require*. Records carry both.
- **Card examples rank by primary principle, then public instrument, then
  date,** or one broad order (VA EO 22, NV EO 2026-005) headlines every card.
- **"Latest actions" merges in governor orders filed on the Moratoriums tab**
  (`isGovernorMoratorium`), since readers look for NY EO 62 here too.

**Copy rules (the user's slop pass):**
- Say what a section holds in one plain line, or say nothing.
- No "Every record links to its source," and no "Click a row to…" manuals.
- No "X, not Y" hedges ("a coverage fact, not a verdict").
- No "by X and Y" headings ("Commitments by company and theme" became
  "Published commitments").
- No fragment-pair notes ("A separate instrument", "Enacted, proposed &
  failed").
- Empty states are one short sentence.
- Stat tiles size to their content (`flex: 0 1 auto`); a row of four numbers
  never stretches to full width.

**Type system (enforced by tests/test_type_scale.py):**
- **Two families only**, `--font-sans` and `--font-serif`. The audit found
  five: a stray Georgia stack, `monospace` on bill ids, and Leaflet's
  Helvetica Neue / Lucida Console. Leaflet's CSS lazy-loads after ours and
  wins ties, so its override needs a `body` prefix.
- **One size scale:** nine `--fs-*` tokens, from 11px labels to the 1.55rem
  masthead. It replaced 35 distinct sizes. A new size is a design decision:
  add a token or reuse one.
- **No `clamp()` display sizes.** The pledge band's title and Roman numerals
  scaled past the site title.
- **Uppercase labels share one weight (600) and one tracking (0.05em).**
- Measure before restyling: a Playwright walk over every visible text node
  per tab, counting (family, size, weight, case) combinations. It went from
  79 combinations to 37. Re-run it after any visual change.

**The 2026-07 "enhanced high-priority" moratorium batch is poisoned.** 5 of
its 9 records were fabricated: WA SB 5982, MA S.2455, VT H.149 and ID HB620
are unrelated real bills, and OK HB 2992 was a different law. 3 more had
wrong facts: Maine LD 307 was vetoed, not enacted; Denver's sponsors and vote
were wrong; MN HF 4888 is a pending 2026 bill. Only NY checked out. The
shape: a real bill number with an invented data-center narrative and a
homepage source. One fetch of the legislature's bill page catches it every
time. Treat any record from a bulk generation pass the same way, and check
the 19 remaining homepage-sourced moratoriums (the ratchet list in
tests/test_policies.py) with the same method.

## IA v3 — Home as the record's front door (2026-08-03)

Tab labels changed, **hashes did not** (deep-link compatibility): Home
(`#overview`, default) · The Pledge (`#ratepayer`) · Companies (`#comparison`)
· Moratoriums · Tariffs & Rate Cases (`#tariffs`) · Sites (`#explorer`) · By
State & Company (`#aggregate`). Home is no longer pledge-only: new
masthead/dek introducing all five record types, a **"What's next"** list
(dated docket milestones, soonest first — the user question the dashboard
exists to answer), the activity feed, and five reader paths (added: rate
watchers → `ratecases` target, planners → `moratoriums` target). The tariffs
tab gained the rate-cases section; the state panel a fifth section (e2e
updated 4 → 5); the aggregate a fourth sub-tab (CSV/PDF exports cover it —
the derived one-section-per-subtab e2e test caught the gap the same day it
was created, exactly as designed).

## Home as a minimal briefing (2026-08-24, user-directed)

The user asked for a landing "simpler, like an industry or news website —
tabs go into the specifics," and picked the minimal-briefing cut over a
news-grid or tighten-in-place option. Home (`#overview`) is now: one-line dek
+ `.pledge-hero-fineprint` disclaimer · a **five-tile numbers band** spanning
the whole record (orgs signed / governors / sites assessed / moratoriums /
tariffs + rate cases) · **"What's next" beside "What changed"**
(`.home-latest`) · **six `.home-card` tab cards** ("Explore the record", one
per non-Home view). ~1,650px tall, was ~2,430. Rules that keep it that way:

- **This deliberately reverses the v2 "it is not four stat tiles" decision
  for Home only — the shape graphics MOVED, they did not die.** The
  proportional roster bar + key now render in the Pledge tab's Coverage
  section, where they **replaced** the `rp-category-stats` tiles (same
  numbers twice in one section); the 50-state strip replaced `rp-state-chips`
  there (two state grids in one section, and the strip's all-50 honesty is
  the documented keeper). The commitment meters were deleted outright because
  `rp-commitments` already renders richer per-principle tallies. **Don't**
  reintroduce a second state grid or category-count tiles beside the bar,
  and **don't** grow Home panels back — depth belongs to the owning tab.
- **`coverage.json` now carries a `totals` block** (len() of each payload,
  federal records INCLUDED — the state cells exclude them by design, so
  summing the grid client-side undercounts: 123 vs 124 moratoriums, 10 vs 12
  rate cases). The numbers band and card counts read `state.coverageTotals`
  instead of fetching moratoriums/tariffs payloads; first paint is unchanged.
  Guarded by `test_coverage_totals_include_federal_records`.
- **"What's next" is capped** at `HOME_WHATS_NEXT_MAX` (6) with a 2-line
  `-webkit-line-clamp` on `.wn-text`; the `#whats-next-more` link ("All N
  docket milestones →") routes to the `ratecases` target where
  `renderRateCases()` shows every milestone in full. The full regulator prose
  ships on the Tariffs tab, never on Home.
- **The five persona pathway cards are gone**; the `.home-card`s (static
  markup, wired once on boot via `wirePledgeTargets`, counts filled by
  `renderHomeCards()` as payloads land) replaced them. `PLEDGE_TARGETS`
  gained anchor-less `pledge` / `companies` / `tariffs` / `aggregate`
  entries. `test_home_cards_cover_every_other_tab` derives the expected card
  count from `VIEWS.length` — don't hardcode a 6.
- **Card counts and tile numbers are data-only**: markup placeholder is
  "&mdash;", and the cards test asserts no count is still "—" after load,
  alongside the existing no-hardcoded-numbers test.
- The e2e tests moved with the graphics (`/#ratepayer` navigation, strip-cell
  selectors instead of `rp-state-chip`); the pathway-card tests became
  stat-tile tests (`data-path-target='roster'` / `'scorecard'` on the band),
  preserving the collapsed-target-opens guard.

## One type scale, one accent (2026-08-24, user-directed)

The first cut of the minimal-briefing Home shipped with the inherited v3
chrome and the user called it out: four visible font families, a site title
smaller than the page headings, red label chrome everywhere, and a Home that
spoke a different component language from its own tabs. The fixes are
system-wide rules, not Home styling — hold every future view to them:

- **Exactly two font families.** `--font-sans` (body, UI, labels, dates,
  counts) and `--font-serif` (masthead, headings, the band). `--font-display`
  and `--font-mono` are deleted; the mono kickers/dates/badges all moved to
  sans with letterspacing (+ `font-variant-numeric: tabular-nums` where
  digits columnize). Reintroducing a third family is a deliberate act against
  this section, not a styling choice.
- **The masthead outranks everything.** h1 1.5rem > h2 1.4rem > `.acc-title`
  1.28rem > h3 1.2rem. No view heading may exceed the site title — the old
  Home hero (2.6rem display serif + mono kicker) is the cautionary example.
  Every view opens with the same `.hero` block (h2 `.hero-title` + one-line
  `.hero-dek`); Home adds only `.pledge-hero-fineprint` under it.
- **One structural accent: `--accent`** (navy light / amber dark).
  `--accent-mark` / `--accent-rule` are deleted — they had become synonyms.
  Red now appears ONLY through semantic status tokens (failed / rejected /
  negative / shortfall); if chrome needs an accent it uses `--accent`, and if
  something red shows up outside a status badge, that's a bug.
- **Section labels are muted, not accented.** `.pledge-panel-h`,
  `.home-card-tag`, `.acc-count` are `--text-muted` uppercase sans — labels
  identify, they don't signal.
- **One stat-tile component.** Home's `.pledge-stat` now mirrors `.rp-stat`
  (boxed, hairline border, 3px `--accent` top, sans-700 numeral at 1.55rem in
  the accent color). Don't invent a per-view tile style; if a view needs a
  stat row, copy the `.rp-stat` shape.
- **Lists over boxes for reading flows.** `.wn-btn` milestone rows are
  hairline-separated rows, not bordered cards — box chrome is for
  navigation targets (`.home-card`), not for every list item.

## Civic palette v3 — whitehouse.gov, contrast-computed (2026-08-03)

> **Partially superseded 2026-08-24** (see "One type scale, one accent"
> below): the red mark/rule tokens and the second display-serif stack are
> gone. The navy family, the band, and the contrast-computing method stand.

The user directed the theme to follow whitehouse.gov's colors and type. The
palette was **extracted from the live site's own CSS presets** (browser
`getComputedStyle` + stylesheet walk), not eyeballed: deep navy `#0D132D` /
`#151A30` / `#141F4D`, charcoal ink `#293340`, signal red `#B50000`, amber
`#FFBD00`, stone `#E8E6E0`, pale-gray `#D9DEE8`. Every text pairing was
contrast-computed before landing (red on white 7.08:1; amber on white 1.68:1
— so **amber is a mark color on light surfaces and a text color only on the
navy band**, where it hits 10.9:1; dark-mode muted 7.28:1). Dark mode is the
navy family, not gray. Fonts: whitehouse.gov uses Instrument Serif/Sans —
the stacks now **name those first and fall back to system faces**, which
costs zero bytes and engages when a reader has them installed; the no-web-font
budget test still enforces no `@font-face`. If the user later wants the real
faces, two self-hosted WOFF2 subsets (~60 KB, +2 requests) are the price —
that is a deliberate budget decision, not a default.

## Comparison view is summary-pop-out, not claims-list (v1.3)

The Comparison view's job is to surface "what does each company actually publish about community engagement?" — not to be a global claim browser. v1.0–v1.2 had a global claims list under the matrix that filtered when you clicked a cell; v1.3 removed that entirely. The matrix now opens a per-company pop-out (`#company-detail`) on row / cell click, showing:

- A curated 1–2 paragraph `summary` (new optional field on `Company`, see `schema.py`) describing how the company frames data-center community engagement.
- A link to `dedicated_page_url` (the company's main community/engagement page on their own site).
- Counts of recorded claims + tracked projects for that company.
- Last-reviewed date.
- A "View this company's projects →" CTA that switches to the Explorer view with the company filter pre-set (via `state.explorerFilters.company` + `syncExplorerFilterUIToState()`).

**Don't** restore the global claims list. The user explicitly cut it because the matrix should answer "does this company speak to this theme at all?" + "what's their overall framing?", not "scroll a wall of every claim by every company". Claim-level browsing happens in the Project Explorer's per-project Claims tab. **Don't** make the company summary an aggregation of the per-company claims either — the summary's editorial value is meta-commentary on the company's framework / page structure / gaps (e.g. "Anthropic has no published framework — they don't operate their own data centers"), which is information that doesn't fall out of the claim records.

The `summary` field is **Optional** in the schema. An empty summary surfaces a muted "No community-impact summary captured for this company yet" placeholder — that's editorially honest for a future entity we haven't researched yet. **Don't** lazy-fill summaries by templating from the claims; spend the curation time.

## Matrix is checkmark-only (v1.2) — SUPERSEDED by v5 (see "v5 tab pass" below)

`renderMatrix()` in [docs/app.js](../../docs/app.js) emits `<span class="count check">✓</span>` for **every** populated cell, regardless of the underlying claim count. The matrix answers a binary question — "does this company speak to this theme at all?" — and volume goes in the claims list below, not the matrix itself. The `aria-label` still carries the precise integer (`"6 Meta Jobs claims — click to filter"`) so screen readers get the count even when the visual is a glyph. **Don't** restore the digit-count branch: the v1.1 implementation surfaced volume in the matrix and the user explicitly cut it because the matrix should read at a glance. **Don't** drop the `aria-label` numeric — the visual is intentionally lossy. Tests `test_all_populated_cells_render_check`, `test_no_digit_only_cells_remain`, and `test_check_cell_aria_label_carries_numeric_count` guard the contract.

## Compact claim card variant (v1.1)

Claim cards have two visual modes driven by an opt-in `.compact` class on the parent `<ol class="claims-list">`:
- **Default** (Comparison view's main claims list) — full padding, 0.92rem font, box-shadow, large typographic curly quotes (`\201C` / `\201D`) wrapping the verbatim quote. The serif font on the quote is load-bearing — it signals "this is a quoted statement," not body copy.
- **Compact** (Project detail's Claims tab) — tighter padding, 0.85rem font, no shadow, same serif quote treatment but at 0.88rem. The card is supporting context for a project, not the headline read; visual weight should drop accordingly.

**Don't** drop the serif on `.claim-quote` in either mode — that's the editorial signal. **Don't** add the `compact` class to the comparison view's main list — that view IS the read.

## v5 tab pass: view-level sub-tabs, Companies depth, Sites contested (2026-10-08, user-directed)

The owner asked for sub-tabs on every tab, a Companies tab that "makes
sense" (it was all checkmarks and codes), a Sites tab that tracks contested
sites with local news and hearings, Policy Playbook renamed **Local Policy
Frameworks**, and rate cases reachable without scrolling. Spec:
[notes/specs/SPEC_V5_TABS.md](../../notes/specs/SPEC_V5_TABS.md).

- **Sub-tabs now exist at view level** on Companies (`co`), Sites (`sites`),
  Moratoriums (`mor`), Tariffs & Rate Cases (`tar`) and Local Policy
  Frameworks (`pol`), plus The Pledge's in-section `rp-sites`. This reverses
  the v2.2/IA-v4 "one/two groups only" cap at the owner's direction; the
  alternatives-vs-sequence test still decides what goes in a pane. Moratoriums
  splits Directory / Trends & concerns / Influence claims because the
  directory is what readers came for and the page ran 25 phone screens.
- **`VIEW_SUBTAB_GROUP` puts the pane in the URL**: `#tariffs/tariffs`,
  `#explorer/contested`, `#comparison/commitments`. The first key of each
  group is the default and keeps the bare hash. Read the sub-key BEFORE
  `activateView` (it rewrites the hash), same rule as `#state/XX`.
  `PLEDGE_TARGETS` entries with a `subtab` set it before scrolling, because
  an anchor inside a hidden pane has no box.
- **Charts inside a hidden pane need a re-park.** The moratorium timeline's
  scroll-to-recent ran while its pane was `hidden`; a `dcb:subtab` listener
  re-parks it when Trends is shown. Any new chart in a pane needs the same.
- **Companies: the matrix measures commitment DEPTH, not presence.** A cell
  is *Specific* (≥1 claim with a structured `metric`), *General* (claims, no
  figure) or *None found*, plus the claim count. Derived from the records,
  not a curator grade. Clicking a cell or theme header opens the quotes panel
  (strongest first: figure before none, then newest). This supersedes
  "Matrix is checkmark-only" — the owner cut the ticks because 13 of 15 rows
  were solid ticks and said nothing. Profiles (one card per operator) and
  Footprint (the totals table) are the other panes.
- **No codes.** `13A 7C 3O` became "3 operating · 7 building · 13 announced"
  (`statusWords`), and stance dots became "12 supportive · 14 mixed · 19
  critical" (`stanceWords`). A number without its word is a code.
- **Contested sites are derived** (`contestedReasons` / `isContestedSite`):
  a negative community response, a `contested` ratepayer assessment, a
  `contested`/`shortfall` delivery finding, or a `lawsuit` update. Shared by
  the Companies cards and the Sites Contested pane so their counts agree.
  The six-card "Recently contested" rail is gone; the pane lists every one.
- **`Project.updates` (typed `SiteUpdate`) is the site timeline** (BACKLOG
  decision 3, now made): date, kind (`hearing|vote|permit|lawsuit|filing|
  agreement|construction|news`), neutral title, optional summary/authority,
  `upcoming`, source. `siteTimeline()` merges it with the site's community
  responses; announced future dates lead, and an `upcoming` date that has
  passed renders "Outcome not yet recorded", never as still upcoming.
  Mirrored as `SITE_UPDATE_KINDS`/`SITE_UPDATE_LABELS`, parity-tested.
- **A timeline date is the EVENT date.** The validator caught four
  relative-day errors in one batch ("on Tuesday" in an article dated
  Wednesday). When the page states only its own publication date, the event
  ships as `kind: "news"` with a title phrased as reported, not as a dated
  vote or filing. `scripts/merge_v5_refresh.py` records every correction and
  drop with its reason.
- **claims.json is the deferred tier on every landing except Companies**
  (`ensureCompanyData` / `ensureClaimsData`). Home never shows a claim, and
  the v5 views pushed first paint to 258.6 KB. The cap went 250 → 275 KB the same day (owner-approved headroom); the deferral stays. `indexClaimsByProject` runs
  when either claims or projects land, so whichever arrives second builds
  the index. Views that quote claims (Pledge scorecard, Sites, totals)
  await or re-render on `ensureClaimsData`.
- **Map tiles:** CARTO's keyless basemaps now return an "API KEY REQUIRED"
  placeholder; the Sites map uses Esri's light/dark gray canvas (keyless,
  attributed). If tiles ever show a watermark, check the endpoint with curl
  and look at the PNG before debugging Leaflet.
- **Compact filter bars**: `.filter-bar--slim` rows; the select's first
  option says what it filters ("All states"), so the label is `.sr-only`.
  Tariff design elements became a filter select; their chips moved to the
  Rate-design elements pane.

## Home v6, tab order, Benefit Agreements tab, interaction cost (2026-10-08, owner-directed)

**Home renders from `data/home.json`**, a ~1 KB gzipped digest built by
`refresh.py` (`_build_home`): section totals, a mixed "Latest" feed (≤4 per
type, policies labeled by scope) and a "Coming up" list (≤3 per type, never
in the past). Coming up carries only dates a record states: rate-case
milestones and upcoming site events. Moratorium end dates were derived from
`duration_months` and came out a day or more wrong, so they are off until the
schema has a curated end date. First paint is
`index.html`, `styles.css`, `app.js`, `companies.json`, `home.json`: 142 KB,
5 requests. Every other payload loads after `dcb:home-ready`. The Python side
duplicates two JS rules, and an e2e parity test holds each pair together:
`_is_contested` ↔ `contestedReasons`, `_is_agreement` ↔ `isAgreementRecord`.

**Tab order:** Home · The Pledge · Local Policy Frameworks · Benefit
Agreements · Moratoriums · Tariffs & Rate Cases · Companies · Sites. Home
cards follow the same order (`test_sections_lead_with_numbers_in_tab_order`
derives it from `VIEWS`). On screens ≤960px the tab bar wraps instead of
scrolling sideways, and on phones it uses short labels (`.tab-long` hidden,
full name in `aria-label`). The UAT counted side-swipes to reach half the tabs
before this.

**Benefit Agreements (`#agreements`)** reads `policies.json`, with no payload
of its own. It shows `benefit_agreement` records plus company pledges to one
community; company-wide plans stay on Frameworks. `Policy.agreement_features`
is a frozen 9-value vocabulary (`AGREEMENT_FEATURES`, parity-tested) of what an
agreement's *text* contains: binding contract, dollar amounts, independent
oversight of the money, a numeric hiring target, a water cap, ratepayer
protection, public reporting, successor binding, clawback. The list comes from
the NAACP 2026 CBA template, the Lancaster PA agreement and Michigan HB 6137.
- **Each tag must be shown by one of the record's own `key_terms`.** Never tag
  from memory or from a news summary. An untagged record reads "Terms not yet
  reviewed", not "has none".
- **"Most complete" is derived, not picked.** It ranks signed agreements by tag
  count, then by stated value, then by date. Don't add a hand-written "best
  of" field; if the ranking is wrong, the tags are wrong.
- **A feature describes paper, not delivery.** Delivery stays in `delivered`,
  under the evidence bar in "Policies & Agreements tab".
- Opening a record from another view uses `openAgreement(id)`: it switches to
  All, clears filters and opens the card in place. There is no modal, so
  there is no invisible-modal trap.

**Interaction cost is measured and budgeted per device.**
`python3 tools/interaction_cost.py` cold-loads Home and walks 14 reader tasks
on mobile (390×844 touch), tablet (820×1180 touch) and desktop (1366×900). It
counts taps, swipes (0.75 of the visible area), side-swipes and typed queries,
in a `default` context and an `expanded` one (every section accordion open).
It writes `uat/interaction_costs.json` and appends a dated line to
`uat/interaction_costs_history.jsonl`. `tests/e2e/test_interaction_cost.py`
fails when any task exceeds `uat/interaction_budgets.json` for its device.
Lessons from the first run:
- **A collapsed section is cheap until it sits above the thing you want.**
  Forcing the Pledge accordions open pushed the scorecard from 4 swipes to
  68 on a phone, because the 300-row roster opens above it. Collapsed by
  default is right for long reference lists, and the roster now sits first
  (collapsed) because "did my utility sign?" is the most common question.
- **Count only section accordions in "expanded".** Forcing per-card
  `<details>` open measured a page no reader ever sees.
- **On a phone, a long list with no search costs swipes in the dozens.**
  Finding one site took 19 swipes, so Sites got a search box (`#f-q`, also
  serialized to `?q=`).
- **Measure after the network goes idle.** A lazy payload landing mid-measure
  produced one run with 19 phantom swipes and one with none.
- A table row whose tail overflows a scroll container is tappable once its
  leading edge shows; counting its right edge invented side-swipes.

## Oct 19 session: full site validation, withdrawn status, phone paging

**Every site re-validated.** Eight Haiku validators (17 sites each, stalest
first) re-fetched each record's sources and searched for news since capture.
One Sonnet pass turned the results into append-only changes. What it caught:
- **Two pledge assessments on pre-pledge sites.** Google Chesterfield VA and
  Stillwater OK were announced in Aug 2025 according to their own cited
  sources; the records said Mar/Apr 2026. The wrong date had made them
  "pledge era", so they were carrying `pledge_only` assessments the frozen
  eligibility rule forbids. When a record's date sits close to the pledge
  date, fetch its source's own dateline.
- **Company-level claims that no page contains.** Seven claims were removed
  because no page, live or archived, has their words. One was a "$50M
  community investment" that was really Microsoft's land price. Their shape:
  a fluent first-person sentence ("We engage early with local stakeholders —
  elected officials, residents…") citing a hub page (`/community/`) that has
  since 404'd. Treat a hub-page citation for a specific quote as a lead.
- **Scope mismatches,** such as statewide or multi-campus totals stored on
  one site. They are flagged per site in BACKLOG §3 (`#### site:<id>`), not
  silently changed.

**Link checks:** `check_links.py` counts 403 as DEAD. 122 of 487 URLs
"failed", but only 31 were really gone (404/410/DNS). Most of the rest were
bot walls (datacenterdynamics, openai.com, x.ai). Filter to 404/410 before
acting. Wayback rate-limits hard (429) after a few dozen requests: space
fetches 15–30 s apart. probe.py can't read most snapshot PDFs (compressed
fonts), but macOS PDFKit can, via JXA: `osascript -l JavaScript` with
`ObjC.import('PDFKit')` and `PDFDocument…string`.

**`withdrawn` project status (#78).** A withdrawn site keeps its record and
history. `isLiveProject()` drops it from the pledge scorecard cohorts and
from the investment/jobs/MW totals; it is still counted in `statusWords`. A
project whose developer changes, like Crusoe → Google at Cheyenne, becomes
two records: the old one `withdrawn`, the new operator's as a new record.
There is no `paused` status. A pause is a timeline update.

**Phone paging (#79).** Below 700px, `phonePageSize()` and
`showMoreControl()` page the long lists: Sites 20, Moratoriums 40, the
Pledge scorecard 10, Benefits' "Most documented" 5. A new filter or search
resets to page one. Desktop renders everything. A card the reader selected
always renders. Use the same helpers for any new long list rather than a
bespoke "show more".

## Local previews and startup requests (2026-11-05)

Opening `docs/index.html` as a file blocks JSON fetches and module imports in
the browser. Use `python tools/build_preview.py --verify`, then open
`.preview/dashboard.html`. That bundle includes both lazy modules (planning
guide and Elections), retains the viewport metadata and parses embedded JSON
only when its view needs it. Its verifier now exercises Elections and the
canonical legal-record link; a module import left unbundled fails the build.

Do not idle-prefetch projects, responses and claims on unrelated tabs. The
Elections cold load was competing with roughly 684 KB of unrelated JSON. Each
view already has explicit loaders; request-level tests now check after the first
render as well as before it. Measure through usable content, not just paint.

## One Policy tab; names, counts and Pledge order (2026-11-09, owner-directed)

From the UX audit (`notes/ux/2026-11-09/UX_AUDIT.md`) and its follow-up.

**Tabs:** Home · The Pledge · Policy · Moratoriums · Elections ·
Power Costs · Companies · Sites · International.

**Policy and Moratoriums.** Policy opens with nine topics. Its Agreements pane
includes signed agreements, terms, draft plans and evidence; Latest and Rules
remain alongside it. Moratoriums has its own directory, map and trends.
Keep old agreement and policy/pause hashes in `LEGACY_HASHES` so shared links
land on the same records. The data files and inclusion criteria are unchanged.

**One name per tab.** The tab label, the Home card title, the view's
`.hero-title` and the llms.txt name are identical. The tabs have no
short/long label variants. On phones, labels wrap inside an auto-sized
5-column grid. `test_tab_name_is_the_same_everywhere` enforces this.

**Matching counts.** Each Home card's number must appear in its tab's stat
row, sub-tab pills or dek. `test_home_card_numbers_match_their_tab` checks
it. If you change a tab's lead stat, change the card with it.

**Pledge order.** Roster and Coverage sit collapsed above Tracked sites, and
Tracked sites leads. The interaction budgets went up for this, and the
reasons are noted in uat.md.

**"Record at a glance" is gone.** The generated crawler summary and its
`static-summary` markers were removed; refresh.py only stamps
`dateModified`. Don't add a generated summary block back. Home is the
summary.

## 2026-11-06 — original file and native preview support

`docs/index.html` now supports direct file opening through generated classic
script adapters. `refresh.py` emits `docs/data/*.preview.js` from canonical JSON;
`tools/build_preview.py` emits module adapters beside their source modules and
still builds the standalone bundle. Regenerate and stage these alongside source
changes before committing. Hosted startup still uses ordinary JSON and dynamic
imports; adapters load only for file/native previews where those requests fail.
Tests compare adapters with their source and exclude generated copies from the
dead-CSS scan so stale duplicates cannot certify an orphan selector.

## v7: linked records, record URLs, one policy directory, LBL 2026 tariffs (2026-11-16, owner-directed)

Spec: [notes/specs/SPEC_V7_POLICY_RECORD.md](../../notes/specs/SPEC_V7_POLICY_RECORD.md). Owner picked "keep the record types, combine in the view."

- **Links between records are `related: list[RecordRef]`** (kind, id, relation, note) on Policy, Moratorium, Tariff and RateCase. Store a link on ONE record. `refresh.py` `_build_links` validates every target and writes `docs/data/links.json` with each link's inverse (`RELATION_INVERSE`). The older single-purpose fields (`related_moratorium_id`, `related_project_ids`, `related_tariff_id`, election `related_*_ids`) and `Tariff.legislation[].policy_id` feed the same graph. `RECORD_KINDS` / `RELATION_LABELS` are mirrored in app.js and parity-tested. Panels render "Related records" from links.json via `renderRelatedRecords`.
- **Every record has a URL:** `#moratorium/<id>`, `#tariff/<id>`, `#ratecase/<id>`, `#policy/<id>` (hands off to `?policy=`), `#site/<id>` (hands off to `?project=`), `#company/<slug>`. `RECORD_ROUTES` is the table; `test_every_record_kind_has_a_route` derives the expected kinds from `RECORD_KINDS`. Opening a record calls `setRecordUrl` (replaceState); closing calls `clearRecordUrl`, which does nothing while `state._routing` is set (the #72 rule). Table rows are role=button, so they don't nest links: the address bar and each panel's "Link to this record" carry the URL.
- **Policy → Rules lists moratoriums too** (`moratoriumAsPolicyRow`, `.is-moratorium-row`, type filter "Moratorium"), with a moratorium call-out (`#policy-moratorium-callout`). Moratoriums load only for the Rules and Latest panes (a perf test guards Topics). e2e tests that mean "a policy row" select `tr[role=button]:not(.is-moratorium-row)`.
- **Tariff elements follow LBL's Aug 2026 update**: 18 elements + 12 sub-elements (`TARIFF_PARAMETER_PARENT`) in four practice groups, with LBL's sample counts (`TARIFF_PARAMETER_LBL_COUNT`). Generated from `notes/specs/v7_work/taxonomy.py` by `gen_taxonomy.py`. Every credited element carries `verbatim` (tested). A sub-element without its parent fails validation. The directory shows the decision date, not an element count.
- **Power Costs leads with `brief`** (TariffsPayload): dated, sourced paragraphs with named record links (`note` is the link text, because the policy payload isn't loaded on that tab). It is curated, not generated; refresh it when a date in it passes. Stat row cut to three numbers. The first rate case now sits within ~1.5 screens on desktop (test updated, owner-directed).
- **`commission_order`** is a new Policy instrument for PUC/PSC/FERC orders that set large-load terms beyond one tariff. A federal-scope Policy goes in the `state:US` refresh unit.
- **The claims.json size test now caps the deferred file at 600 KB**, not companies+claims at 256 KB. claims.json has not been first paint since v5; the old cap was 183 bytes from failing the daily refresh.

## 2026-11-21 — async record routing and optional election evidence

Expected a canonical record link to use the router's existing history entry.
An awaited site/policy lookup continued after the synchronous routing flag
had reset, creating a second entry; a late result could also overwrite Back.
Keep a generation guard across the await and restore routing mode around the
continuation's view activation. The civic navigation tests cover returning
from a record to a place search.

Expected election results to carry evidence in the action-feed builder.
Unreported results legitimately have no evidence: guard the optional field
and omit the source rather than inferring a result or a citation.
