#!/usr/bin/env python3
"""Set the CASTR Spreadsheet version on spreadsheet.html and stage the workbook file.

Usage:  python scripts/set_version.py 75.1.0 ["D:\\path\\to\\CASTR Spreadsheet 75.1.0.xlsm"]

  - Copies the workbook into the repo root as "CASTR Spreadsheet <ver>.xlsm"
    (if no path is given, looks in the repo root, then in
     D:\\aShare\\Claude\\Projects\\PRBE Excel).
  - Deletes other "CASTR Spreadsheet *.xlsm" files in the repo root.
  - Rewrites every version reference in spreadsheet.html (meta tag, download
    href + download attribute, card file name, card "Version" line) and the
    "approx. N.N MB" size text.
Used by "Prepare Release.cmd"; run scripts/check_release.py afterwards.
"""
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "spreadsheet.html")
SOURCE_DIRS = [ROOT, r"D:\aShare\Claude\Projects\PRBE Excel"]
VERSION_RE = r"\d+(?:\.\d+){0,3}"


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        fail("usage: set_version.py <version> [path-to-xlsm]")
    ver = sys.argv[1].strip()
    if not re.fullmatch(VERSION_RE, ver):
        fail(f'"{ver}" is not a dotted numeric version like 75.1.0')

    fname = f"CASTR Spreadsheet {ver}.xlsm"
    dest = os.path.join(ROOT, fname)

    # --- locate the workbook -------------------------------------------------
    src = sys.argv[2] if len(sys.argv) > 2 else None
    if not src:
        for d in SOURCE_DIRS:
            cand = os.path.join(d, fname)
            if os.path.exists(cand):
                src = cand
                break
    if not src or not os.path.exists(src):
        fail(f'could not find "{fname}" in the repo folder or the PRBE Excel folder. '
             f"Save the release as that exact name, or pass its full path as the 2nd argument.")
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy2(src, dest)
        print(f"copied  {src}\n    ->  {dest}")
    else:
        print(f"using   {dest}")
    size = os.path.getsize(dest)
    if size < 1_000_000:
        fail(f'"{fname}" is only {size:,} bytes - not a real workbook')

    # --- remove other workbook versions -------------------------------------
    for f in os.listdir(ROOT):
        if re.fullmatch(r"CASTR Spreadsheet .*\.xlsm", f, re.I) and f != fname:
            os.remove(os.path.join(ROOT, f))
            print(f"removed {f}")

    # --- rewrite spreadsheet.html -------------------------------------------
    html = open(PAGE, encoding="utf-8").read()
    subs = [
        (rf'(<meta\s+name="castr-spreadsheet-version"\s+content=")({VERSION_RE})(")', "meta tag"),
        (rf'(href="CASTR%20Spreadsheet%20)({VERSION_RE})(\.xlsm")', "download href"),
        (rf'(download="CASTR Spreadsheet )({VERSION_RE})(\.xlsm")', "download attribute"),
        (rf'(<p>CASTR Spreadsheet )({VERSION_RE})(\.xlsm)', "card file-name text"),
        (rf'(class="dl-meta">Version )({VERSION_RE})(\b)', "card 'Version' text"),
    ]
    for pat, label in subs:
        html, n = re.subn(pat, lambda m: m.group(1) + ver + m.group(3), html, flags=re.I)
        if n != 1:
            fail(f"{label}: expected exactly 1 match in spreadsheet.html, found {n} - page layout changed")
        print(f"set     {label:22s} -> {ver}")
    mb = f"{size / 1_000_000:.1f}"
    html, n = re.subn(r"(approx\. )\d+(?:\.\d+)?( MB)", lambda m: m.group(1) + mb + m.group(2), html)
    print(f"set     {'file size':22s} -> approx. {mb} MB" if n == 1 else "WARNING: size text not updated")
    open(PAGE, "w", encoding="utf-8", newline="").write(html)
    print(f"OK - spreadsheet.html now publishes {ver}")


if __name__ == "__main__":
    main()
