# Refresh and research procedures

Moved verbatim from CLAUDE.md on 2026-11-23. Read before a data refresh, validation pass or research run. The daily routine follows .claude/skills/daily-refresh/SKILL.md.

## Daily refresh routine and the review queue (2026-09-25)

A cloud routine, **DataCenterCommunityBenefits-DailyRefresh**, runs every day
at 10:00 America/New_York on Sonnet, as one agent with no subagents, capped
at 20 minutes by its prompt. It follows
[.claude/skills/daily-refresh/SKILL.md](../../.claude/skills/daily-refresh/SKILL.md).
Change the procedure by editing that file in a PR, not the routine's prompt,
which only says "follow the skill". Manage the routine itself at
claude.ai/code/routines.

- **The queue is derived, and the ledger only annotates.**
  `scripts/refresh_queue.py` builds its units from the payloads: every
  project is a `site:`, every company a `company:`, and every `STATE_NAMES`
  key in app.js plus `US` is a `state:`. `data/refresh_ledger.json` holds only
  `last_reviewed`, a one-line `summary`, dated `follow_ups` and `last_check`
  (the finding of the latest quick follow-up check, so it outlives the run's
  commit message), keyed by unit. A new project enters the queue by existing.
  `test_committed_ledger_is_valid` rejects a ledger key that no longer names
  a unit, such as a renamed project id.
- **Some follow-ups are derived, not stored.** A pending rate case's
  `next_milestone_date` comes due the next day. An enacted moratorium with
  `duration_months` comes due at its computed end date. Each clears when the
  record's `captured_at` passes the due date, so a re-check has to bump
  `captured_at`. Don't copy these into the ledger, or they drift.
- **Run rhythm:** due follow-ups first, as targeted checks marked with
  `--followups-only`, which does *not* count as a review. Then full reviews
  in the order site, state or company on alternating days, site, then one
  `country` unit (v6). Target intervals are site 90 days, state 120,
  company 30, country 120. `run_plan` asserts every kind in `TARGET_DAYS` has
  a rhythm slot, because a new kind without one is silently never scheduled.
- **Evidence gate:** each run logs `{id, source_url, verbatim}` per change,
  then `scripts/probe.py --evidence` re-fetches every page and fails on a
  MISS, meaning the page loaded but lacks the quote. That is the mechanical
  version of the v1.19 "live link ≠ verified claim" rule. A BLOCKED site
  (bot wall) needs a WebFetch read in the run, and the run lists it as not
  machine-verified.
- **Merge policy:** the routine squash-merges to `main` when `refresh.py` and
  the unit tests pass, matching the owner's other refresh routines, because
  a merge is a deploy. This is an open decision (BACKLOG §1). It also keeps
  the ledger moving: unmerged runs would start from a stale ledger and redo
  the same units. The routine never adds companies, marks `contested`,
  attaches `delivered`, deletes records or edits company summaries; those
  become BACKLOG leads.
- **BACKLOG §3 is keyed by unit heading** (`#### state:GA`), and
  `refresh_queue.py --unit` hands a unit its own section. A lead filed under
  any other heading is invisible to the routine.
- **Agents:** `model: "sonnet"`, one at a time, each checkpointing to disk
  per record. The 2026-09-22 pass lost two agents' unsaved context to a
  session limit. Only what was on disk survived.
- **Local environment:** this Mac has only the system Python 3.9. schema.py's
  `X | None` annotations need `eval_type_backport` there, now in
  requirements.txt behind a `python_version < "3.10"` marker. Use a project
  `.venv` (gitignored).

**The gate had two loopholes, caught by Codex on PR #49 before any
unattended run.** A changed evidence row with no `source_url` or `verbatim`
was counted as "skipped", which means passed. The quote check matched only
the longest clause, truncated to 160 characters, so a page holding the first
sentence of a two-fact quote passed while contradicting the second. Now only
`no_change`/`held`/`not_found` rows may lack evidence, and every clause of
every quote must be on the page. Trailing punctuation is ignored, because
quoting the front of a sentence and closing it with a period is normal. Two
general rules follow:
- **A gate that skips malformed input is a gate that passes it.**
- **Check every piece of a claim, not the most matchable one.**

