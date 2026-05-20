import sys
sys.path.insert(0, "scraper")
from scrape_connectnigeria import scrape_category, load_existing_names
import time
import random
import json
import os

existing_names = load_existing_names()

# Scrape key categories one at a time with incremental saves
key_cats = [
    ("Financial Services", 10068, 100),
    ("Real Estate", 7168, 100),
    ("Oil and Gas", 4027, 80),
    ("Religious Services", 10591, 100),
]

all_results = []

for cat_name, cat_count, max_pages in key_cats:
    businesses = scrape_category(cat_name, max_pages=max_pages, per_page=50)

    # Dedup and add
    for b in businesses:
        name_key = b["name"].lower().strip()
        if name_key not in existing_names:
            existing_names.add(name_key)
            all_results.append(b)

    # Save cumulative after each category
    output = "data/nigeria_connectnigeria_all.json"
    existing_all = []
    if os.path.exists(output):
        try:
            with open(output, "r", encoding="utf-8") as f:
                existing_all = json.load(f)
        except:
            pass

    all_results = existing_all + all_results
    # Dedup the combined list
    seen = set()
    deduped = []
    for b in all_results:
        k = b["name"].lower().strip()
        if k not in seen:
            seen.add(k)
            deduped.append(b)
    all_results = deduped

    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nCumulative total: {len(all_results)} unique businesses")
    time.sleep(random.uniform(2, 4))

print(f"\nFinal: {len(all_results)} businesses")
