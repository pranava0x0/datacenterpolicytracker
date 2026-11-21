"""Material edits are news; metadata refreshes are not."""
import json
from datetime import date

import refresh


class Payload:
    def __init__(self, records: dict) -> None:
        self.records = records

    def model_dump(self, **kwargs) -> dict:
        return self.records


def test_history_baseline_capture_only_material_and_repeat(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(refresh, 'OUT_DIR', tmp_path)
    names = ['projects', 'policies', 'moratoriums', 'tariffs', 'rate_cases', 'companies']
    data = {name: [] for name in names}
    data['rate_cases'] = [{'id': 'test', 'title': 'A case', 'status': 'pending', 'captured_at': '2026-11-01', 'source_url': 'https://example.org'}]
    for name in names:
        (tmp_path / f'{name}.json').write_text(json.dumps({name: data[name]}))
    payloads = {name: Payload({name: data[name]}) for name in names}
    today = date(2026, 11, 21)
    refresh._write_changes(payloads, today=today)
    assert json.loads((tmp_path / 'changes.json').read_text())['changes'] == []
    data['rate_cases'][0]['captured_at'] = '2026-11-21'
    refresh._write_changes(payloads, today=today)
    assert json.loads((tmp_path / 'changes.json').read_text())['changes'] == []
    data['rate_cases'][0]['status'] = 'approved'
    refresh._write_changes(payloads, today=today)
    history = json.loads((tmp_path / 'changes.json').read_text())
    assert history['changes'][0]['fields'] == ['status']
    assert history['changes'][0]['href'] == '#ratecase/test'
    (tmp_path / 'rate_cases.json').write_text(json.dumps({'rate_cases': data['rate_cases']}))
    before = (tmp_path / 'changes.json').read_bytes()
    refresh._write_changes(payloads, today=today)
    assert (tmp_path / 'changes.json').read_bytes() == before


def test_international_and_election_edits_have_resolvable_routes(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(refresh, 'OUT_DIR', tmp_path)
    data = {
        'international': {'policies': [{'id': 'ie-policy', 'country': 'IE', 'title': 'Connection rule', 'status': 'proposed'}]},
        'elections': {'races': [{'id': 'pa-governor', 'jurisdiction': 'Pennsylvania', 'result': {'status': 'unreported'}}]},
    }
    for name, payload in data.items():
        (tmp_path / f'{name}.json').write_text(json.dumps(payload))
    payloads = {name: Payload(records) for name, records in data.items()}
    refresh._write_changes(payloads, today=date(2026, 11, 21))
    data['international']['policies'][0]['status'] = 'in_effect'
    data['elections']['races'][0]['result']['status'] = 'reported'
    refresh._write_changes(payloads, today=date(2026, 11, 22))
    edits = json.loads((tmp_path / 'changes.json').read_text())['changes']
    assert {entry['href'] for entry in edits} == {'#country/IE', '#elections/pa-governor'}
    assert {tuple(entry['fields']) for entry in edits} == {('status',), ('result',)}


def test_published_actions_are_complete_and_observations_are_distinct() -> None:
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / 'docs' / 'data'
    actions = json.loads((root / 'actions.json').read_text())['actions']
    home = json.loads((root / 'home.json').read_text())['latest']
    assert len(actions) > len(home)
    assert [item['date'] for item in actions] == sorted((item['date'] for item in actions), reverse=True)
    observations = [item for item in actions if 'join dates unpublished' in item['title']]
    assert observations and all(item['date_kind'] == 'observed' for item in observations)
    assert any(item.get('href', '').startswith('#country/') for item in actions)
    assert any(item.get('href', '').startswith('#elections/') for item in actions)
