"""Apply the LBL 2026 reassessments (out_A/out_B.jsonl) to data/seed/tariffs.json.

Agent findings replace each tariff's `parameters`. Old elements with no LBL
2026 equivalent (duration_flexibility, econ_dev_payments) move to
additional_terms so nothing curated is lost. Elements whose quote failed the
probe (listed in a MISS file) are dropped. Idempotent: re-running with the
same inputs yields the same file.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD_ONLY = {
    "duration_flexibility": "Contract term flexibility",
    "econ_dev_payments": "Economic development payments",
}


def misses() -> set[str]:
    out = set()
    for f in HERE.glob("probe_*.txt"):
        for line in f.read_text().splitlines():
            m = re.match(r"MISS\s+(\S+):", line)
            if m:
                out.add(m.group(1))
    return out


def main() -> int:
    found = {}
    for f in sorted(HERE.glob("out_*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                d = json.loads(line)
                found[d["id"]] = d
    bad = misses()
    path = ROOT / "data/seed/tariffs.json"
    data = json.loads(path.read_text())
    done = 0
    for t in data["tariffs"]:
        d = found.get(t["id"])
        if d is None:
            continue
        old = t.get("parameters", {})
        params = {}
        for key, e in d["elements"].items():
            if f"{t['id']}:{key}" in bad:
                continue
            p = {"status": e["status"], "detail": e["detail"].strip()}
            if e.get("source_url") and e["source_url"] != t["source_url"]:
                p["source_url"] = e["source_url"]
            if e.get("verbatim"):
                p["verbatim"] = e["verbatim"].strip()
            params[key] = p
        # A sub-element whose parent was dropped (a probe miss) would fail
        # validation; drop the orphan rather than invent a parent.
        sys.path.insert(0, str(ROOT))
        from schema import TARIFF_PARAMETER_PARENT
        params = {k: v for k, v in params.items() if k not in TARIFF_PARAMETER_PARENT or TARIFF_PARAMETER_PARENT[k] in params}
        terms = t.setdefault("additional_terms", [])
        have = {a["term"] for a in terms}
        for key, label in OLD_ONLY.items():
            if key in old and label not in have:
                term = {"term": label, "detail": old[key]["detail"]}
                if old[key].get("source_url"):
                    term["source_url"] = old[key]["source_url"]
                terms.append(term)
        t["parameters"] = params
        done += 1
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"applied {done} of {len(data['tariffs'])} tariffs; dropped {len(bad)} probe misses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
