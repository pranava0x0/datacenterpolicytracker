import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from taxonomy import GROUPS, ELEMENTS
root = Path(sys.argv[1])

def py_block():
    L = []
    L.append("# v7 (2026-11-16): the element taxonomy follows LBL's 2026 update, Frick,")
    L.append("# Cappers et al., \"Electricity Rate Designs for Large Loads: Evolving")
    L.append("# Practices and Opportunities, 2026 Update\" (LBNL, Aug 10 2026), which")
    L.append("# reviewed 55 tariffs and sorted 18 elements (plus 12 sub-elements) by how")
    L.append("# common they are and whether adoption is rising. Groups are LBL's four")
    L.append("# practice types. Changing this list is a migration: BACKLOG entry, the JS")
    L.append("# mirrors in app.js, and every tariff re-keyed (parity-tested).")
    L.append("TARIFF_PARAMETER_GROUPS: tuple[tuple[str, str], ...] = (")
    for k, l in GROUPS: L.append(f"    ({k!r}, {l!r}),".replace("'", '"'))
    L.append(")\n")
    L.append("TARIFF_PARAMETERS: tuple[str, ...] = (")
    for e in ELEMENTS: L.append(f'    "{e[0]}",')
    L.append(")\n")
    L.append("TARIFF_PARAMETER_LABELS: dict[str, str] = {")
    for e in ELEMENTS: L.append(f'    "{e[0]}": {json.dumps(e[1])},')
    L.append("}\n")
    L.append("# One plain-English line per element (tooltips and the element pane).")
    L.append("TARIFF_PARAMETER_DESCRIPTIONS: dict[str, str] = {")
    for e in ELEMENTS: L.append(f'    "{e[0]}": {json.dumps(e[5])},')
    L.append("}\n")
    L.append("TARIFF_PARAMETER_GROUP_OF: dict[str, str] = {")
    for e in ELEMENTS: L.append(f'    "{e[0]}": "{e[2]}",')
    L.append("}\n")
    L.append("# Sub-elements nest under a parent element (LBL Appendix 2). A tariff that")
    L.append("# includes a sub-element must include its parent (validated on Tariff).")
    L.append("TARIFF_PARAMETER_PARENT: dict[str, str] = {")
    for e in ELEMENTS:
        if e[3]: L.append(f'    "{e[0]}": "{e[3]}",')
    L.append("}\n")
    L.append("# How many of LBL's 55 sampled tariffs include each element (Appendix 2).")
    L.append("# Context for readers, not a score.")
    L.append("TARIFF_PARAMETER_LBL_COUNT: dict[str, int] = {")
    for e in ELEMENTS: L.append(f'    "{e[0]}": {e[4]},')
    L.append("}\n")
    L.append("TARIFF_LBL_SAMPLE_SIZE = 55\n")
    return "\n".join(L) + "\n"

def js_block():
    L = []
    L.append("// v7: LBL 2026 update taxonomy. Mirrors schema.py (parity-tested).")
    L.append("const TARIFF_PARAMETER_GROUPS = [")
    for k, l in GROUPS: L.append(f'  ["{k}", "{l}"],')
    L.append("];")
    L.append("const TARIFF_PARAMETERS = [")
    for e in ELEMENTS: L.append(f'  "{e[0]}",')
    L.append("];")
    L.append("const TARIFF_PARAMETER_LABELS = {")
    for e in ELEMENTS: L.append(f'  {e[0]}: {json.dumps(e[1])},')
    L.append("};")
    L.append("const TARIFF_PARAMETER_DESCRIPTIONS = {")
    for e in ELEMENTS: L.append(f'  {e[0]}: {json.dumps(e[5])},')
    L.append("};")
    L.append("const TARIFF_PARAMETER_GROUP_OF = {")
    for e in ELEMENTS: L.append(f'  {e[0]}: "{e[2]}",')
    L.append("};")
    L.append("const TARIFF_PARAMETER_PARENT = {")
    for e in ELEMENTS:
        if e[3]: L.append(f'  {e[0]}: "{e[3]}",')
    L.append("};")
    L.append("const TARIFF_PARAMETER_LBL_COUNT = {")
    for e in ELEMENTS: L.append(f'  {e[0]}: {e[4]},')
    L.append("};")
    L.append("const TARIFF_LBL_SAMPLE_SIZE = 55;")
    return "\n".join(L) + "\n"

sp = root / "schema.py"; s = sp.read_text()
i = s.index("# The five LBL element groups, in the brief's order. (group_key, label).")
j = s.index("# Per-parameter coverage status.")
s = s[:i] + py_block() + s[j:]
s = s.replace('''    "TARIFF_PARAMETER_GROUP_OF",''', '''    "TARIFF_PARAMETER_GROUP_OF",
    "TARIFF_PARAMETER_PARENT",
    "TARIFF_PARAMETER_LBL_COUNT",''', 1)
sp.write_text(s)
ap = root / "docs/app.js"; a = ap.read_text()
i = a.index("// The five LBL element groups, in the brief's order: [group_key, label].")
j = a.index("const TARIFF_PARAMETER_GROUP_OF = {", i)
j = a.index("};\n", j) + 3
a = a[:i] + js_block() + a[j:]
ap.write_text(a)
print("ok")
