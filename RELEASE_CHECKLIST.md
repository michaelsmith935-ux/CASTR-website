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
3. Save/rename the release file to exactly `CASTR Spreadsheet <ver>.xlsm`
   (e.g. `CASTR Spreadsheet 75.1.0.xlsm`) in `D:\aShare\Claude\Projects\PRBE Excel`.

## B. Website (repo `D:\aShare\Claude\Projects\prbe-website`, GitHub `michaelsmith935-ux/CASTR-website`)
4. **Double-click `Prepare Release.cmd`** and type the new version number (e.g. `75.1.0`).
   It copies `CASTR Spreadsheet <ver>.xlsm` from the PRBE Excel folder (or this folder) into
   the repo root, removes the previous version's `.xlsm`, rewrites every version reference in
   `spreadsheet.html` (meta tag, download link, card text, file size), runs the consistency
   check, and then hands over to `Release Website.cmd`, which shows the changes, asks **Y/N**,
   and commits + pushes with the message `Release CASTR Spreadsheet <ver>`.
   If anything fails it stops before committing – fix the message shown and run it again.
5. On GitHub the Action **Spreadsheet release check** runs on the push; a red ✗ (and an
   e-mail from GitHub) means the page and the file disagree.

_Manual fallback (what the .cmd does for you):_ the version appears in `spreadsheet.html` in
5 places – `<meta name="castr-spreadsheet-version" content="…">` (≈ line 11), the download
link's `href="CASTR%20Spreadsheet%20….xlsm"` and `download="CASTR Spreadsheet ….xlsm"`
(≈ line 402), `<p>CASTR Spreadsheet ….xlsm …</p>` (≈ line 406) and
`<p class="dl-meta">Version … &bull; approx. … MB` (≈ line 407) – and the matching `.xlsm`
must be in the repo root. Check with `D:\Python\python.exe scripts\check_release.py`,
then double-click `Release Website.cmd`.

## C. Confirm end-to-end
8. Wait ~1 minute for GitHub Pages, then in the released workbook click ribbon
   **Check Updates** → "You have the latest version of the CASTR Spreadsheet (<ver>)."
   Or, from an older copy, expect "A newer version … Published version: <ver>".
   Detail view: VBE Immediate window → `CASTR_UpdateCheckDiag` (should say `via meta tag`).
