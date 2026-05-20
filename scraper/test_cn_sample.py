import requests
import json
import re

BASE_API = "https://api.connectnigeria.com/api/v1/generic/businesses"
HEADERS = {"User-Agent": "Mozilla/5.0"}

params = {
    "page": 1, "per_page": 3,
    "filter[is_featured]": 0, "filter[name]": "",
    "filter[category_name]": "Sports",
    "include": "owner,category,locations,hours",
}
r = requests.get(BASE_API, headers=HEADERS, params=params, timeout=15)
d = r.json()

for b in d["data"]["businesses"]["data"]:
    locs = b.get("locations", [])
    loc = locs[0] if locs else {}
    phones = []
    if loc.get("phone_1"):
        phones.append(loc["phone_1"])
    if loc.get("phone_2"):
        phones.append(loc["phone_2"])
    hours = b.get("hours", [])
    hours_str = "; ".join([f"{h.get('day_id')}: {h.get('open_time','')[:5]}-{h.get('close_time','')[:5]}" for h in hours[:3]])
    profile = re.sub(r"<[^>]+>", "", b.get("profile", "") or "")[:100]
    print(f"Name: {b['name']}")
    print(f"  Phone: {', '.join(phones)}")
    print(f"  Address: {loc.get('full_address', '')}")
    print(f"  City: {loc.get('city', {}).get('name', '')}")
    print(f"  Website: {loc.get('website_url', '')}")
    print(f"  Hours: {hours_str}")
    print(f"  Profile: {profile}")
    print(f"  Category: {b.get('category', {}).get('name', '')}")
    print()

print(f"Total in Sports: {d['data']['businesses']['total']}")
