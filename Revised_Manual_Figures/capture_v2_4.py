"""Capture v2.3 / v2.4 manual figures from the running CASTR dev server.

Targets the new UI shipped today:
  - fig_5_1d_envelope_sme_reviewed.png   — Triage envelope card with the new
                                            SME-Reviewed EV / SME Implied %
                                            columns, sortable headers, and
                                            Risks (Active / Reviewed / Inactive)
                                            count column.
  - fig_7_5_distribution_health.png      — Distribution Health card on the
                                            Summary Statistics tab (overall
                                            traffic-light, P10–P90 spread /
                                            skewness / kurtosis cells,
                                            Variance Concentration, Risk
                                            Register Coverage).
  - fig_7_5a_component_by_component.png  — Contingency by Component placeholder
                                            (when no Component Analysis run).
  - fig_7_3b_tornado_variance.png        — Spearman Tornado with the new
                                            "% var" annotations on risk_cost
                                            rows.
  - fig_7_3c_risk_impact_sort.png        — Risk Impact tornado with the
                                            Sort: EV / Sort: Variance Share
                                            toggle.
  - fig_7_6_what_if_sensitivity.png      — What-If Sensitivity tab in its
                                            baseline state.
  - fig_7_6a_what_if_deactivated.png     — What-If Sensitivity tab with one
                                            risk deactivated, showing engine
                                            re-run badge + Δ vs baseline.

Assumes:
  - Backend running on http://localhost:8000
  - Frontend running on http://localhost:5173
  - Project id=13 has a recent simulation run with a populated risk register
    (16 risks, all cost+sched).

Run from the repo root:
    python manual_figures/capture_v2_4.py
"""
from __future__ import annotations

import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUT = os.path.dirname(os.path.abspath(__file__))
FRONTEND = "http://localhost:5173"
PROJECT_ID = 13

VIEWPORT = {"width": 1400, "height": 1000}


def safe_goto(page, url, *, wait="networkidle", timeout=30000):
    try:
        page.goto(url, wait_until=wait, timeout=timeout)
    except PWTimeout:
        page.goto(url, wait_until="domcontentloaded", timeout=timeout)


def capture(page, selector_text, out_name, *, wait_ms=600, scroll_to=True,
            full_page=False, viewport_only=False):
    """Capture an element by visible text or a CSS selector. Falls back to
    full-page screenshot when element not found."""
    out_path = os.path.join(OUT, out_name)
    try:
        page.wait_for_timeout(wait_ms)
        if selector_text.startswith("css:"):
            el = page.locator(selector_text[4:]).first
        else:
            el = page.locator(f'text={selector_text}').first
        if scroll_to:
            el.scroll_into_view_if_needed(timeout=4000)
        page.wait_for_timeout(wait_ms)
        # Find the enclosing card (class is exactly 'card', not 'card-header'
        # or 'card-body'). Match class as a whitespace-separated word.
        card = el.locator(
            "xpath=ancestor::div[contains(concat(' ',normalize-space(@class),' '),' card ')][1]"
        )
        target = card if card.count() > 0 else el
        if viewport_only:
            page.screenshot(path=out_path)
        else:
            target.screenshot(path=out_path)
        print(f"  [ok] {out_name}")
    except Exception as e:
        print(f"  [fail] {out_name}: {e}")
        if full_page:
            try:
                page.screenshot(path=out_path, full_page=True)
                print(f"    fallback full-page saved")
            except Exception as e2:
                print(f"    fallback failed: {e2}")


