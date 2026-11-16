"""v7: typed cross-record links (RecordRef) and the derived links.json graph."""
import json
import re
from pathlib import Path

import pytest

import refresh
from schema import RECORD_KINDS, RELATION_INVERSE, RELATION_LABELS, RECORD_RELATIONS

ROOT = Path(__file__).resolve().parent.parent
APP = (ROOT / "docs" / "app.js").read_text()


def _payloads():
    return {name: refresh._load_payload(name, model) for name, model in refresh.PAYLOAD_FILES.items()}


@pytest.fixture(scope="module")
def payloads():
    return _payloads()


def _js_array(name):
    m = re.search(rf"const {name} = \[(.*?)\];", APP, re.S)
    return re.findall(r'"([a-z_]+)"', m.group(1))


def _js_object_keys(name):
    m = re.search(rf"const {name} = \{{(.*?)\}};", APP, re.S)
    return re.findall(r"^\s*([a-z_]+):", m.group(1), re.M)


def test_record_kinds_match_frontend():
    assert _js_array("RECORD_KINDS") == list(RECORD_KINDS)


def test_relation_labels_match_frontend():
    assert _js_object_keys("RELATION_LABELS") == list(RELATION_LABELS)
    assert set(RELATION_LABELS) == set(RECORD_RELATIONS)


def test_every_relation_has_an_inverse_that_round_trips():
    for rel in RECORD_RELATIONS:
        assert RELATION_INVERSE[RELATION_INVERSE[rel]] == rel, rel


def test_committed_links_resolve(payloads):
    graph, errors = refresh._build_links(payloads)
    assert errors == []
    assert graph, "expected at least one link"


def test_every_link_has_its_inverse(payloads):
    graph, _ = refresh._build_links(payloads)
    for src, edges in graph.items():
        skind, sid = src.split(":", 1)
        for e in edges:
            back = graph.get(f"{e['kind']}:{e['id']}", [])
            assert any(
                b["kind"] == skind and b["id"] == sid and b["relation"] == RELATION_INVERSE[e["relation"]]
                for b in back
            ), (src, e)


def test_unknown_target_is_an_error(payloads):
    pol = payloads["policies"].policies[0]
    from schema import RecordRef
    original = list(pol.related)
    pol.related.append(RecordRef(kind="tariff", id="no-such-tariff"))
    try:
        _, errors = refresh._build_links(payloads)
        assert any("no-such-tariff" in e for e in errors)
    finally:
        pol.related[:] = original


def test_self_link_is_an_error(payloads):
    pol = payloads["policies"].policies[0]
    from schema import RecordRef
    original = list(pol.related)
    pol.related.append(RecordRef(kind="policy", id=pol.id))
    try:
        _, errors = refresh._build_links(payloads)
        assert any("itself" in e for e in errors)
    finally:
        pol.related[:] = original


def test_tariff_legislation_policy_ids_resolve_and_link(payloads):
    graph, _ = refresh._build_links(payloads)
    found = 0
    for t in payloads["tariffs"].tariffs:
        for leg in t.legislation:
            if leg.policy_id:
                found += 1
                edges = graph[f"tariff:{t.id}"]
                assert {"kind": "policy", "id": leg.policy_id, "relation": "implements"} in edges
    assert found, "expected tariff legislation to point at Policy records"


def test_links_json_is_built_and_current(payloads):
    built = json.loads((ROOT / "docs" / "data" / "links.json").read_text())["links"]
    graph, _ = refresh._build_links(payloads)
    assert built == json.loads(json.dumps(graph)), "links.json is stale — re-run refresh.py"
