"""Capture fig_5_3a_correlation_multiselect.png for the v2.2.1 manual update.

Shows the Correlation Editor with: Variable A picked, the multi-select picker
open with 3 targets ticked, the Add button label reading "Add 3 Pairs",
and the chip row visible with the conflict-count badge if applicable.
"""
import os
import time
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
FRONTEND = "http://localhost:5173"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        page.goto(f"{FRONTEND}/project/1/correlation", wait_until="networkidle", timeout=30000)
        time.sleep(1.5)

        # Pick Variable A (anchor)
        page.locator("select").first.select_option(index=1)
        time.sleep(0.4)

        # Open the multi-select picker
        page.locator("button:has-text('pick one or more risks')").click(timeout=3000)
        time.sleep(0.5)

        # Tick 3 visible checkboxes inside the picker
        cbs = page.locator("input[type=checkbox]")
        ticked = 0
        for i in range(cbs.count()):
            try:
                if ticked >= 3:
                    break
                cb = cbs.nth(i)
                if cb.is_visible() and not cb.is_checked():
                    cb.check(timeout=1500)
                    ticked += 1
            except Exception:
                pass

        # Bump the coefficient to 0.5 for a more illustrative shot
        coef_input = page.locator("input[type=number]").first
        try:
            coef_input.fill("0.5")
            coef_input.press("Tab")
        except Exception:
            pass

        # Resolve the bounding rectangle of the "Add Correlation Pair" card so we
        # only capture the relevant region (form + chips + open picker).
        time.sleep(0.6)
        bbox = page.evaluate("""
            () => {
                const headings = Array.from(document.querySelectorAll('h3, .card-header h3'));
                const h = headings.find(el => /add correlation pair/i.test(el.textContent || ''));
                if (!h) return null;
                let scope = h;
                for (let i = 0; i < 6 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && scope.classList && scope.classList.contains('card')) break;
                }
                if (!scope) return null;
                const r = scope.getBoundingClientRect();
                // Extend the height enough to include the open picker dropdown
                // which is positioned absolutely under Variable B.
                return {
                    x: Math.max(0, r.x - 6),
                    y: Math.max(0, r.y - 6),
                    width: Math.min(1380, r.width + 12),
                    height: Math.min(900, r.height + 380),
                };
            }
        """)
        out = os.path.join(OUT, "fig_5_3a_correlation_multiselect.png")
        if bbox and bbox.get("width") and bbox.get("height"):
            page.screenshot(path=out, clip=bbox)
        else:
            page.screenshot(path=out, full_page=False)
        print(f"ok -> {out}")
        browser.close()


if __name__ == "__main__":
    main()
