# SPEC v7: one policy record, LBL 2026 power costs, record deep links

Owner request, 2026-11-16:
1. Combine Moratoriums with the other government actions (state EOs, legislation, policies, tariff legislation and orders), with moratoriums kept as their own call-out.
2. Power Costs is hard to read. Re-base the tariff "elements" on LBL's Aug 2026 update, reassess every tariff against it, and lead with plain prose on what to watch.
3. Give every row, policy, moratorium, site and company its own URL.
4. Make sure the data model supports this and relates records across types.

## Current state (measured 2026-11-16)

| Type | Records | Outbound links today |
|---|---|---|
| Moratorium | 358 (190 city, 143 county, 24 state, 1 federal) | none |
| Policy | 162 (54 legislation, 33 ordinances, 29 agreements, 22 company plans, 20 EOs, 3 frameworks, 1 regulation) | `related_moratorium_id` (set on 10), `related_project_ids` |
| Tariff | 29 | `legislation[]`, 7 embedded `{title,url}` entries that are not Policy records |
| RateCase | 21 | `related_tariff_id`, `related_project_ids` |
| Project | — | `ratepayer.evidence_claim_id`, `serving_utility_signatory_id` |

Gaps:
- Links run one way only. A moratorium can't show the policy that replaced it, and a tariff can't show its rate cases unless the frontend scans for them.
- The law behind a tariff (OH HB 15, NJ S731, OR HB 3546, TX SB 6) is an embedded string, so it never shows up as a policy.
- There is no instrument type for a commission order. PUC orders that set large-load rules have nowhere to go except Tariff.
- Only 20 EOs and 54 statutes are tracked; several known state actions are missing.
- Deep links exist only for `#state/XX`, `#country/XX`, `#elections/<id>` and `?policy=<id>`. Moratoriums, tariffs, rate cases, sites and companies have none.

## 1. Data model

**Keep the five record types.** Moratoriums have fields no other type needs: thresholds, votes, duration, lift dates. Merging 358 records into Policy would blur the schema to save one tab. The "combined" part happens in the view and in the links between records.

**One cross-reference shape on every government-action record:**

```python
class RecordRef(BaseModel):
    kind: Literal["policy","moratorium","tariff","rate_case","project","company","election"]
    id: str
    relation: Literal["implements","authorizes","replaces","replaced_by",
                      "challenges","related"] = "related"
```

- Add `related: list[RecordRef]` to Moratorium, Policy, Tariff and RateCase.
- Migrate the existing `related_moratorium_id`, `related_tariff_id` and `related_project_ids` into it, then delete the old fields. One shape, not four.
- **Store links one way; derive the reverse.** refresh.py builds `docs/data/links.json` (`{"kind:id": [{kind,id,relation}]}`), which includes the inverse of each relation (authorizes ↔ implements, replaces ↔ replaced_by). The frontend reads that file, so a link written on one record appears on both. Storing both directions is the "hand-written list that mirrors a registry" failure.
- refresh.py rejects a ref whose target doesn't exist (same pass as today's cross-ref check).
- `Tariff.legislation[]` gains an optional `policy_id`. Each of the 7 entries becomes a real Policy record (OH HB 15, NJ S731, etc.) where one doesn't already exist, and links with `relation: authorizes`.
- New `PolicyInstrument` value: `commission_order`, for PUC/PSC orders that set large-load rules outside any one tariff. A tariff stays a Tariff.

## 2. Policy tab (combined), moratoriums called out

- The Policy tab lists every government action: statutes, EOs, ordinances, commission orders, agreements **and moratoriums**, in one directory with an instrument filter. Moratoriums keep a distinct badge and a call-out band at the top: count, enacted, proposed, the latest three.
- The Moratoriums tab stays as the depth view (map, trends, influence claims) and is linked from that band. Old hashes keep working.
- A record's detail shows a "Related" block from `links.json`: the law that authorized it, the tariff that implements it, the moratorium it replaced, rate cases, sites.
- **Research pass** for the missing state EOs, statutes and orders: one fetch-verified record each, sourced to the legislature's or governor's own page. No homepage citations.

## 3. Power Costs on the LBL 2026 framework

Source: Frick, Cappers et al., *Electricity Rate Designs for Large Loads: Evolving Practices and Opportunities, 2026 Update* (LBNL, 2026-08-10), 55 tariffs.

New element taxonomy: 18 elements in LBL's four practice groups, plus 12 sub-elements from its Appendix 2.

| Practice | Elements (sub-elements) |
|---|---|
| Established | Minimum demand threshold · Minimum contract duration · Monthly demand charge · Minimum billing demand · Minimum bill · Collateral requirements · Direct assignment of costs (capacity reservation, interconnection upgrades, generation/capacity, network transmission) · Customer-specific resource procurement (behind-the-meter generation, customer-led procurement, load flexibility) |
| Stable | Load factor threshold · Aggregation rules · Load forecast requirement (explicit forecast, update cadence) · Price premium |
| Emerging | Study requirements · Load ramp period · Hold harmless (formulaic backstop, incremental/marginal cost, no-harm analysis) · Resizing or reassigning contracted capacity · Exit fee |
| Declining | Customer type |

- `TARIFF_PARAMETERS` is replaced, a deliberate taxonomy migration with a BACKLOG entry, Python↔JS parity and new group labels. The 17 old keys map onto the new ones. Six map directly (min_load, contract_duration, monthly_demand_charge, credit_collateral, exit_fee, load_factor …). Elements LBL dropped, such as `clean_energy` and `econ_dev_payments`, move into `additional_terms`.
- **Each of the 29 tariffs is reassessed from its own docket or order.** Each included or partial element cites the source and quotes the provision. Where LBL's Appendix 1 lists the same tariff, its classification is a cross-check, not the source.
- **Toplines:** a curated `power_costs_brief` (seed JSON: dated paragraphs, each with source links). It covers 3–5 plain sentences on what to watch, including upcoming decisions with dates, and is updated by the daily refresh. It isn't generated text.
- **Readability:** the tab leads with the brief, then a "next decisions" list, then the directory. Element counts move into the detail and the element pane. The per-tariff number grid goes away from the main table.

## 4. Deep links

One scheme, matching the `#state/XX` pattern that already exists:

| Record | URL | Opens |
|---|---|---|
| Moratorium | `#moratorium/<id>` | Moratoriums tab, record modal |
| Policy | `#policy/<id>` (`?policy=` still read) | Policy tab, record modal |
| Tariff | `#tariff/<id>` | Power Costs, tariff modal |
| Rate case | `#ratecase/<id>` | Power Costs, rate-case row expanded and scrolled to |
| Site | `#site/<id>` | Sites, project detail |
| Company | `#company/<slug>` | Companies, company panel |
| Election | `#elections/<id>` (exists) | — |

- Opening a record writes its URL, and closing it restores the tab URL. Back/Forward follows the `_routing` rules in CLAUDE.md (Oct 18 lesson).
- Every table row and card has a real `<a href>` to its record URL, so middle-click, copy-link and crawlers work. "Related" links use the same URLs.
- The router is table-driven, with one `RECORD_ROUTES` map `{prefix: {view, load, open}}`. A test derives the expected prefixes from the record kinds in `RecordRef`, so a new kind can't ship without a route.

## Phasing (PRs)

1. Data model: RecordRef, migration, `links.json`, `commission_order`, tariff-legislation → Policy records. Also deep-link routes for all kinds; these are independent of the UI changes.
2. Policy tab combine plus the moratorium call-out, then the research pass for missing EOs, statutes and orders.
3. Power Costs: LBL 2026 taxonomy, 29 reassessments, brief and readability.
