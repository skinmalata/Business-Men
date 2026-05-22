import json
import glob
import os

os.chdir("..")  # Go to project root

all_data = []
for f in glob.glob("data/nigeria_businesslist_*.json"):
    if "all" not in f:
        data = json.load(open(f, encoding="utf-8"))
        all_data.extend(data)

# Deduplicate
seen = set()
unique = []
for d in all_data:
    key = d["name"].lower().strip()
    if key not in seen:
        seen.add(key)
        unique.append(d)

with open("data/nigeria_businesslist_all.json", "w", encoding="utf-8") as f:
    json.dump(unique, f, indent=2, ensure_ascii=False)

print(f"Merged {len(unique)} unique entries")
