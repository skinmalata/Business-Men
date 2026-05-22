import json
import os

os.chdir("..")  # Go to project root

with open("data/nigeria_all_businesses.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total entries: {len(data)}")

cats = {}
for b in data:
    cat = b.get("category", "general")
    cats[cat] = cats.get(cat, 0) + 1

print("\nCategories:")
for k, v in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
