import sys
sys.path.insert(0, "scraper")
from scrape_connectnigeria import scrape_category, load_existing_names, CATEGORIES
import time
import random

existing_names = load_existing_names()

# Scrape medium categories (500-5000 businesses)
medium_cats = [
    ("Legal Services", 4185),
    ("Business & Professional Services", 4075),
    ("Oil and Gas", 4027),
    ("Security Services", 4974),
    ("Real Estate", 7168),
    ("Financial Services", 10068),
    ("Religious Services", 10591),
]

all_results = []

for cat_name, cat_count in medium_cats:
    max_pages = min(100, (cat_count // 50) + 2)
    businesses = scrape_category(cat_name, max_pages=max_pages, per_page=50)

    new_count = 0
    for b in businesses:
        name_key = b["name"].lower().strip()
        if name_key not in existing_names:
            existing_names.add(name_key)
            new_count += 1

    all_results.extend(businesses)
    print(f"  New (not in existing): {new_count}")
    time.sleep(random.uniform(2, 4))

print(f"\nTotal scraped: {len(all_results)}")
