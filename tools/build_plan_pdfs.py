"""Build the six downloadable plan packets from the same HTML shown in the tracker.

Run with the project's Playwright environment: python tools/build_plan_pdfs.py.
--check verifies the printable content and the shipped bytes without rewriting them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
from html import escape
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

DOCS = Path(__file__).resolve().parents[1] / "docs"
OUT = DOCS / "plans"
CSS = """
@page {size: Letter; margin: .64in .72in .7in}
body {font: 10.5pt/1.38 Arial,sans-serif;color:#202e3e;margin:0}
h1,h2,h3,summary {font-family:Georgia,serif;color:#111d35}
h1 {font-size:21pt;line-height:1.1;margin:6pt 0 12pt}
h2,h3,summary {break-after:avoid} h2 {font-size:17pt} h3,summary {font-size:13pt}
.brand,.bp-kicker {color:#465977;font-weight:bold} .brand {border-bottom:1pt solid;padding-bottom:5pt}
p,dl,ul {margin:5pt 0 8pt} dt {font-weight:bold;margin-top:8pt;break-after:avoid}
dd {margin:2pt 0 6pt} li {margin-bottom:4pt} a {color:#184776}
.bp-note {border-left:2pt solid #a3b1c0;padding-left:8pt} #common {break-before:page}
details {break-inside:avoid;margin:10pt 0} summary {font-weight:bold}
details dl {margin-left:10pt} details dt {display:inline;font-size:9.5pt} details dd {display:inline;margin:0}
details dd::after {content:"";display:block} details dt::after {content:": "}
"""
FOOTER = '<div style="font:9px Arial;width:100%;text-align:center;color:#465977">Data Center Policy Tracker · Working draft · <span class="pageNumber"></span> / <span class="totalPages"></span></div>'
LOG = logging.getLogger(__name__)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render_source(page: Page, key: str, base: str, policy: bool) -> str:
    if policy:
        page.locator("#draft-plan-kind").select_option(key)
    return page.evaluate("""({key,base,policy}) => {
      const blocks = policy ? ['draft-plan-content'] : [key,'common','pause','sources'];
      return blocks.map(id=>{
        const node=document.getElementById(id).cloneNode(true);
        node.querySelectorAll('.bp-actions,.bp-pdf').forEach(e=>e.remove());
        node.querySelectorAll('details').forEach(d=>d.open=true);
        node.querySelectorAll('a').forEach(a=>a.href=new URL(a.getAttribute('href'),base).href);
        const title=node.querySelector(policy?'h3':'h2');
        if(id===blocks[0]) {
          const h=document.createElement('h1');h.textContent=title.textContent;title.replaceWith(h);
        }
        return node.outerHTML;
      }).join('');
    }""", {"key": key, "base": base, "policy": policy})


def build(check: bool) -> None:
    path = OUT / "manifest.json"
    previous = json.loads(path.read_text()) if path.exists() else {}
    manifest = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        source = browser.new_page()
        source.goto((DOCS / "community-benefits.html").as_uri())
        base = source.locator('link[rel="canonical"]').get_attribute("href")
        assert base
        local_ids = source.locator("main > article").evaluate_all("els=>els.map(e=>e.id)")
        source.evaluate("document.body.append(Object.assign(document.createElement('div'),{id:'policy-guide'}))")
        code = (DOCS / "community-plans.js").read_text().replace("export function ", "function ")
        source.add_script_tag(content="(()=>{" + code + "\nrenderPlans(document.querySelector('#policy-guide'));})();")
        policy_ids = source.locator("#draft-plan-kind option").evaluate_all("els=>els.map(e=>e.value)")
        printable = browser.new_page()
        if not check:
            OUT.mkdir(exist_ok=True)
        for key in [*local_ids, *policy_ids]:
            policy = key in policy_ids
            body = render_source(source, key, base, policy)
            target = base.rsplit("/", 1)[0] + "/#policies/agreements/drafts" if policy else base + "#" + key
            name = f"{key}-community-benefits.pdf"
            html = (f'<!doctype html><html lang="en"><meta charset="utf-8"><title>{escape(key.title())} community benefits draft</title>'
                    f'<style>{CSS}</style><div class="brand">Data Center Policy Tracker · Community benefits plans</div>{body}'
                    f'<p><a href="{escape(target)}">Read the guide and get the editable draft online</a></p></html>')
            fingerprint = digest((html + FOOTER).encode())
            product = OUT / name
            cached = previous.get(name, {})
            current = (cached.get("source") == fingerprint and product.exists()
                       and cached.get("pdf") == digest(product.read_bytes()))
            if not check and not current:
                printable.set_content(html)
                printable.pdf(path=str(OUT / name), prefer_css_page_size=True, display_header_footer=True,
                              header_template="<span></span>", footer_template=FOOTER)
            data = (OUT / name).read_bytes()
            if not data.startswith(b"%PDF-"):
                raise ValueError(f"{name}: invalid PDF")
            manifest[name] = {"source": fingerprint, "pdf": digest(data)}
        browser.close()
    if check:
        if json.loads(path.read_text()) != manifest:
            raise SystemExit("Plan PDFs are stale. Run python tools/build_plan_pdfs.py.")
    else:
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    LOG.info("%s %d plan PDFs", "Checked" if check else "Built", len(manifest))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    build(parser.parse_args().check)