def click_button_with_text(page, text):
    """Click the first button whose text matches exactly."""
    page.evaluate(f"""
    () => {{
        const btns = [...document.querySelectorAll('button, a')];
        const t = btns.find(b => b.textContent.trim() === {text!r});
        if (t) t.click();
    }}
    """)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=VIEWPORT)
        page = ctx.new_page()

        # ─────────────────────────────────────────────────────────────────
        # 1. Triage envelope with SME-Reviewed columns
        # ─────────────────────────────────────────────────────────────────
        print("Triage envelope (Risk Identification page) ...")
        safe_goto(page, f"{FRONTEND}/project/{PROJECT_ID}/risk-id")
        page.wait_for_timeout(2000)

        # Switch to Triage view
        click_button_with_text(page, "Triage")
        page.wait_for_timeout(1500)

        # Expand the envelope panel if collapsed
        page.evaluate("""
        () => {
          const panel = document.querySelector('[data-testid=\"envelope-panel\"]');
          if (panel && !panel.textContent.includes('Project basis')) {
            panel.querySelector('button').click();
          }
        }
        """)
        page.wait_for_timeout(800)

        capture(page, 'css:[data-testid="envelope-panel"]',
                "fig_5_1d_envelope_sme_reviewed.png",
                wait_ms=600)

        # ─────────────────────────────────────────────────────────────────
        # 2. Results page → Summary tab → Distribution Health card
        # ─────────────────────────────────────────────────────────────────
        print("Distribution Health card (Results) ...")
        safe_goto(page, f"{FRONTEND}/project/{PROJECT_ID}/results")
        page.wait_for_timeout(2500)

        # The Summary tab is default
        capture(page, "Distribution Health",
                "fig_7_5_distribution_health.png",
                wait_ms=600)

        # ─────────────────────────────────────────────────────────────────
        # 3. Component by Component placeholder
        # ─────────────────────────────────────────────────────────────────
        # (Same card; sub-section. Take a viewport-cropped capture by
        # scrolling the section into view and using element shot.)
        capture(page, "Contingency by Component",
                "fig_7_5a_component_by_component.png",
                wait_ms=600)

        # ─────────────────────────────────────────────────────────────────
        # 4. Tornado tab — Spearman with %var annotations
        # ─────────────────────────────────────────────────────────────────
        print("Tornado Spearman with % var ...")
        click_button_with_text(page, "Tornado")
        page.wait_for_timeout(1800)

        # Make sure we're on the YOE Spearman tornado (default)
        capture(page, "Spearman Rank Correlation",
                "fig_7_3b_tornado_variance.png",
                wait_ms=800)

        # ─────────────────────────────────────────────────────────────────
        # 5. Tornado tab — Risk Impact view with sort toggle
        # ─────────────────────────────────────────────────────────────────
        print("Risk Impact tornado with sort toggle ...")
        click_button_with_text(page, "Risk Impact")
        page.wait_for_timeout(1500)

        capture(page, "css:button:has-text('Sort: Variance Share')",
                "fig_7_3c_risk_impact_sort.png",
                wait_ms=800)

        # ─────────────────────────────────────────────────────────────────
        # 6. What-If Sensitivity tab — baseline state
        # ─────────────────────────────────────────────────────────────────
        print("What-If Sensitivity tab (baseline) ...")
        click_button_with_text(page, "What-If Sensitivity")
        page.wait_for_timeout(2200)

        # Target the card whose <h3> is "What-If Sensitivity" — the first
        # locator-by-text would hit the TAB button (also reading "What-If
        # Sensitivity"), not the panel header. Using a CSS selector with
        # :has() pins us to the card div.
        capture(page, "css:div.card:has(h3:text-is('What-If Sensitivity'))",
                "fig_7_6_what_if_sensitivity.png",
                wait_ms=1000, scroll_to=True)

        # ─────────────────────────────────────────────────────────────────
        # 7. What-If with one risk deactivated (engine re-run path)
        # ─────────────────────────────────────────────────────────────────
        print("What-If Sensitivity tab (deactivated state) ...")
        # Toggle the first risk in the checklist (Capital Costs — has_sched=true)
        page.evaluate("""
        () => {
          const cb = [...document.querySelectorAll('input[type=\"checkbox\"]')]
            .find(c => /Capital Costs/i.test(c.closest('label')?.textContent || ''));
          if (cb) cb.click();
        }
        """)
        page.wait_for_timeout(2800)  # wait for /whatif round-trip

        capture(page, "css:div.card:has(h3:text-is('What-If Sensitivity'))",
                "fig_7_6a_what_if_deactivated.png",
                wait_ms=600, scroll_to=True)

        ctx.close()
        browser.close()
    print("Done.")


if __name__ == "__main__":
    main()
