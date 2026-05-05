"""Re-capture fig_6_1a with both extra scenarios enabled and labelled."""
import os, time
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
FRONTEND = "http://localhost:5173"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        page.goto(f"{FRONTEND}/project/1/simulation", wait_until="networkidle", timeout=30000)
        time.sleep(1.5)
        # Scroll to scenarios panel
        target = page.get_by_text("Inflation Sensitivity Scenarios", exact=False).first
        target.scroll_into_view_if_needed(timeout=4000)
        time.sleep(0.5)
        # Click both extra checkboxes (Scenario 2 and 3) and fill values via DOM
        page.evaluate("""
            () => {
                const all = Array.from(document.querySelectorAll('h1,h2,h3,h4,div,span,p'));
                const heading = all.find(el => /inflation sensitivity scenarios/i.test(el.textContent || ''));
                if (!heading) return false;
                let scope = heading;
                for (let i = 0; i < 6 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && scope.querySelectorAll('input').length >= 6) break;
                }
                if (!scope) return false;
                // Click any unchecked checkboxes (these enable scenarios 2 and 3)
                scope.querySelectorAll('input[type=checkbox]').forEach(cb => {
                    if (!cb.checked && !cb.disabled) cb.click();
                });
            }
        """)
        time.sleep(0.5)
        # Fill deltas and labels now that inputs are enabled
        page.evaluate("""
            () => {
                const all = Array.from(document.querySelectorAll('h1,h2,h3,h4,div,span,p'));
                const heading = all.find(el => /inflation sensitivity scenarios/i.test(el.textContent || ''));
                let scope = heading;
                for (let i = 0; i < 6 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && scope.querySelectorAll('input').length >= 6) break;
                }
                const inputs = Array.from(scope.querySelectorAll('input'));
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                const setVal = (el, v) => {
                    setter.call(el, String(v));
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('blur', { bubbles: true }));
                };
                // Identify number inputs and text inputs in panel order.
                const numbers = inputs.filter(i => i.type === 'number' && !i.disabled);
                const texts   = inputs.filter(i => i.type === 'text' && !i.disabled);
                // We expect 2 enabled number inputs (scenarios 2 and 3 deltas) and 3 label inputs.
                // Set deltas: -3 and +5
                const deltas = [-3, 5];
                numbers.forEach((n, i) => { if (i < deltas.length) setVal(n, deltas[i]); });
                const labels = ['Recession', 'Overheated', 'High Inflation'];
                texts.forEach((t, i) => { if (i < labels.length) setVal(t, labels[i]); });
            }
        """)
        time.sleep(0.7)
        # Resolve clip and screenshot
        bbox = page.get_by_text("Inflation Sensitivity Scenarios", exact=False).first.evaluate("""
            el => {
                let scope = el;
                for (let i = 0; i < 6 && scope; i++) {
                    scope = scope.parentElement;
                    if (scope && scope.querySelectorAll('input').length >= 6) break;
                }
                if (!scope) return null;
                const r = scope.getBoundingClientRect();
                return { x: Math.max(0, r.x-6), y: Math.max(0, r.y-12), width: Math.min(1380, r.width+12), height: Math.min(900, r.height+24) };
            }
        """)
        page.screenshot(path=os.path.join(OUT, "fig_6_1a_inflation_scenarios.png"), clip=bbox)
        print("ok")
        browser.close()

if __name__ == "__main__":
    main()
