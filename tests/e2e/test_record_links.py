"""v7: every record kind has its own URL, and panels show derived links."""

import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e

DATA = Path(__file__).resolve().parents[2] / "docs" / "data"
APP = (Path(__file__).resolve().parents[2] / "docs" / "app.js").read_text()


def _first(name, key):
    return json.loads((DATA / f"{name}.json").read_text())[key][0]


def test_every_record_kind_has_a_route():
    kinds = re.findall(r'"([a-z_]+)"', re.search(r"const RECORD_KINDS = \[(.*?)\];", APP, re.S).group(1))
    routed = set(re.findall(r'kind: "([a-z_]+)"', re.search(r"const RECORD_ROUTES = \{(.*?)\n\};", APP, re.S).group(1)))
    assert set(kinds) == routed


def test_moratorium_url_opens_its_record(page: Page, base_url):
    m = _first("moratoriums", "moratoriums")
    page.goto(f"{base_url}/?i=m#moratorium/{m['id']}")
    expect(page.locator("#moratorium-modal")).to_be_visible()
    expect(page.locator("#md-jurisdiction")).to_have_text(m["jurisdiction"])
    assert page.url.endswith(f"#moratorium/{m['id']}")
    expect(page.locator("#md-permalink")).to_have_attribute("href", f"#moratorium/{m['id']}")


def test_closing_a_record_restores_the_view_url(page: Page, base_url):
    page.goto(f"{base_url}/?i=c#moratoriums")
    page.locator("#moratoriums-tbody tr").first.click()
    expect(page.locator("#moratorium-modal")).to_be_visible()
    assert re.search(r"#moratorium/[a-z0-9-]+$", page.url)
    page.keyboard.press("Escape")
    expect(page.locator("#moratorium-modal")).to_be_hidden()
    assert page.url.endswith("#moratoriums")


def test_tariff_url_opens_its_record(page: Page, base_url):
    t = _first("tariffs", "tariffs")
    page.goto(f"{base_url}/?i=t#tariff/{t['id']}")
    expect(page.locator("#tariff-modal")).to_be_visible()
    assert page.url.endswith(f"#tariff/{t['id']}")


def test_rate_case_url_marks_its_row(page: Page, base_url):
    rc = _first("rate_cases", "rate_cases")
    page.goto(f"{base_url}/?i=r#ratecase/{rc['id']}")
    expect(page.locator(f"#rc-{rc['id']}")).to_have_class(re.compile("is-target"))
    expect(page.locator(f"#rc-{rc['id']} .rc-perma")).to_have_attribute("href", f"#ratecase/{rc['id']}")


def test_policy_url_opens_its_record(page: Page, base_url):
    p = _first("policies", "policies")
    page.goto(f"{base_url}/?i=p#policy/{p['id']}")
    expect(page.locator("#policy-modal")).to_be_visible()
    assert f"policy={p['id']}" in page.url


def test_site_url_opens_its_record(page: Page, base_url):
    p = _first("projects", "projects")
    page.goto(f"{base_url}/?i=s#site/{p['id']}")
    expect(page.locator("#project-detail")).to_be_visible()
    assert f"project={p['id']}" in page.url


def test_company_url_opens_its_panel(page: Page, base_url):
    page.goto(f"{base_url}/?i=co#company/meta")
    expect(page.locator("#company-detail")).to_be_visible()
    expect(page.locator("#cd-name")).to_have_text("Meta")
    assert page.url.endswith("#company/meta")


def test_related_links_render_both_directions(page: Page, base_url):
    links = json.loads((DATA / "links.json").read_text())["links"]
    # A tariff authorized by a law shows the law; the law's panel shows the tariff.
    src = next(k for k, v in links.items() if k.startswith("tariff:") and any(e["kind"] == "policy" for e in v))
    tid = src.split(":", 1)[1]
    pid = next(e["id"] for e in links[src] if e["kind"] == "policy")
    page.goto(f"{base_url}/?i=rl#tariff/{tid}")
    expect(page.locator("#td-related")).to_be_visible()
    link = page.locator(f'#td-related-list a[href="#policy/{pid}"]')
    expect(link).to_be_visible()
    link.click()
    expect(page.locator("#policy-modal")).to_be_visible()
    expect(page.locator(f'#pd-related-list a[href="#tariff/{tid}"]')).to_be_visible()
