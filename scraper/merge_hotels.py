import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")

# Load existing hotels data
existing = []
for f in ["data/nigeria_hotels.json", "data/nigeria_hotels_scraped.json"]:
    if os.path.exists(f):
        data = json.load(open(f, encoding="utf-8"))
        existing.extend(data)
        print(f"Loaded {len(data)} from {f}")

# Load all businesses
all_bus = json.load(open("data/nigeria_all_businesses.json", encoding="utf-8"))

# Merge new hotels into all businesses
seen = set(b["name"].lower().strip() for b in all_bus)
new_count = 0
for item in existing:
    name_key = item.get("name", "").lower().strip()
    if name_key and name_key not in seen:
        item.setdefault("category", "hotel")
        all_bus.append(item)
        seen.add(name_key)
        new_count += 1

print(f"\nAdded {new_count} new hotels to consolidated dataset")
print(f"Total businesses: {len(all_bus)}")

# Save
with open("data/nigeria_all_businesses.json", "w", encoding="utf-8") as f:
    json.dump(all_bus, f, indent=2, ensure_ascii=False)

# Count hotels
hotel_count = sum(1 for b in all_bus if b.get("category") == "hotel")
print(f"Total hotels: {hotel_count}")
