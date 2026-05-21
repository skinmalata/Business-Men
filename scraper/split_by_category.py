import json
import os

with open("data/nigeria_all_businesses.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total records: {len(data)}")

# Group by category
by_cat = {}
for b in data:
    cat = b.get("category", "general")
    if cat not in by_cat:
        by_cat[cat] = []
    by_cat[cat].append(b)

print(f"Categories: {len(by_cat)}")

# Save per-category files
for cat, items in by_cat.items():
    slug = cat.lower().replace(" & ", "-").replace(" ", "_").replace("(", "").replace(")", "")
    output = f"data/cat_{slug}.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)
    size_kb = round(os.path.getsize(output) / 1024, 1)
    print(f"  {cat}: {len(items)} records ({size_kb} KB)")

# Save category index
cat_index = {}
for cat, items in by_cat.items():
    slug = cat.lower().replace(" & ", "-").replace(" ", "_").replace("(", "").replace(")", "")
    cat_index[cat] = {
        "file": f"data/cat_{slug}.json",
        "count": len(items)
    }

with open("data/cat_index.json", "w", encoding="utf-8") as f:
    json.dump(cat_index, f, indent=2, ensure_ascii=False)

print(f"\nSaved cat_index.json with {len(cat_index)} categories")
