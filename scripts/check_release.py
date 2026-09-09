#!/usr/bin/env python3
"""CASTR website release consistency check.

Run locally:   python scripts/check_release.py   (or double-click "Release Website.cmd")
               python scripts/check_release.py --version   -> prints just the version
Run in CI:     .github/workflows/release-check.yml (every push / pull request)

Fails (exit 1) when spreadsheet.html is internally inconsistent or the
published workbook file is missing. The CASTR Spreadsheet's built-in
"Check Updates" routine (ModWeb.bas, PATCH-UPDGH) reads the version from
this page, so every version reference must agree:

  1. <meta name="castr-spreadsheet-version" content="X.Y.Z">      (read first)
  2. <a href="CASTR%20Spreadsheet%20X.Y.Z.xlsm" download="CASTR Spreadsheet X.Y.Z.xlsm"
  3. <p>CASTR Spreadsheet X.Y.Z.xlsm &mdash; ...</p>
  4. <p class="dl-meta">Version X.Y.Z &bull; ...</p>
  5. A file named exactly "CASTR Spreadsheet X.Y.Z.xlsm" in the repo root.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "spreadsheet.html")
VERSION_RE = r"\d+(?:\.\d+){0,3}"

errors = []
warnings = []


def one(pattern, text, label):
    hits = re.findall(pattern, text, flags=re.I)
    if len(hits) == 0:
        errors.append(f"{label}: not found")
        return None
    if len(set(hits)) > 1:
        errors.append(f"{label}: several different values {sorted(set(hits))}")
        return None
    return hits[0]


def main():
    if not os.path.exists(PAGE):
        print("ERROR: spreadsheet.html not found")
        return 1
    html = open(PAGE, encoding="utf-8").read()

    meta = one(rf'<meta\s+name="castr-spreadsheet-version"\s+content="({VERSION_RE})"', html, "meta tag")
    href = one(rf'href="CASTR%20Spreadsheet%20({VERSION_RE})\.xlsm"', html, "download href")
    dl_attr = one(rf'download="CASTR Spreadsheet ({VERSION_RE})\.xlsm"', html, "download attribute")
    card_file = one(rf'<p>CASTR Spreadsheet ({VERSION_RE})\.xlsm', html, "card file-name text")
    card_ver = one(rf'class="dl-meta">Version ({VERSION_RE})\b', html, "card 'Version' text")

    found = {"meta tag": meta, "download href": href, "download attribute": dl_attr,
             "card file-name text": card_file, "card 'Version' text": card_ver}
    values = {v for v in found.values() if v}
    if len(values) > 1:
        errors.append("version references disagree: " + ", ".join(f"{k}={v}" for k, v in found.items()))

    version = meta or href
    if version:
        fname = f"CASTR Spreadsheet {version}.xlsm"
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            errors.append(f'workbook file "{fname}" is not in the repo root')
        else:
            size = os.path.getsize(path)
            if size < 1_000_000:
                warnings.append(f'"{fname}" is only {size:,} bytes - is it the real workbook?')
        # stale copies of other versions
        for f in os.listdir(ROOT):
            if f.lower().endswith(".xlsm") and f != fname:
                warnings.append(f'old workbook still in repo root: "{f}" (delete it or keep deliberately)')

    print("CASTR website release check")
    for k, v in found.items():
        print(f"  {k:22s} {v or '-'}")
    for w in warnings:
        print("  WARNING:", w)
    for e in errors:
        print("  ERROR:", e)
    if errors:
        print("FAIL - fix spreadsheet.html / upload the workbook, then push again.")
        return 1
    print(f"OK - spreadsheet.html consistently publishes version {version}.")
    return 0


if __name__ == "__main__":
    if "--version" in sys.argv:
        # print only the version from the meta tag (used by "Release Website.cmd")
        try:
            html = open(PAGE, encoding="utf-8").read()
            m = re.search(rf'<meta\s+name="castr-spreadsheet-version"\s+content="({VERSION_RE})"', html, re.I)
            print(m.group(1) if m else "")
            sys.exit(0 if m else 1)
        except OSError:
            sys.exit(1)
    sys.exit(main())
