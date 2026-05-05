"""Capture v2.2 manual figures from the running CASTR dev server.

Assumes:
  - Backend running on http://localhost:8000
  - Frontend running on http://localhost:5173
  - Sample Highway Project has id=1 with a recent simulation run that
    includes inflation scenarios (run #87 at the time of writing).

Run from the repo root:
    python manual_figures/capture_v2_2.py

Each capture is wrapped in a try/except so a failure on one figure does not
prevent the others from being produced. Captures use the project's existing
1400x1000 viewport convention.
"""
from __future__ import annotations

import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUT = os.path.dirname(os.path.abspath(__file__))
FRONTEND = "http://localhost:5173"

# CSS selectors / heuristics used to locate scrollable targets. These are kept
# loose on purpose — the layout uses a mix of ids, data-* attrs, and visible
# text. If a heuristic fails, we fall back to a full-viewport screenshot.

CLOSE_PANELS_JS = """
(() => {
    const closeBtns = Array.from(document.querySelectorAll('button')).filter(b => {
        const al = (b.getAttribute('aria-label')||'').toLowerCase();
        return al.includes('close') || b.textContent.trim() === '×';
    });
    closeBtns.forEach(b => b.click());
})();
"""


def safe_goto(page, url, *, wait="networkidle", timeout=30000):
    try:
        page.goto(url, wait_until=wait, timeout=timeout)
    except Exception as e:
        print(f"  warn load {url}: {e}")
    time.sleep(1.5)
    page.evaluate(CLOSE_PANELS_JS)
    time.sleep(0.4)


def shot(page, fname, *, locator=None, full_page=False, clip=None):
    out = os.path.join(OUT, fname)
    try:
        if locator is not None:
            locator.screenshot(path=out, timeout=8000)
        elif clip is not None:
            page.screenshot(path=out, clip=clip)
        else:
            page.screenshot(path=out, full_page=full_page)
        print(f"  ok -> {fname}")
    except Exception as e:
        print(f"  ERR {fname}: {e}")


def cap_inflation_scenarios_panel(page):
    """Simulation page — Inflation Sensitivity Scenarios input panel."""
    safe_goto(page, f"{FRONTEND}/project/1/simulation")
    # Type in deltas + labels so the screenshot shows realistic content.
    page.evaluate("""
        () => {
            // Find the scenario delta inputs and labels by their placeholder/aria.
            // Convention: rows are stacked; each row has a number input and a text input.
            const numericInputs = Array.from(document.querySelectorAll('input[type=number]'));
            // Heuristic: scenario inputs usually have step="0.5" or step="0.1".
        }
    """)
    # Try locating the panel by visible heading text.
    try:
        panel = page.get_by_text("Inflation Sensitivity Scenarios", exact=False).first
        panel.scroll_into_view_if_needed(timeout=4000)
        time.sleep(0.5)
    except Exception as e:
        print(f"  warn could not scroll to scenarios panel: {e}")
    # Try to fill three scenarios + labels via DOM walk
    page.evaluate("""
        () => {
            // Find headings then walk forward to inputs.
            const all = Array.from(document.querySelectorAll('h1,h2,h3,h4,div,span,p'));
            const heading = all.find(el => /inflation sensitivity scenarios/i.test(el.textContent || ''));
            if (!heading) return false;
            // Look in the next ancestor card for inputs.
            let scope = heading;
            for (let i = 0; i < 6 && scope; i++) {
                scope = scope.parentElement;
                if (scope && scope.querySelectorAll('input').length >= 4) break;
            }
            if (!scope) return false;
            const inputs = scope.querySelectorAll('input');
            // Pattern: [delta1, label1, delta2, label2, delta3, label3]
            const deltas = [-2, 2, 5];
            const labels = ['Recession', 'Overheated', 'High Inflation'];
            let dIdx = 0, lIdx = 0;
            inputs.forEach(inp => {
                const t = (inp.getAttribute('type')||'').toLowerCase();
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                if (t === 'number' && dIdx < deltas.length) {
                    setter.call(inp, String(deltas[dIdx++]));
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                } else if (t === 'text' && lIdx < labels.length) {
                    setter.call(inp, labels[lIdx++]);
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
            return true;
        }
    """)
    time.sleep(0.7)
    # Now screenshot the section as a clipped region.
    try:
        panel = page.get_by_text("Inflation Sensitivity Scenarios", exact=False).first
        # Climb to nearest "card" wrapper for nicer framing.
        bbox = panel.evaluate("""
            el => {
                let scope = el;
                for (let i = 0; i < 6 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && scope.querySelectorAll('input').length >= 4) break;
                }
                if (!scope) return null;
                const r = scope.getBoundingClientRect();
                return { x: Math.max(0, r.x-6), y: Math.max(0, r.y-30), width: Math.min(1380, r.width+12), height: Math.min(900, r.height+40) };
            }
        """)
        if bbox and bbox.get("width") and bbox.get("height"):
            shot(page, "fig_6_1a_inflation_scenarios.png", clip=bbox)
            return
    except Exception as e:
        print(f"  warn clip resolve: {e}")
    shot(page, "fig_6_1a_inflation_scenarios.png", full_page=False)


