"""Capture manual figures from the running PRBE dev server.

Assumes:
  - Backend running on localhost:8000
  - Frontend running on localhost:5173
  - Sample Highway Project has id=1 (default seed)
"""
from playwright.sync_api import sync_playwright
import time
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# Page-by-page capture spec.
# Each entry: (filename, url_path, optional setup JS, optional selector to screenshot)
# If selector is None we capture full viewport.
PAGES = [
    ('fig_1_1_project_list',    '/',                         None, None),
    ('fig_3_1_project_info',    '/project/1/info',           None, None),
    ('fig_3_2_segments_phases', '/project/1/segments',       None, None),
    ('fig_3_3_inflation_tables','/project/1/inflation',      None, None),
    ('fig_4_1_base_variability','/project/1/base-variability', None, None),
    ('fig_4_2_market_conditions','/project/1/market-conditions', None, None),
    ('fig_5_1_risk_identification', '/project/1/risk-id',    None, None),
    ('fig_5_1a_heat_maps',      '/project/1/risk-id',
        """
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === 'Triage');
        if (btn) btn.click();
        """, None),
    ('fig_5_2_risk_register',   '/project/1/risk-register',  None, None),
    ('fig_5_3_correlation',     '/project/1/correlation',    None, None),
    ('fig_5_4_minor_risks',     '/project/1/minor-risks',    None, None),
    ('fig_5_5_review_staging',  '/project/1/yoe',            None, None),
    ('fig_6_1_simulation',      '/project/1/simulation',     None, None),
    ('fig_7_1_summary',         '/project/1/results',        None, None),
    ('fig_7_2_distribution',    '/project/1/results',
        """
        const t = Array.from(document.querySelectorAll('button,a')).find(e => /distribution/i.test(e.textContent));
        if (t) t.click();
        """, None),
    ('fig_7_3_tornado',         '/project/1/results',
        """
        const t = Array.from(document.querySelectorAll('button,a')).find(e => /tornado/i.test(e.textContent));
        if (t) t.click();
        """, None),
    ('fig_7_4_tail_drivers',    '/project/1/results',
        """
        const t = Array.from(document.querySelectorAll('button,a')).find(e => /tail/i.test(e.textContent));
        if (t) t.click();
        """, None),
]

CLOSE_PANELS_JS = """
(() => {
    const closeBtns = Array.from(document.querySelectorAll('button')).filter(b => {
        const al = (b.getAttribute('aria-label')||'').toLowerCase();
        return al.includes('close') || b.textContent.trim() === '×';
    });
    closeBtns.forEach(b => b.click());
})();
"""

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1400, 'height': 1000})
        page = ctx.new_page()
        for fname, url, setup, selector in PAGES:
            print(f'Capturing {fname} <- {url}')
            try:
                page.goto(f'http://localhost:5173{url}', wait_until='networkidle', timeout=30000)
            except Exception as e:
                print(f'  warn load: {e}')
            time.sleep(2)
            page.evaluate(CLOSE_PANELS_JS)
            time.sleep(0.5)
            if setup:
                try:
                    page.evaluate(setup)
                    time.sleep(1)
                except Exception as e:
                    print(f'  warn setup: {e}')
            out_path = os.path.join(OUT, f'{fname}.png')
            try:
                if selector:
                    page.locator(selector).first.screenshot(path=out_path, timeout=10000)
                else:
                    page.screenshot(path=out_path, full_page=False)
                print(f'  ok -> {fname}.png')
            except Exception as e:
                print(f'  ERR {fname}: {e}')
        browser.close()

if __name__ == '__main__':
    capture()
