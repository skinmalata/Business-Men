import requests
import json
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AZURE_MAPS_KEY")
if not API_KEY:
    raise ValueError("Set AZURE_MAPS_KEY in scraper/.env")

OUTPUT = "data/nigeria_hospitals_azure.json"

def search_hospitals(query, offset=0):
    url = "https://atlas.microsoft.com/search/address/json"
    params = {
        "api-version": "1.0",
        "query": query,
        "subscription-key": API_KEY,
        "limit": 50,
        "offset": offset,
        "countrySet": "NG",
        "language": "en"
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

def parse_result(r):
    addr = r.get("address", {})
    return {
        "name": r.get("name", ""),
        "phone": r.get("phone", ""),
        "address": addr.get("freeformAddress", ""),
        "city": addr.get("municipality", "Lagos"),
        "description": r.get("type", ""),
        "latitude": r.get("position", {}).get("lat", ""),
        "longitude": r.get("position", {}).get("lon", ""),
        "url": r.get("url", ""),
        "working_hours": "",
        "products": "",
        "verified": False
    }

def main():
    all_results = []
    offset = 0

    while True:
        print(f"Fetching results at offset {offset}...")
        data = search_hospitals("hospitals lagos", offset)

        results = data.get("results", [])
        if not results:
            print("No more results.")
            break

        for r in results:
            parsed = parse_result(r)
            if parsed["name"]:
                all_results.append(parsed)

        print(f"Got {len(results)} results, total so far: {len(all_results)}")

        if len(results) < 50:
            break

        offset += len(results)
        time.sleep(random.uniform(1.5, 3))

    seen = set()
    unique = []
    for h in all_results:
        key = h["name"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(h)

    print(f"\nDone! Saved {len(unique)} unique hospitals to {OUTPUT}")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