def cap_results_scenario_views(page):
    """Results page captures: scenario selector, comparison table, sensitivity curve."""
    safe_goto(page, f"{FRONTEND}/project/1/results")
    time.sleep(1.0)
    # Make sure we're on the Summary tab so the comparison table is visible.
    try:
        tab = page.get_by_role("button", name="Summary").first
        tab.click(timeout=3000)
    except Exception:
        pass
    time.sleep(0.7)

    # Scenario selector — clip to top of page.
    try:
        sel = page.locator("text=/Inflation\\s*Scenario/i").first
        bbox = sel.evaluate("""
            el => {
                // Walk up to find the row of chips.
                let scope = el;
                for (let i = 0; i < 6 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && scope.querySelectorAll('button').length >= 2) break;
                }
                if (!scope) return null;
                const r = scope.getBoundingClientRect();
                return { x: Math.max(0, r.x-6), y: Math.max(0, r.y-6), width: Math.min(1380, r.width+12), height: Math.min(120, r.height+12) };
            }
        """)
        if bbox and bbox.get("width") and bbox.get("height"):
            shot(page, "fig_7_5_scenario_selector.png", clip=bbox)
        else:
            shot(page, "fig_7_5_scenario_selector.png", full_page=False)
    except Exception as e:
        print(f"  warn scenario selector: {e}")
        shot(page, "fig_7_5_scenario_selector.png", full_page=False)

    # Comparison table — find by heading "Inflation Sensitivity"
    try:
        th = page.locator("text=/Inflation Sensitivity/i").first
        th.scroll_into_view_if_needed(timeout=4000)
        time.sleep(0.4)
        bbox = th.evaluate("""
            el => {
                let scope = el;
                for (let i = 0; i < 6 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && (scope.querySelector('table') || scope.classList.contains('card') || scope.querySelectorAll('th').length > 2)) break;
                }
                if (!scope) return null;
                const r = scope.getBoundingClientRect();
                return { x: Math.max(0, r.x-6), y: Math.max(0, r.y-6), width: Math.min(1380, r.width+12), height: Math.min(900, r.height+12) };
            }
        """)
        if bbox and bbox.get("width") and bbox.get("height"):
            shot(page, "fig_7_5a_comparison_table.png", clip=bbox)
        else:
            shot(page, "fig_7_5a_comparison_table.png", full_page=False)
    except Exception as e:
        print(f"  warn comparison table: {e}")

    # Sensitivity curve — try Plotly chart anchored under the comparison table
    try:
        # Looking for a Plotly element near "Sensitivity"
        sc = page.locator("text=/Sensitivity Curve|sensitivity curve/i").first
        sc.scroll_into_view_if_needed(timeout=4000)
        time.sleep(0.4)
        bbox = sc.evaluate("""
            el => {
                let scope = el;
                for (let i = 0; i < 8 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && (scope.querySelector('.js-plotly-plot') || scope.querySelector('svg.main-svg'))) break;
                }
                if (!scope) return null;
                const r = scope.getBoundingClientRect();
                return { x: Math.max(0, r.x-6), y: Math.max(0, r.y-6), width: Math.min(1380, r.width+12), height: Math.min(900, r.height+12) };
            }
        """)
        if bbox and bbox.get("width") and bbox.get("height"):
            shot(page, "fig_7_5b_sensitivity_curve.png", clip=bbox)
        else:
            shot(page, "fig_7_5b_sensitivity_curve.png", full_page=False)
    except Exception as e:
        print(f"  warn sensitivity curve: {e}")


