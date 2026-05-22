import requests
import json
import time
import random
import os
from dotenv import load_dotenv

load_dotenv("scraper/.env")

API_KEY = os.getenv("AZURE_MAPS_KEY")
if not API_KEY:
    raise ValueError("Set AZURE_MAPS_KEY in scraper/.env")

EXISTING_FILE = "data/nigeria_realestate.json"
OUTPUT_FILE = "data/nigeria_realestate_azure.json"

LAGOS_BOUNDS = "3.0,6.2,4.0,6.8"

def load_existing_names():
    try:
        with open(EXISTING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        names = set()
        for d in data:
            city = d.get("city") or ""
            if "lagos" in city.lower():
                names.add(d["name"].lower().strip())
        print(f"Loaded {len(names)} existing Lagos real estate names for dedup")
        return names
    except FileNotFoundError:
        return set()

def search_real_estate(query, offset=0):
    url = "https://atlas.microsoft.com/search/address/json"
    params = {
        "api-version": "1.0",
        "query": query,
        "subscription-key": API_KEY,
        "limit": 50,
        "offset": offset,
        "countrySet": "NG",
        "language": "en",
        "view": "Unified",
        "lat": 6.5244,
        "lon": 3.3792,
        "radius": 50000,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

def parse_result(r):
    addr = r.get("address", {})
    city = addr.get("municipalitySubdivision") or addr.get("municipality") or "Lagos"
    return {
        "name": r.get("name", ""),
        "phone": r.get("phone", ""),
        "address": addr.get("freeformAddress", ""),
        "city": city,
        "description": r.get("poi", {}).get("categories", [""])[0] if r.get("poi", {}).get("categories") else r.get("type", ""),
        "latitude": r.get("position", {}).get("lat", ""),
        "longitude": r.get("position", {}).get("lon", ""),
        "url": r.get("poi", {}).get("url", "") or r.get("url", ""),
        "working_hours": "",
        "products": "",
        "verified": False
    }

def main():
    existing_names = load_existing_names()
    new_results = []
    total_new = 0
    target = 500

    queries = [
        "real estate lagos",
        "real estate agency lagos",
        "property company lagos",
        "real estate developer lagos",
        "property management lagos",
        "estate agent lagos",
        "realty lagos",
    ]

    for query in queries:
        if total_new >= target:
            print(f"\nReached target of {target} new entries. Stopping.")
            break

        print(f"\n--- Searching: '{query}' ---")
        offset = 0

        while True:
            if total_new >= target:
                break

            try:
                data = search_real_estate(query, offset)
            except Exception as e:
                print(f"Error: {e}")
                break

            results = data.get("results", [])
            if not results:
                break

            batch_added = 0
            for r in results:
                addr = r.get("address", {})
                country = addr.get("countryCode", "")
                if country != "NG":
                    continue

                parsed = parse_result(r)
                name_key = parsed["name"].lower().strip()

                if not name_key:
                    continue
                if name_key in existing_names:
                    continue
                if any(n["name"].lower().strip() == name_key for n in new_results):
                    continue

                new_results.append(parsed)
                existing_names.add(name_key)
                batch_added += 1
                total_new += 1

            print(f"  Offset {offset}: {len(results)} results, {batch_added} new (total: {total_new})")

            if len(results) < 50:
                break

            offset += len(results)
            time.sleep(random.uniform(1, 2))

        time.sleep(random.uniform(1, 2))

    print(f"\nDone! Found {len(new_results)} new real estate companies in Lagos")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(new_results, f, indent=2, ensure_ascii=False)

    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
