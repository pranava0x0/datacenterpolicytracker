# Engineering lessons

Moved verbatim from CLAUDE.md on 2026-11-23. Read before writing a guard test, a checker, an e2e test, or before a PR review/merge pass.

## Cross-project lessons carried forward

- **Source attribution is non-negotiable.** Every record must include its origin URL. If a record lacks a source, it doesn't ship.
- **Defensive optional field handling.** Null values in the UI render as explicit placeholders ("N/A", "Not disclosed"), never blank cells.
- **Schema is the contract.** Pydantic `extra="forbid"` catches drift before write; tests cover normalize/edge cases.
- **The `[hidden]` trap.** See Frontend Standards above — pair every `display: ...` override with `[hidden] { display: none }`.
- **Static-first deployment.** GitHub Pages serving `docs/` with no runtime backend; same pattern as adjacent projects in this org.

## ISSUES.md is GENERATED — bugs do not go there

`ISSUES.md` is a **refresh.py output** (`--audit`), regenerated on every run: a
prioritized list of *data* gaps (missing `power_mw`, stale `proposed` bills).
The universal convention at the top of this file — "maintain a living issues.md
as an audit trail" — does **not** apply to this project's copy: anything
hand-written there is erased on the next refresh.

Code bugs, root causes and fixes go in the **commit message** (which is where
this project's real bug history lives) and, when they carry a reusable lesson,
in this file. Deferred work and leads go in `BACKLOG.md`. Don't hand-edit
ISSUES.md.

## First-paint budget is now a test (v2)

Making Ratepayer the landing view pulled projects + responses + the roster into
first paint: **~141 KB → ~237 KB gzipped across 8 requests**, inside the 250 KB
/ 8 guardrail but with little headroom. The old ~202 KB / 6 baseline in this
file described the Comparison landing and no longer applies. (v2.1: the default
view is now Overview, not Ratepayer, but the budget is unchanged — Overview
shares Ratepayer's `loadRatepayerView()` loader and needs the identical
payload, so nothing below moved.)

`tests/test_perf_budget.py` gates it. **When it fails, make the new payload lazy
— don't raise the ceiling.** This has already been exercised once: P5 took it to
246.5 KB, and the fix was splitting `responses.json` out of `loadProjectData`
into its own `loadResponseData` (**back to 203.9 KB / 7 requests**). Responses
only decorate below-the-fold concern flags, so the Ratepayer view paints from
projects and re-renders the scorecard when they land; Explorer and Aggregate,
which render response *content*, await both. `loadRatepayerView` **awaits** the
late fetch before firing `dcb:ratepayer-ready` — several e2e tests and the
concern-first sort treat that event as "the view is complete". Sizes are measured gzipped because that is how
Pages serves them, and raw bytes flatter JSON enormously (signatories.json is
121 KB raw, 8 KB gzipped).

## Universal lessons learned here (mirrors the canonical CLAUDE.md)

Promoted to `~/Projects/coding-best-practices/CLAUDE.md` in the same pass, and
repeated here because this is the file that actually loads in this directory.

- **A click anywhere inside `<summary>` toggles the panel**, so a button in a
  collapsible header fires *and* collapses the section. Toolbars go in the body.
  The old `.directory-section` shipped its CSV/PDF buttons in the summary.
- **Aliasing legacy class names onto a new shared rule only works if the shared
  rule wins the cascade.** `.hot-rail-title` / `.hot-rail-sub` sat later in the
  sheet and silently re-won, so the Explorer heading kept rendering a size
  smaller than every other tab while the new rule looked "not applied". Grep and
  delete the redundant declarations; a selector with zero remaining markup is
  dead code (four were, one referencing a `--text-secondary` that no `:root`
  defines).
- **A styled `<span>` standing in for a heading is invisible in review and in a
  screenshot.** The pledge band's `<h3>` became a `<span>` during the accordion
  conversion and dropped out of the document outline. Wrap in a `<div>` (a
  `<span>` can't legally contain a heading) and guard with
  `test_every_accordion_header_is_a_real_heading`.
- **Hiding content behind a disclosure or tab breaks every test that waits on
  it** — attached but not painted, so `state="visible"` times out and
  `inner_text()` returns `""`. Click the disclosure rather than loosening the
  wait. Third time this project has paid for it (Community pane → v2 comparison
  default → accordions + sub-tabs).
- **`page.goto(base + "#hash")` does not reload an SPA**, so hash routing never
  fires; successive fragment-only `goto`s are same-document navigations. The
  screenshot harness silently captured four un-rendered tabs. Use
  `/?i=<name>#hash` or `reload()`.
- **A source's heading routinely claims more than its body supports — quote the
  body.** See the commitments section above for this project's instance.
- **Never assert a layout measurement against an exact pixel floor.** A
  `min-height: 44px` sub-tab measures `43.999969...` in Playwright's
  device-scaled mobile context, so `height < 44` failed ~1 run in 5 on correct
  CSS and read as flake. `TOUCH_FLOOR_PX - 0.5` in
  `TestTouchTargets`; mutation-checked that 39px still fails.
- **`set_viewport_size` does NOT make `(pointer: coarse)` match** — only a
  context with `is_mobile`/`has_touch` does. Every other mobile test in this
  repo resizes the viewport, so all of them silently measure the *desktop*
  rule. Any test about touch behaviour needs a real touch context, and needs to
  assert the media query engages before trusting its numbers
  (`test_coarse_pointer_emulation_actually_engages`).

- **"Make it simpler" is a request about the design SYSTEM, not the layout**
  (2026-08-24). The minimal-briefing Home shipped at half the old height and
  still read as "way too busy / worse than before" because it inherited four
  font families, red label chrome, and a page headline that dwarfed the
  masthead. Before calling any simplification done: count font families on
  one screen (two), count colors doing non-semantic chrome work (one accent;
  red/amber/green only for data meaning), confirm the masthead outranks
  every view heading. Enforce by deleting the extra tokens, not styling
  around them — see "One type scale, one accent".
- **"I don't see your changes / is this stale?" is a which-surface question**
  (2026-08-24). The deployed site serves `main` (branch work invisible until
  merge), the preview artifact updates on republish but viewers cache until
  a hard reload, and localhost is its own thing. Verify the publish landed
  by grepping the published bundle for a marker only the new version
  contains, then tell the user which surface shows what — before debugging
  code that was never wrong.

## A guard's SCOPE rots exactly like any other hand-written list

`tests/test_no_dead_css.py` started with an allowlist of "project-owned"
class prefixes. Codex pointed out it omitted whole families — `claims-` and
`chip-` were never in the list, so `.claims-section`, `.chip-row` and seven
others sat dead and *certified clean*. This is CLAUDE.md's own
single-source-of-truth lesson landing inside the tool written to catch drift,
for the fourth time in this project.

Now inverted: scan **every** class in styles.css, exclude a short denylist of
third-party prefixes (`leaflet`). A denylist is obvious when it needs an entry;
an allowlist is silent when it doesn't have one.

Two live classes were false-positived on the way, both from interpolations
carrying their own quotes:

```js
class="mor-toggle-btn${active ? " is-active" : ""}"
class="at-a-glance-text${isCurated ? " curator-override" : ""}"
```

A `class="(.*?)"` regex stops at the quote before ` is-active`. The fix is a
depth-tracking scanner (`_class_attr_values`) plus harvesting class names from
*inside* the interpolation's string literals — `curator-override` only ever
appears there. Leaflet's `L.DomUtil.create("div", "map-legend")` needed teaching
too.

**The pattern across all four rounds of this guard**: every time it was
tightened it produced false positives on known-good code, and every time the
loosening that fixed them had to be checked for re-opening the original hole.
Budget for that; a scanner is not a one-line test.

## Zero is a result; missing is not

Both count helpers cleared their chip on a falsy value, so `0` and "hasn't
loaded" rendered identically — blank. A directory filtered down to nothing lost
its "0 records" the moment the reader collapsed the section, which is exactly
when the chip is the only thing left saying anything. `Number.isFinite(n)` is
the check; only a non-number clears.

This is **not** in tension with the project's honest-absence rule (`renderRatepayerStats`
deliberately omitted a zero "contested" tile). The distinction: a stat tile's
*existence* asserts a finding, so a zero one manufactures one. A count chip
answers "how much is inside this section", and `0` is a true answer to that.

## Check the spec with a validator, not from memory

Codex flagged the accordion summaries as non-conforming, claiming both the
`<div>` wrapper **and** the `<h3>`-beside-spans pattern were invalid. Running
`docs/index.html` through the W3C Nu validator settled it in one call:

```
curl -sS -H "Content-Type: text/html; charset=utf-8" \
  --data-binary @docs/index.html "https://validator.w3.org/nu/?out=json"
```

The `<div>` was a real error ("Element div not allowed as child of element
summary"); the h3-with-sibling-spans pattern drew no complaint — `<summary>`
takes phrasing content *optionally intermixed with heading content*, which is a
spec change I'd have got wrong from memory in either direction. The kicker moved
inside the `<h3>` (which does take phrasing content), so no wrapper is needed.

**The same call found 22 pre-existing errors nobody had looked for**, four of
which are `aria-label` on a bare `<div>` — silently ignored by AT, so four
regions a screen-reader user hears unlabelled. Logged in BACKLOG.md, not
widened into that PR. Worth wiring into CI so the count can only go down.

`test_summaries_contain_only_conforming_children` is the offline proxy, scoped
to `details.acc > summary` so it doesn't fail on the 39 pre-existing
`.rp-card-details` summaries that have the identical defect.

## A "does this name appear anywhere?" check is not a usage check

`tests/test_no_dead_css.py` v1 asked whether a CSS class name appeared as a
substring of index.html + app.js. Codex pointed out that an **id** of the same
name answers yes: `.rp-commitments` had three orphaned rule blocks and the
guard passed on the strength of `id="rp-commitments"` sitting on an element
whose class is `rp-commit-list`. A guard that accepts an id as evidence of a
class certifies exactly what it cannot see.

v2 parses class *application* sites — `class="..."`, `className =`,
`classList.add(...)`, and this project's `el(tag, "classes")` helper. It found
two more dead selectors immediately.

**Tightening a guard needs its own false-positive pass.** The stricter version
initially reported `.mor-toggle-btn` and `.rp-state-chip` as dead, and both are
live. Cause: the interpolation contains its own quotes —

```js
class="mor-toggle-btn${active ? " is-active" : ""}"
```

— so the `class="..."` regex stops at the quote before ` is-active` and the
captured value ends mid-expression. Substituting only well-formed `${...}` left
`mor-toggle-btn${active` as a literal class name. Any residual `${` now
truncates the token to a stem. **Run a newly-strict check against known-good
code before trusting its output**; a guard that cries wolf gets disabled.

## A guard can inherit the exact blind spot of the bug it guards

`goToPledgeTarget` failed to open the signatory roster because
`openAccordionsFor()` walks **ancestors**, and the roster's `<details>` is a
**child** of the `#rp-roster-section` the target pointed at. Codex caught it.

The test written to guard the whole `PLEDGE_TARGETS` table then used
`el.closest('details.acc:not([open])')` — which also only looks *upward*.
Reverting the fix left the new test **green**. It was only caught by mutating
the fix away, which is the whole argument for doing that on every new
assertion. The guard now checks self + ancestors + descendants.

Generalizes: when you write a test for a directional bug (upward/downward,
before/after, inner/outer), the obvious API for the check usually shares the
bug's direction. Mutate the fix away and watch the test go red, or you have
written the bug twice.

Related, same review: `test_only_the_active_subtab_is_in_the_tab_order` passes
from the authored HTML alone, so deleting the `btn.tabIndex` line in
`setActiveSubtab` does **not** turn it red — `test_tab_order_follows_selection`
is what covers the JS half. Both docstrings say so. **Two tests that look like
one guard can each cover a different half and neither cover the whole.**

## The documented `<details>` display-override trap did NOT reproduce here

The base CLAUDE.md warns that an author `display:` rule on a direct child of
`<details>` outranks the UA rule hiding a closed panel. Mutation-checked in this
project's Chromium: adding `.acc-body { display: grid }` **and** deleting the
`.acc:not([open]) > :not(summary)` safeguard left the panel correctly hidden and
the test green. Current Chromium hides closed content via the slot, not a
defeatable `display: none`.

Both stay: the CSS rule as defense for engines where it does bite, and
`test_closed_accordion_does_not_paint_its_body` as the weaker assertion it can
honestly make — its docstring says so explicitly. **The transferable bit is the
method, not the result:** the test looked like a guard on that trap and would
have been believed. Mutating the code to make a new assertion go red is the only
way to know which of your guards are real (base CLAUDE.md > "a green test you
have never seen go red is a hypothesis").

## PR #41 review + merge lessons (2026-08-04)

A fresh review pass (2 background code-reviewer agents, backend/data vs.
frontend/e2e split) on PR #41 found 9 + 4 findings (the 4 from an independent
Codex bot review already posted); every one was verified against the actual
PR branch before acting, all were fixed, and PR #40 + #41 merged to `main`.
Concrete, reusable lessons:

- **A class-name-mapping constant's parity test must check the CSS *value*
  resolves, not just that the JS object's *keys* match the enum.**
  `RATE_CASE_BADGE_CLASS` mapped `approved` → `badge-tariff-approved`, but
  `styles.css` only ever defined `badge-tariff-status-approved` (note the
  extra `-status-`) — every rate-case badge rendered with no color. The
  guarding test (`test_rate_case_badge_class_covers_every_status`) asserted
  `set(js_keys) == set(RATE_CASE_STATUSES)` and passed green over the bug,
  because a mismatched *value* is invisible to a keys-only check. This is the
  **third** recorded instance of this exact shape in this project (v1.19
  `badge-reason-*`, the RATEPAYER_STATUSES-adjacent drift, now
  RATE_CASE_BADGE_CLASS) — worth grepping for the pattern
  `_extract_object_keys(js, "..._CLASS")` without a matching values check
  anywhere else it might still exist. Fixed by adding
  `_extract_object_values()` and asserting `f".{class_name}" in css` for
  every mapped value.
- **New `docs/app.js` loaders must follow the existing promise-memoization
  pattern (`let _xDataPromise = null`), not a plain boolean flag.**
  `loadRateCasesData()` guarded on `state.rateCasesLoaded` — a boolean not
  set until after its own `await` resolves — while every sibling loader
  (`loadProjectData`, `loadResponseData`, `loadSignatoryData`) caches the
  in-flight *promise*. Concretely: `loadAggregateView()` calls
  `loadTariffsData()` (which itself calls `loadRateCasesData()`) **and**
  `loadRateCasesData()` directly in the same `Promise.all` — both synchronous
  calls saw the flag `false` before either `await` settled, so
  `data/rate_cases.json` fetched twice on every Aggregate-view load. When
  adding a lazy-loaded payload here, copy the `let _xPromise = null; function
  loadX() { if (!_xPromise) { _xPromise = (async () => {...})(); } return
  _xPromise; }` shape verbatim, and add an e2e test asserting the payload URL
  is requested exactly once (`page.on("request", ...)` + count assertion) —
  this bug had zero test coverage until this pass.
- **A `Promise.all` combining a view's primary payload with a secondary/
  decorative one needs the secondary payload's promise caught individually**
  (`loadRateCasesData().catch(err => console.error(...))`), not the whole
  array — otherwise the secondary payload failing rejects the primary too and
  blanks the whole view. `loadRatepayerView` and `openStatePanel` already did
  this correctly; the two new call sites (`loadTariffsData`,
  `loadAggregateView`) didn't.
- **When a claim's cited source is third-party news paraphrasing a company
  statement, check whether the article links to the company's own primary
  source and fetch that directly.** A Clay County claim read "the company
  pays for 100% of the power it uses" (POWER Magazine, third-person, no
  quotation marks — the exact shape CLAUDE.md's first-party rule rejects).
  The article linked to Google's own blog post; fetching that directly
  surfaced the *actual* first-person quote ("we're supporting... helping to
  ensure we cover our own operational and infrastructure costs") — a
  genuinely different, more defensible claim, not just a reformatting of the
  same one. One extra WebFetch turned an unusable paraphrase into a valid
  first-party claim instead of a deletion.
- **A DOE/LBL-brief-cited docket number is not automatically verified** — the
  brief is a trusted source for the *existence* of a proceeding, not for a
  *later* status change claimed by a different, weaker secondary source.
  `nv-energy-callisto-esa`'s docket number (`24-06014`, originally from the
  LBL brief) came back in an independent web search attached to an
  *unrelated* Sierra Pacific general rate case — stronger grounds to revert
  an unverified `approved` status flip than "the source_url predates the
  claim" alone. Don't stop at "the source doesn't support this specific
  claim"; a quick search on the docket number itself can surface a direct
  contradiction.
- **Stacked-PR merge sequence that works cleanly on GitHub:** merge the base
  PR first *without* deleting its branch (`gh pr merge N --merge
  --delete-branch=false`), then `gh pr edit (N+1) --base main` to retarget
  the dependent PR — GitHub recomputes mergeability against `main`'s new HEAD
  cleanly as long as the base PR's branch still exists at retarget time. Only
  delete both branches after the dependent PR has also merged.
- **`gh api .../pulls/{n}/reviews` rejects `event: "REQUEST_CHANGES"` (and
  presumably `APPROVE`) when the authenticated user is the PR's own author** —
  422 `"Review Can not request changes on your own pull request"`. Use
  `event: "COMMENT"` for a self-authored PR review submitted via the API.
- **`git merge-tree $(git merge-base A B) B A` finds real conflicts without
  attempting an actual merge** — used to confirm PR #36 (a `ui/` branch from
  2026-07-27) had genuine, substantive conflicts with `main` before closing
  it as superseded, rather than guessing from commit dates alone.
- **A new seed-data builder must use `ensure_ascii=False` like every other
  one, or it — and any ad-hoc `python3 -c` edit of the seed JSON that doesn't
  explicitly pass it — produces `\uXXXX`-escape churn that reads as a
  whole-file diff on the next run of a builder that DOES pass it.**
  `build_rate_cases.py` shipped with the `json.dumps()` default
  (`ensure_ascii=True`); by the time this was caught, all six seed files
  (not just the one that script generates — meaning some other pass, likely
  a direct Python edit, had the same gap) had ~1,300 lines of pure escape
  churn. Fixed the builder and normalized all seed + `docs/data` JSON back to
  UTF-8, verifying `json.loads(before) == json.loads(after)` for every file
  before writing so the fix was provably free of semantic changes.

## e2e suite: 40+ minutes → ~80 seconds (2026-10-08)

`python3 -m pytest tests/e2e -n 4` (pytest-xdist). Three changes, all in
`tests/e2e/`:
- **One wait budget, `E2E_WAIT`** (6 s, env `E2E_WAIT_MS`) replaced 190
  hardcoded 10-15 s waits, and an autouse fixture sets the same default
  for actions and `expect`. Locally a view renders in under a second; the
  long waits only made each broken test cost 10-15 s.
- **Basemap tiles are answered locally** (204) in the autouse fixture. No
  test asserts tile pixels.
- **Parallel workers**: the docs server is session-scoped per worker.
Run the suite after every UI change; at 80 s there is no excuse not to.
The first fast run caught a real bug the slow one had hidden in its
timeouts: `wireSubtabs()` was only reached from the Pledge renderer, so the
new sub-tab strips switched panes by URL and ignored clicks
(`test_every_view_subtab_responds_to_a_click` now guards every strip).
**A test that pins a specific record to a capped list** (Frederick County
in the 12-item "Latest actions") goes stale on the next data refresh;
assert the rule, not the record.
