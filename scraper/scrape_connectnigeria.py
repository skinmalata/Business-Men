import requests
import json
import time
import os
import random
import re
from datetime import datetime

BASE_API = "https://api.connectnigeria.com/api/v1/generic/businesses"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# Categories sorted by size (only those with 100+ businesses)
CATEGORIES = [
    ("Fashion and Beauty", 99534),
    ("Electronics", 46247),
    ("Education and Vocation", 38869),
    ("Entertainment", 32079),
    ("Media", 20633),
    ("Food", 19110),
    ("Transportation", 14176),
    ("Agriculture", 13293),
    ("Hospitality", 12297),
    ("Religious Services", 10591),
    ("Financial Services", 10068),
    ("Store", 36261),
    ("Construction", 64175),
    ("Healthcare", 22645),
    ("Real Estate", 7168),
    ("Oil and Gas", 4027),
    ("Legal Services", 4185),
    ("Business & Professional Services", 4075),
    ("Security Services", 4974),
    ("Art", 5582),
    ("Interior Exterior Decoration", 2975),
    ("Information Technology (IT)", 37),
    ("Web Services", 90),
    ("Sports", 952),
]

DAY_MAP = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_existing_names():
    existing = set()
    data_dir = "data"
    if not os.path.exists(data_dir):
        return existing
    for filename in os.listdir(data_dir):
        if filename.startswith("nigeria_") and filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        name = item.get("name", "").lower().strip()
                        if name:
                            existing.add(name)
            except:
                pass
    print(f"Loaded {len(existing)} existing names for dedup")
    return existing


def transform_business(b):
    locations = b.get("locations", [])
    primary_loc = locations[0] if locations else {}
    city_obj = primary_loc.get("city", {}) or {}
    lg_obj = primary_loc.get("local_government", {}) or {}

    hours = b.get("hours", [])
    hours_str = ""
    if hours:
        parts = []
        for h in hours:
            day = DAY_MAP.get(h.get("day_id", ""), "")
            open_t = h.get("open_time", "")[:5] if h.get("open_time") else ""
            close_t = h.get("close_time", "")[:5] if h.get("close_time") else ""
            if day and open_t and close_t:
                parts.append(f"{day}: {open_t}-{close_t}")
        hours_str = "; ".join(parts)

    phones = []
    if primary_loc.get("phone_1"):
        phones.append(primary_loc["phone_1"])
    if primary_loc.get("phone_2") and primary_loc["phone_2"] != primary_loc.get("phone_1"):
        phones.append(primary_loc["phone_2"])

    return {
        "name": b.get("name", "").strip(),
        "phone": ", ".join(phones),
        "email": "",
        "website": primary_loc.get("website_url", "") or "",
        "address": primary_loc.get("full_address", "") or primary_loc.get("street_address", "") or "",
        "city": city_obj.get("name", "") or "",
        "state": lg_obj.get("name", "") or "",
        "description": clean_html(b.get("profile", ""))[:500],
        "working_hours": hours_str,
        "products": "",
        "category": b.get("category", {}).get("name", ""),
        "source_url": f"https://www.connectnigeria.com/businesses/{b.get('slug', '')}",
        "logo": b.get("logo", "") or "",
        "verified": b.get("claim_request_status") == "approved",
        "reviews_count": b.get("reviews_count", 0),
        "likes_count": b.get("likes_count", 0),
    }


