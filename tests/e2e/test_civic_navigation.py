"""The primary journeys: cross-directory search, sources and shareable comparison."""
import re

from playwright.sync_api import expect


def test_search_place_and_record_back(page, base_url):
    page.goto(base_url + '/?find=Pennsylvania#overview')
    expect(page.locator('#civic-search-status')).to_contain_text('records')
    expect(page.locator('#civic-places')).to_contain_text('Pennsylvania')
    page.locator('#civic-places a').first.click()
    expect(page.locator('#civic-place-heading')).to_have_text('Pennsylvania')
    expect(page.locator('#civic-results > li')).not_to_have_count(0)
    before = page.url
    page.locator('#civic-results h3 a').first.click()
    page.go_back()
    expect(page).to_have_url(before)
    expect(page.locator('#civic-place-heading')).to_have_text('Pennsylvania')


def test_compare_share_reload_and_remove(page, base_url):
    page.goto(base_url + '/?kind=agreement#overview')
    expect(page.locator('#civic-results input').first).to_be_visible()
    page.locator('#civic-results input').nth(0).check()
    page.locator('#civic-results input').nth(1).check()
    page.locator('#civic-compare-tray a').click()
    expect(page.locator('#civic-compare-grid article')).to_have_count(2)
    expect(page).to_have_url(re.compile('records=.*#benefits/compare'))
    page.reload()
    expect(page.locator('#civic-compare-grid article')).to_have_count(2)
    expect(page.locator('#civic-compare-grid')).to_contain_text('Terms')
    page.locator('#civic-compare-grid button').first.click()
    expect(page.locator('#civic-compare-grid article')).to_have_count(1)
    page.locator('#civic-compare-clear').click()
    expect(page.locator('#civic-compare-grid article')).to_have_count(0)


def test_search_failure_is_explicit_and_retryable(page, base_url):
    page.route('**/data/projects.json', lambda route: route.abort())
    page.goto(base_url + '/?find=Google#overview')
    expect(page.locator('#civic-search-status')).to_contain_text('Unavailable: projects')
    expect(page.locator('#civic-results > li')).not_to_have_count(0)
    page.unroute('**/data/projects.json')
    page.locator('#civic-retry').click()
    expect(page.locator('#civic-retry')).to_be_hidden()
    expect(page.locator('#civic-search-status')).not_to_contain_text('Unavailable')


def test_phone_primary_navigation_and_updates(page, base_url):
    page.set_viewport_size({'width': 375, 'height': 812})
    page.goto(base_url)
    # The first top line is readable on the first phone screen.
    expect(page.locator('[data-line-for="pledge"]')).not_to_be_empty()
    assert page.locator('[data-line-for="pledge"]').bounding_box()['y'] < 600
    for name in ['Overview', 'Community benefits']:
        expect(page.get_by_role('tab', name=name, exact=True)).to_be_in_viewport()
    # Updates has no tab (2026-11-23); Home's Latest links to it.
    page.locator('.home-all-updates').click()
    expect(page.locator('#civic-updates')).to_contain_text('Event date')
    page.locator('#civic-update-kind').select_option('record')
    expect(page.locator('#civic-updates-status')).to_contain_text('Record history since')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


def test_typing_then_leaving_does_not_rewrite_destination(page, base_url):
    page.goto(base_url)
    page.locator('#civic-query').fill('Virginia')
    page.locator('.home-all-updates').click()
    expect(page.locator('#civic-updates')).to_contain_text('Event date')
    expect(page).to_have_url(re.compile('#updates$'))
    expect(page.locator('#view-overview')).to_be_hidden()
