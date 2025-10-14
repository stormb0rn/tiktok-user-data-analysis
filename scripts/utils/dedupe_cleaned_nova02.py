"""
Deduplicate `/Users/jiajun/tiktok_user_scrape/Nova 02 User List - Cleaned`.
- Creates a timestamped backup of the original cleaned file.
- Writes deduplicated output to `... - Cleaned.deduped` (preserves order) and
  also replaces the original file with the deduped content (keeping the backup).
"""
from pathlib import Path
from datetime import datetime

SRC = Path("/Users/jiajun/tiktok_user_scrape/Nova 02 User List - Cleaned")
if not SRC.exists():
    print(f"Source not found: {SRC}")
    raise SystemExit(1)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = SRC.with_name(SRC.name + f".{stamp}.bak")
DEDUPED = SRC.with_suffix('.deduped')

# Read lines
with SRC.open('r', encoding='utf-8') as f:
    lines = [l.rstrip('\n') for l in f]

seen = set()
deduped = []
for l in lines:
    if not l:
        continue
    if l in seen:
        continue
    seen.add(l)
    deduped.append(l)

# Backup original
SRC.replace(BACKUP)
print(f"Backed up original to: {BACKUP}")

# Write deduped file and also write back to SRC path
with DEDUPED.open('w', encoding='utf-8') as f:
    for l in deduped:
        f.write(l + '\n')

with SRC.open('w', encoding='utf-8') as f:
    for l in deduped:
        f.write(l + '\n')

print(f"Wrote {len(deduped)} unique lines to: {DEDUPED} and replaced original.")
