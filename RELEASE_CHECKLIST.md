# CASTR Spreadsheet – release checklist

Two sides must agree on the version number: the workbook (`ChangeLog!B6`, named range
`CurrVersion`) and the website (`spreadsheet.html`). The workbook's **Check Updates**
button reads the website; the website's GitHub Action checks itself. This list is
also shown by the workbook's `CASTR_VerifyRelease` macro (runs automatically at the
end of `DoRelease`).

## A. Workbook (Excel)
1. Add the new version row to the **ChangeLog** sheet so `B6` (`CurrVersion`) shows the
   new version, e.g. `74.1.0`. Dotted numbers only – no `-beta`, no letters.
2. Run the release macro (`DoRelease`, Ctrl+Shift+R, or `DoReleaseXlsm`). Its last step,
   `CASTR_VerifyRelease`, compares the workbook version with the website and lists what
   is still missing on the website.
3. Rename the release file to exactly `CASTR Spreadsheet <ver>.xlsm`
   (e.g. `CASTR Spreadsheet 74.1.0.xlsm`).

## B. Website (repo `D:\aShare\Claude\Projects\prbe-website`, GitHub `michaelsmith935-ux/CASTR-website`)
4. Copy `CASTR Spreadsheet <ver>.xlsm` into the repo root. Remove the previous version's
   `.xlsm` (or keep it deliberately – the check only warns).
5. In `spreadsheet.html` change every version reference to `<ver>` (5 places):
   - `<meta name="castr-spreadsheet-version" content="<ver>">`   (≈ line 11 – read first by the workbook)
   - `<a href="CASTR%20Spreadsheet%20<ver>.xlsm" download="CASTR Spreadsheet <ver>.xlsm"`  (≈ line 400)
   - `<p>CASTR Spreadsheet <ver>.xlsm &mdash; …</p>`                       (≈ line 404)
   - `<p class="dl-meta">Version <ver> &bull; approx. <size> MB …</p>`  (≈ line 405; update the size too)
6. **Double-click `Release Website.cmd`** in the repo folder (`D:\aShare\Claude\Projects\prbe-website`).
   It runs `scripts\check_release.py` (must print `OK - spreadsheet.html consistently publishes
   version <ver>.`), shows the files to be committed, asks **Y/N**, then runs
   `git add -A`, `git commit -m "Release CASTR Spreadsheet <ver>"` and `git push origin`.
   If the check fails it stops and nothing is committed – fix steps 4–5 and double-click again.
7. On GitHub the Action **Spreadsheet release check** runs on the push; a red ✗ (and an
   e-mail from GitHub) means step 4 or 5 is still incomplete.

## C. Confirm end-to-end
8. Wait ~1 minute for GitHub Pages, then in the released workbook click ribbon
   **Check Updates** → "You have the latest version of the CASTR Spreadsheet (<ver>)."
   Or, from an older copy, expect "A newer version … Published version: <ver>".
   Detail view: VBE Immediate window → `CASTR_UpdateCheckDiag` (should say `via meta tag`).
