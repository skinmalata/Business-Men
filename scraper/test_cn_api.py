import requests
import json

BASE_API = "https://api.connectnigeria.com/api/v1/generic/businesses"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# Test 1: All businesses page 1
print("=== Test 1: All businesses ===")
params = {
    "page": 1, "per_page": 5,
    "filter[is_featured]": 0, "filter[name]": "",
    "include": "owner,category,locations,hours",
}
resp = requests.get(BASE_API, headers=HEADERS, params=params, timeout=30)
data = resp.json()
biz_data = data["data"]["businesses"]
print(f"Total: {biz_data['total']}, Pages: {biz_data['last_page']}, Current: {biz_data['current_page']}")
for b in biz_data["data"]:
    locs = b.get("locations", [])
    loc = locs[0] if locs else {}
    print(f"  {b['name']} | {b.get('category',{}).get('name','')} | {loc.get('street_address','')} | {loc.get('state','')} | {loc.get('phone','')}")

# Test 2: Filter by category
print("\n=== Test 2: Agriculture category ===")
params2 = {
    "page": 1, "per_page": 5,
    "filter[is_featured]": 0, "filter[name]": "",
    "filter[category]": "Agriculture",
    "include": "owner,category,locations,hours",
}
resp2 = requests.get(BASE_API, headers=HEADERS, params=params2, timeout=30)
data2 = resp2.json()
if data2.get("success"):
    biz_data2 = data2["data"]["businesses"]
    print(f"Total: {biz_data2['total']}, Pages: {biz_data2['last_page']}")
    for b in biz_data2["data"]:
        locs = b.get("locations", [])
        loc = locs[0] if locs else {}
        print(f"  {b['name']} | {loc.get('street_address','')} | {loc.get('phone','')} | {loc.get('email','')} | {loc.get('website','')}")
else:
    print(f"Failed: {data2}")
    # Try without category filter to see available fields
    print("\nTrying to find category filter name...")
    # Check all fields in response
    b = data["data"]["businesses"]["data"][0]
    print(f"Business keys: {list(b.keys())}")
    print(f"Category: {b.get('category')}")
    print(f"Location keys: {list(locs[0].keys()) if locs else 'none'}")

# Test 3: Try different category filter formats
print("\n=== Test 3: Category filter variations ===")
for fmt in ["Agriculture", "agriculture", "23", "media"]:
    p = {
        "page": 1, "per_page": 2,
        "filter[is_featured]": 0, "filter[name]": "",
        "include": "owner,category,locations,hours",
    }
    # Try different filter keys
    for key in ["filter[category]", "filter[category_id]", "category"]:
        p2 = dict(p)
        p2[key] = fmt
        r = requests.get(BASE_API, headers=HEADERS, params=p2, timeout=15)
        d = r.json()
        if d.get("success"):
            total = d["data"]["businesses"]["total"]
            if total > 0:
                print(f"  {key}={fmt}: {total} results")
