"""Re-capture figures that failed or needed a simulation run."""
from playwright.sync_api import sync_playwright
import time
import os

OUT = os.path.dirname(os.path.abspath(__file__))

CLOSE = """
(() => {
    const closeBtns = Array.from(document.querySelectorAll('button')).filter(b => {
        const al = (b.getAttribute('aria-label')||'').toLowerCase();
        return al.includes('close') || b.textContent.trim() === '×';
    });
    closeBtns.forEach(b => b.click());
})();
"""

def click_by_text(page, text_regex):
    """Click first button/link whose visible text matches regex."""
    return page.evaluate(f"""
        const els = Array.from(document.querySelectorAll('button, a'));
        const r = new RegExp({text_regex!r}, 'i');
        const el = els.find(e => r.test(e.textContent.trim()));
        if (el) {{ el.click(); return true; }}
        return false;
    """)

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 1400, 'height': 1000})
    page = ctx.new_page()

    # Fig 4.1: Base Variability (needed more wait)
    print('Fig 4.1 Base Variability')
    page.goto('http://localhost:5173/project/1/base-variability', wait_until='networkidle', timeout=30000)
    time.sleep(5)
    page.evaluate(CLOSE); time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT, 'fig_4_1_base_variability.png'))

    # Fig 7.1 Results Summary
    print('Fig 7.1 Results summary')
    page.goto('http://localhost:5173/project/1/results', wait_until='networkidle', timeout=30000)
    time.sleep(5)
    page.evaluate(CLOSE); time.sleep(0.5)
    page.screenshot(path=os.path.join(OUT, 'fig_7_1_summary.png'))

    # Fig 7.2 Distribution Charts - click Distribution tab
    print('Fig 7.2 Distribution')
    page.goto('http://localhost:5173/project/1/results', wait_until='networkidle', timeout=30000)
    time.sleep(3)
    page.evaluate(CLOSE); time.sleep(0.5)
    page.evaluate("""
        const btn = Array.from(document.querySelectorAll('button, a')).find(e => /distribution/i.test(e.textContent.trim()));
        if (btn) btn.click();
    """)
    time.sleep(2)
    page.screenshot(path=os.path.join(OUT, 'fig_7_2_distribution.png'))

    # Fig 7.3 Tornado
    print('Fig 7.3 Tornado')
    page.goto('http://localhost:5173/project/1/results', wait_until='networkidle', timeout=30000)
    time.sleep(3)
    page.evaluate(CLOSE); time.sleep(0.5)
    page.evaluate("""
        const btn = Array.from(document.querySelectorAll('button, a')).find(e => /tornado/i.test(e.textContent.trim()));
        if (btn) btn.click();
    """)
    time.sleep(2)
    page.screenshot(path=os.path.join(OUT, 'fig_7_3_tornado.png'))

    # Fig 7.4 Tail Drivers
    print('Fig 7.4 Tail')
    page.goto('http://localhost:5173/project/1/results', wait_until='networkidle', timeout=30000)
    time.sleep(3)
    page.evaluate(CLOSE); time.sleep(0.5)
    page.evaluate("""
        const btn = Array.from(document.querySelectorAll('button, a')).find(e => /tail/i.test(e.textContent.trim()));
        if (btn) btn.click();
    """)
    time.sleep(2)
    page.screenshot(path=os.path.join(OUT, 'fig_7_4_tail_drivers.png'))

    browser.close()
    print('done')