def scrape_category(category_name, max_pages=None, per_page=50, start_page=1):
    slug = category_name.lower().replace(" & ", "-").replace(" ", "_").replace("(", "").replace(")", "")
    print(f"\n{'='*60}")
    print(f"Category: {category_name}")
    print(f"{'='*60}")

    all_businesses = []
    page = start_page
    session = requests.Session()

    while True:
        params = {
            "page": page,
            "per_page": per_page,
            "filter[is_featured]": 0,
            "filter[name]": "",
            "filter[category_name]": category_name,
            "include": "owner,category,locations,hours",
        }

        try:
            resp = session.get(BASE_API, headers=HEADERS, params=params, timeout=30)
            if resp.status_code != 200:
                print(f"  Page {page}: HTTP {resp.status_code}, retrying...")
                time.sleep(5)
                continue

            data = resp.json()
            if not data.get("success"):
                print(f"  Page {page}: API error")
                break

            biz_data = data["data"]["businesses"]
            businesses = biz_data.get("data", [])
            total_pages = biz_data.get("last_page", 1)
            total_count = biz_data.get("total", 0)

            if page == start_page:
                effective_max = min(max_pages, total_pages) if max_pages else total_pages
                print(f"  Total: {total_count} businesses, {total_pages} pages, scraping up to page {effective_max}")

            if not businesses:
                break

            for b in businesses:
                transformed = transform_business(b)
                if transformed["name"]:
                    all_businesses.append(transformed)

            if page >= (min(max_pages, total_pages) if max_pages else total_pages):
                break

            print(f"  Page {page}: {len(businesses)} businesses (total: {len(all_businesses)})")
            page += 1

            # Save checkpoint every 10 pages
            if page % 10 == 0:
                cp = {"category": category_name, "page": page, "count": len(all_businesses)}
                with open(f"scraper/cn_checkpoint_{slug}.json", "w") as f:
                    json.dump(cp, f)

            time.sleep(random.uniform(1.0, 2.0))

        except requests.exceptions.RequestException as e:
            print(f"  Page {page}: Error - {e}, retrying in 10s...")
            time.sleep(10)
            continue

    print(f"  DONE: {len(all_businesses)} businesses")

    # Save category file
    if all_businesses:
        output = f"data/nigeria_cn_{slug}.json"
        with open(output, "w", encoding="utf-8") as f:
            json.dump(all_businesses, f, indent=2, ensure_ascii=False)
        print(f"  Saved to {output}")

    # Clean checkpoint
    cp_file = f"scraper/cn_checkpoint_{slug}.json"
    if os.path.exists(cp_file):
        os.remove(cp_file)

    return all_businesses


def main():
    existing_names = load_existing_names()

    # Check which categories have checkpoints
    checkpoints = {}
    for cat_name, _ in CATEGORIES:
        slug = cat_name.lower().replace(" & ", "-").replace(" ", "_").replace("(", "").replace(")", "")
        cp_file = f"scraper/cn_checkpoint_{slug}.json"
        if os.path.exists(cp_file):
            try:
                with open(cp_file, "r") as f:
                    cp = json.load(f)
                    checkpoints[cat_name] = cp
                    print(f"Checkpoint found: {cat_name} at page {cp['page']}")
            except:
                pass

    all_results = []

    for cat_name, cat_count in CATEGORIES:
        # Skip tiny categories
        if cat_count < 50:
            print(f"\nSkipping {cat_name} ({cat_count} businesses - too small)")
            continue

        # Check if we already have data for this category
        slug = cat_name.lower().replace(" & ", "-").replace(" ", "_").replace("(", "").replace(")", "")
        existing_file = f"data/nigeria_cn_{slug}.json"
        if os.path.exists(existing_file):
            try:
                with open(existing_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    print(f"\nSkipping {cat_name} - already have {len(existing_data)} businesses")
                    all_results.extend(existing_data)
                    continue
            except:
                pass

        # Determine max pages (limit to reasonable amount)
        # 50 per page, max 200 pages = 10,000 businesses per category
        max_pages = min(200, (cat_count // 50) + 2)

        start_page = 1
        if cat_name in checkpoints:
            start_page = checkpoints[cat_name].get("page", 1)

        businesses = scrape_category(cat_name, max_pages=max_pages, per_page=50, start_page=start_page)

        # Dedup
        new_count = 0
        for b in businesses:
            name_key = b["name"].lower().strip()
            if name_key not in existing_names:
                existing_names.add(name_key)
                new_count += 1

        all_results.extend(businesses)
        print(f"  New (not in existing data): {new_count}")

        time.sleep(random.uniform(2, 4))

    # Final merge
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(all_results)} businesses from ConnectNigeria")
    print(f"{'='*60}")

    output = "data/nigeria_connectnigeria_all.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"Saved all to {output}")


if __name__ == "__main__":
    main()
