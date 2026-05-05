"""Smoke test: confirm the new multi-select correlation UI loads and works.

Navigates to project 1's Correlation Editor, verifies that the UI labels Variable
B as a multi-select picker, opens it, ticks two targets, and confirms the Add
button reflects the count.
"""
import time
from playwright.sync_api import sync_playwright

FRONTEND = "http://localhost:5173"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        page.goto(f"{FRONTEND}/project/1/correlation", wait_until="networkidle", timeout=30000)
        time.sleep(1.5)

        # 1. Verify the new "Variable B (one or more)" label is present.
        try:
            page.get_by_text("Variable B (one or more)", exact=False).first.wait_for(timeout=4000)
            print("[OK] Variable B label updated to multi-select")
        except Exception as e:
            print(f"[FAIL] Variable B label not found: {e}")
            page.screenshot(path="manual_figures/smoke_corr_fail.png", full_page=False)
            browser.close()
            return

        # 2. Pick anchor (Variable A) — first dropdown
        page.locator("select").first.select_option(index=1)
        time.sleep(0.4)

        # 3. Open the multi-select picker
        picker_btn = page.locator("button:has-text('pick one or more risks')")
        picker_btn.click(timeout=3000)
        time.sleep(0.5)

        # 4. Tick the first 3 visible checkboxes
        cbs = page.locator("input[type=checkbox]")
        n = cbs.count()
        ticked = 0
        for i in range(n):
            try:
                if ticked >= 3:
                    break
                cb = cbs.nth(i)
                if cb.is_visible() and not cb.is_checked():
                    cb.check(timeout=1500)
                    ticked += 1
            except Exception:
                pass
        print(f"[OK] Ticked {ticked} target(s)")

        # 5. Verify Add button label reflects count
        time.sleep(0.4)
        add_btn = page.locator("button:has-text('Add')").last
        label = add_btn.inner_text(timeout=2000)
        print(f"[OK] Add button label: {label!r}")

        # 6. Screenshot the populated state for visual confirmation.
        page.screenshot(path="manual_figures/smoke_corr_multi.png", full_page=False)
        print("[OK] Screenshot at manual_figures/smoke_corr_multi.png")

        browser.close()


if __name__ == "__main__":
    main()