Re-running the strict gate on the day's already-reviewed evidence found three
more problems:
- a quote blended from two sentences on one page;
- a bracket insertion ("r[eading]");
- a claim on no page at all (Fort Worth "extendable for an additional 90
  days").

**The first scheduled run (2026-09-26 10:05) hit the setup-not-merged guard,
made no changes, and stopped in 9 seconds.** It showed that the cloud session
starts **on `main`**, not on an assigned branch as the owner's other routine
does. A bare `git push -u origin HEAD` would have pushed straight to main and
skipped the PR audit trail, so the skill now branches first.

**Cross-device audit (2026-09-25).** A Playwright harness that serves `docs/`
gzipped cold-loads each tab at 390/820/1366/1920 widths and also under Slow
4G with 4x CPU. It found performance fine: FCP 0.86 s and LCP ≤ 1.4 s
throttled, TBT about 0, warm tab switches 28–110 ms. It found real usability
problems: on a phone only 2–4 of the 7 tabs show, with no overflow cue; stat
tiles wrap raggedly; Moratoriums runs 25 screens; The Pledge has 214 targets
under 24 px; and Home's "Recent changes" feed is unsorted and blind to every
payload except the roster. First paint is 246.5 of the 250 KB budget, with
most of it being claims and projects that Home barely uses. All of it is in
BACKLOG §4–§5.


**`scripts/revalidate.py` is the token-free pre-pass (2026-10-19).** It walks
every `source_url` / resource URL in the payloads named by
`refresh.PAYLOAD_FILES` (plus `international.json`'s nested lists), classifies
each as live / blocked / dead / redirected, runs probe.py's clause matching on
claim statements and policy `key_terms`, stores a text fingerprint per URL in
`.revalidate_cache/`, and flags date-stale statuses. `--cached` prints the
worklist offline; only records on it need an LLM. Tests:
`tests/test_revalidate.py`.

## Stuck units get parked, not retried (2026-10-08)

The first unattended-style run on the new queue ended after 2 of 20 minutes
with no changes: the top unit (`site:meta-newton-ga`, dead `source_url`) was
already a known dead end, and the run treated "one search found nothing" as the
end of the run instead of moving to the next unit. Two fixes, both in
`scripts/refresh_queue.py` and the daily-refresh skill: `--mark KEY --blocked
--summary "why"` parks a unit for `BLOCKED_COOLDOWN_DAYS` (14), sorting it last
in `ranked()` and out of `run_plan()`, stored as `blocked: {date, reason}` in
the ledger (a completed review clears it); and the skill now forbids ending
before minute 12 without having worked or parked the next units. A queue with no
notion of "known stuck" will serve the same stuck unit first forever.

## Oct 18 refresh: research pipeline and history routing (2026-10-18)

**Research pipeline that worked:** Haiku researchers (≤3 at once, one beat
each: government actions / sites / power) → a deeper Haiku follow-up per beat
→ one Sonnet synthesis into a schema-validated `merge_plan.json` → Haiku
fact-checkers per beat → `probe.py --evidence` over every quote. Three
lessons:
- **Agents read this file's 10-URL gate and stop at it.** All three
  first-pass researchers halted at 8–10 fetches with thin results. When the
  owner has approved a large research pass, say so in the agent brief with a
  number ("up to ~25 WebFetch calls").
- **Fact-checkers strip facts an earlier pass sourced.** Asked to verify an
  *update*, they marked every pre-existing sentence that wasn't on *their*
  page as unsupported. They also wrote "removed pending a source" into the
  notes text. Apply updates append-only by hand. Use a checker's field fixes
  only for the new facts, and for whole records being added.
- **probe.py misses on PDFs and coordinates are usually extraction
  spacing** ("202 6-15"). Re-probe with a short phrase before treating one as
  a real miss.

**History routing (#72, PR #77).** `activateView` pushes a history entry for
every user-driven view change. Boot and Back/Forward go through
`routeFromLocation`, which sets `state._routing`. While it is set, nothing may
push or `replaceState` on its own. Closing the policy modal used to call
`writePolicyUrl()` mid-popstate, which overwrote the entry Back had just
restored and trapped the reader on Frameworks. Two more rules:
- Plain-hash views write `pathname + hash`. A bare `"#x"` keeps the query
  string, and that leaked Sites/policy params into every view.
- Any new modal must be closed in `_routeFromLocation`, and must not touch
  the URL while `state._routing` is set.

**Policy deep links:** `?p-state=&p-status=&…&policy=<id>#policies/<pane>`.
These are separate keys from the Sites filters (`state`, `q`).
`writePolicyUrl` keeps the query string until the payload has applied it,
because `activateView` rewrites the URL before data lands. Back/Forward onto a
Frameworks or Sites entry re-applies *that entry's* params, including clearing
the open project or record. State held in memory must never win over the
restored URL.

## Follow-up to PR #85: discovery script, PDF/charset probing, merge gate (2026-10-19)

- **Discovery is now a script, not a search.** `scripts/scan_sources.py` reads
  `scripts/news_sources.json` (DCD and DCK RSS, plus a Google News feed per
  country in its language), keeps titles that name a data center in any
  tracked language, drops URLs the seed already cites and leads earlier runs
  reported, and writes a per-country worklist. Research agents triage those
  titles before fetching anything. Google News links are redirects that 400
  when fetched, so the outlet name is kept in `[brackets]`: search the outlet
  and cite its own URL, never news.google.com. Add an outlet only after its
  listing URL is confirmed to enumerate dated stories.
- **`scripts/revalidate.py` before any validation pass.** Run it live in
  `--limit` batches until there is no `NOT CHECKED` banner, then hand its
  worklist (dead links, quote misses, stale statuses) to agents. The first
  full run (2,265 of 2,291 rows) found 39 dead links, 214 quote misses and 3
  expired moratorium terms. Most claim misses were real: 24 claims were
  removed because no page carried their words.
- **probe.py reads PDFs with macOS PDFKit** (`scripts/pdftext.js`) and
  decodes Shift-JIS / EUC-KR pages from their meta charset. Before this,
  PDF letter-spacing ("three y ears") and Japanese encodings produced false
  MISSes all session.
- **A figure that no longer matches the live page is not a wrong figure.**
  Google's and Meta's pages changed after capture; Wayback snapshots near
  `captured_at` showed the stored figures were right then. Repoint to the
  snapshot and keep the dated capture. Don't overwrite it with today's number.
- **Merge gate (the #85 lesson).** #85 merged while a side session still had
  three research agents running for it, and their 19 findings missed the
  PR. Before `gh pr merge`, check `list_sessions {"linked": true}` and every
  background agent. Nothing that was promised to the PR may still be running.
  Every subagent brief now says "do not call any session tools". A Haiku
  validator called `hand_off_to_session` by accident and created an
  uncontrolled session that committed to the PR branch.
- **Haiku researchers stop early unless told not to.** Several stopped after
  90 seconds, citing a time limit they had misread. Briefs now say "you have
  the full N minutes and ~M fetches; keep working until one runs out".
- **New countries (wave 4): MX, ES, BE.** Registered with MXN at the Fed
  G.5A 2025 rate (1/19.2052). The international tab now has 18 countries
  plus the EU. Operators added this pass include Naver, Kakao, LG U+,
  Mitsui Fudosan, Colt DCS, Sesterce, EcoDataCenter, CloudHQ and Pampa
  Energía. Each was added because a first-party record needed it.
