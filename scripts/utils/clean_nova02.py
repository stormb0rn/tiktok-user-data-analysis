"""
Clean `/Users/jiajun/tiktok_user_scrape/Nova 02 User List`
Removes blank lines and lines that don't start with http:// or https://
Overwrites the original file safely (writes to a temp file then replaces).
"""
from pathlib import Path
import sys

SRC = Path("/Users/jiajun/tiktok_user_scrape/Nova 02 User List")
if not SRC.exists():
    print(f"Source file not found: {SRC}")
    sys.exit(1)

TMP = SRC.with_suffix(".cleaning.tmp")
count_in = 0
count_out = 0
with SRC.open("r", encoding="utf-8") as rf, TMP.open("w", encoding="utf-8") as wf:
    for line in rf:
        count_in += 1
        s = line.strip()
        if not s:
            continue
        if s.startswith("http://") or s.startswith("https://"):
            wf.write(s + "\n")
            count_out += 1

# Replace original
TMP.replace(SRC)
print(f"Processed {count_in} lines, kept {count_out} URL lines.")
