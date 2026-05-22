import requests
import json
import time

EXISTING_FILE = "data/nigeria_realestate.json"
OUTPUT_FILE = "data/nigeria_realestate_osm.json"

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

def search_overpass(query):
    overpass_query = f"""
    [out:json];
    area["name"="Lagos State"]->.lagos;
    (
      node(area.lagOS)[{query}];
      way(area.lagos)[{query}];
      relation(area.lagos)[{query}];
    );
    out center 500;
    """
    url = "https://overpass-api.de/api/interpreter"
    resp = requests.post(url, data={"data": overpass_query}, timeout=30)
    resp.raise_for_status()
    return resp.json()

def parse_element(elem):
    tags = elem.get("tags", {})
    lat = elem.get("lat", elem.get("center", {}).get("lat", ""))
    lon = elem.get("lon", elem.get("center", {}).get("lon", ""))
    return {
        "name": tags.get("name", ""),
        "phone": tags.get("phone", "") or tags.get("contact:phone", ""),
        "address": tags.get("addr:full", "") or f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(),
        "city": tags.get("addr:city", "Lagos"),
        "description": tags.get("description", "") or tags.get("office", ""),
        "latitude": lat,
        "longitude": lon,
        "url": tags.get("website", "") or tags.get("contact:website", ""),
        "working_hours": tags.get("opening_hours", ""),
        "products": "",
        "verified": False
    }

def main():
    existing_names = load_existing_names()
    new_results = []

    queries = [
        '"office"="real_estate"',
        '"shop"="estate_agent"',
        '"name"~"real estate"',
        '"name"~"property"',
        '"name"~"realty"',
    ]

    for q in queries:
        print(f"\nSearching: {q}")
        try:
            data = search_overpass(q)
        except Exception as e:
            print(f"Error: {e}")
            continue

        elements = data.get("elements", [])
        print(f"Got {len(elements)} elements")

        for elem in elements:
            parsed = parse_element(elem)
            name_key = parsed["name"].lower().strip()

            if not name_key:
                continue
            if name_key in existing_names:
                continue
            if any(n["name"].lower().strip() == name_key for n in new_results):
                continue

            new_results.append(parsed)
            existing_names.add(name_key)

        print(f"New so far: {len(new_results)}")
        time.sleep(2)

    print(f"\nDone! Found {len(new_results)} new real estate companies")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(new_results, f, indent=2, ensure_ascii=False)

    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
