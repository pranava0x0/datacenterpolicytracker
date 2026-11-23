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
    expect(page).to_have_url(re.compile('records=.*#compare'))
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
    expect(page.locator('#home-latest-list li').first).to_be_visible()
    assert page.locator('#home-latest-list li').first.bounding_box()['y'] < 300
    expect(page.get_by_role('tab', name='Home', exact=True)).to_be_in_viewport()
    expect(page.locator('#browse-toggle')).to_be_in_viewport()
    expect(page.locator('#browse-menu')).not_to_have_attribute('open', '')
    page.get_by_role('button', name='All updates', exact=True).click()
    expect(page.locator('#civic-updates')).to_contain_text('Event date')
    page.locator('#civic-update-kind').select_option('record')
    expect(page.locator('#civic-updates-status')).to_contain_text('Record history since')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')


def test_typing_then_leaving_does_not_rewrite_destination(page, base_url):
    page.goto(base_url)
    page.locator('#civic-query').fill('Virginia')
    page.locator('#browse-toggle').click()
    page.locator('#tab-moratoriums').click()
    expect(page.locator('#moratoriums-tbody tr').first).to_be_visible()
    expect(page).to_have_url(re.compile('#moratoriums$'))
    expect(page.locator('#view-overview')).to_be_hidden()


def test_browse_closes_and_returns_keyboard_focus(page, base_url):
    page.goto(base_url)
    page.locator('#browse-toggle').click()
    expect(page.locator('#tab-moratoriums')).to_be_visible()
    page.keyboard.press('Escape')
    expect(page.locator('#browse-toggle')).to_be_focused()
    expect(page.locator('#tab-moratoriums')).to_be_hidden()
    page.locator('#browse-toggle').click()
    page.locator('#tab-moratoriums').click()
    expect(page.locator('#view-moratoriums')).to_be_visible()
    expect(page.locator('#browse-menu')).not_to_have_attribute('open', '')
    expect(page.locator('#main')).to_be_focused()


def test_agreements_have_one_local_navigation_row(page, base_url):
    page.goto(base_url + '/#policies/agreements')
    expect(page.locator('#view-policies .hero-title')).to_have_text('Agreements')
    expect(page.locator('#view-policies > .subtabs')).to_be_hidden()
    expect(page.locator('#subtab-cba-drafts')).to_be_visible()
    page.locator('#subtab-cba-drafts').click()
    expect(page.locator('#draft-plan-decision')).to_be_visible()
    page.locator('#browse-toggle').click()
    page.locator('#tab-policies').click()
    expect(page.locator('#view-policies .hero-title')).to_have_text('Policy')
    expect(page.locator('#view-policies > .subtabs')).to_be_visible()


def test_home_clears_search_and_back_restores_it(page, base_url):
    page.goto(base_url + '/?find=Pennsylvania#overview')
    expect(page.locator('#civic-results li').first).to_be_visible()
    page.locator('#tab-overview').click()
    expect(page.locator('#civic-home-content')).to_be_visible()
    expect(page.locator('#civic-query')).to_have_value('')
    page.go_back()
    expect(page.locator('#civic-query')).to_have_value('Pennsylvania')
    expect(page.locator('#civic-results li').first).to_be_visible()


def test_agreements_keyboard_focus_moves_to_visible_controls(page, base_url):
    page.goto(base_url + '/#policies')
    page.locator('#subtab-pol-principles').focus()
    page.keyboard.press('ArrowRight')
    expect(page.locator('#subtab-cba-strongest')).to_be_focused()
    expect(page.locator('#subtab-pol-principles')).to_be_hidden()
    page.keyboard.press('ArrowRight')
    expect(page.locator('#subtab-cba-all')).to_be_focused()
