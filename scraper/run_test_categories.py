import sys
sys.path.insert(0, "scraper")
from scrape_connectnigeria import scrape_category

# Test with small categories
for cat in ["Sports", "Web Services", "Art"]:
    businesses = scrape_category(cat, max_pages=5, per_page=50)
    print(f"{cat}: {len(businesses)} businesses scraped")
    if businesses:
        b = businesses[0]
        print(f"  Sample: {b['name']} | {b['phone']} | {b['city']}")