def cap_risk_impact_tornado(page):
    """Results → Tornado tab → Risk Impact toggle."""
    safe_goto(page, f"{FRONTEND}/project/1/results")
    time.sleep(0.6)
    try:
        # Click the Tornado tab.
        tab = page.locator("button:has-text('Tornado'), a:has-text('Tornado')").first
        tab.click(timeout=4000)
        time.sleep(0.8)
    except Exception as e:
        print(f"  warn tornado tab: {e}")
    # Toggle to Risk Impact mode.
    try:
        btn = page.locator("button:has-text('Risk Impact')").first
        btn.click(timeout=3000)
        time.sleep(0.7)
    except Exception as e:
        print(f"  warn risk-impact toggle: {e}")
    shot(page, "fig_7_3a_risk_impact_tornado.png", full_page=False)


def cap_seeded_shield(page):
    """Risk Identification → Triage view, capture P(occur) cell with shield badge."""
    safe_goto(page, f"{FRONTEND}/project/1/risk-id")
    # Click Triage toggle if present
    try:
        page.locator("button:has-text('Triage')").first.click(timeout=3000)
        time.sleep(0.6)
    except Exception:
        pass
    shot(page, "fig_5_1c_seeded_shield.png", full_page=False)


def cap_probability_bands(page):
    """Settings → Scoring Tables → Probability Bands editor."""
    safe_goto(page, f"{FRONTEND}/scoring-tables")
    try:
        target = page.locator("text=/Probability\\s*Bands|Probability Score/i").first
        target.scroll_into_view_if_needed(timeout=4000)
        time.sleep(0.4)
        bbox = target.evaluate("""
            el => {
                let scope = el;
                for (let i = 0; i < 6 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && scope.querySelector('table')) break;
                }
                if (!scope) return null;
                const r = scope.getBoundingClientRect();
                return { x: Math.max(0, r.x-6), y: Math.max(0, r.y-6), width: Math.min(1380, r.width+12), height: Math.min(900, r.height+12) };
            }
        """)
        if bbox and bbox.get("width") and bbox.get("height"):
            shot(page, "fig_11_4_probability_bands.png", clip=bbox)
            return
    except Exception as e:
        print(f"  warn prob bands locator: {e}")
    shot(page, "fig_11_4_probability_bands.png", full_page=False)


def cap_starter_import(page):
    """Starter Library admin page — Excel Import dialog."""
    safe_goto(page, f"{FRONTEND}/starter-library")
    # Click the "Import from Excel" button if present
    try:
        page.locator("button:has-text('Import from Excel'), button:has-text('Import')").first.click(timeout=3000)
        time.sleep(0.6)
    except Exception as e:
        print(f"  warn import button: {e}")
    shot(page, "fig_9_3_starter_import.png", full_page=False)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()

        for fn, label in [
            (cap_inflation_scenarios_panel, "Inflation Scenarios panel"),
            (cap_results_scenario_views,    "Results scenario views"),
            (cap_risk_impact_tornado,       "Risk Impact tornado"),
            (cap_seeded_shield,             "Seeded shield (Triage)"),
            (cap_probability_bands,         "Probability Bands"),
            (cap_starter_import,            "Starter Library import"),
        ]:
            print(f"\n[capture] {label}")
            try:
                fn(page)
            except Exception as e:
                print(f"  FATAL {label}: {e}")
        browser.close()


if __name__ == "__main__":
    main()
