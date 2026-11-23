# Ledger redesign — 2026-11-23

## What a reader comes for

| Journey | Question | Where it is answered now |
|---|---|---|
| briefing | What is happening overall? | Home: five top lines, then Latest / Coming up |
| pledge | Who signed, and is it showing up at sites? | Home top line; The Pledge opens on the same sentence, Tracked sites leads |
| moratoriums | Where are pauses in force, and what is newest? | Home top line + monthly bars; Moratoriums stat row, directory first |
| policy | What laws, orders and rules apply? | Home top line; Policy opens on "In effect", topics show counts |
| benefits | What have communities won? | Home top line (newest signed) + links to signed agreements, drafts, impact claims |
| power | What do regulators decide next? | Home top line (next step); Power Costs opens on rate cases |
| place | What is happening in my state, county or city? | Search on Home; state panel; jurisdiction map |
| elections, operators, international | — | One row each under the top lines; own tabs |

`tools/interaction_cost.py` groups its tasks under these journeys
(`JOURNEYS`) and reports which top lines are on the first screen.

## What changed

- **One navigation row.** It used to be three: Explore / Compare / Plans /
  Updates, a second "browse" row of eight links, and a footer copy of the
  same tabs. Now it is Overview, the record tabs in ledger order (The Pledge,
  Moratoriums, Policy, Power Costs, Elections, Companies, Sites,
  International), then Updates, Compare and Plans. Phones get a 4 × 3 grid, so
  no tab hides behind a side-swipe.
- **Home is a ledger.** Search, then five rows. Each row has a large tabular
  figure, one status sentence, and the newest or next dated record, which
  opens directly. Two data marks: assessed pledge sites by status, and
  moratoriums enacted per month. The numbers come from `toplines` in
  `home.json` (`refresh.py::_build_toplines`), under the rule each tab uses.
- **No eyebrows.** Modal kinds, operators on pledge and contested cards, and
  the type on feed items moved under the title.
- **Sections are ruled, not boxed.** Grey accordion bars became a hairline and
  a heading. The dark commitments slab became a ruled section.
- **Copy cut:** "One card per operator", "Coverage varies by state", the
  tariff footnote, "theme by theme" ×2 and a corrective-negation note. "Why
  it failed" became "Failure reason". The Home search label is "Search".
- **Phones:** moratorium rows are two-line entries (place and status, then
  date and duration) with no side-swipe. Policy topics fit the first screen.
- **Docs:** CLAUDE.md went from 182 KB to 8 KB, with a "Load before…" table.
  Everything else moved verbatim to `notes/agent/`.

## Borrowed from other trackers

The research notes are in the session's research summary. Two sites could
not be fetched: Good Jobs First returned 403 and Heatmap is paywalled.

- ProPublica Nonprofit Explorer: search first, with no hero above it.
- Brennan Center voting-laws roundup; NC Clean Energy Technology Center:
  a dated, countable top-line sentence. Our top lines read "as of" where the
  source is a snapshot.
- Our World in Data; KFF: counts that are links. Every top-line figure opens
  its tab.
- Sabin Center: example links instead of instructions. The benefits row
  links straight to signed agreements, drafts and impact claims.
- FT / GOV.UK: a short type scale, tabular figures, status as a word plus
  one colour, and hairline rules.

## Left for later

- On phones, the general Latest and Coming up feeds now sit below the
  ledger, 2–3 swipes down. Each top line already carries its own newest or
  next item.
- Pledge-bar and jurisdiction-map colours are still hex values outside
  `:root`. They are pre-existing; `slop_design` warns on them.
- The ★ governor marker on the Pledge coverage strip is flagged as emoji in
  body copy. It stays because it is a data key.
