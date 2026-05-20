import json

# Load existing consolidated data
with open("data/nigeria_all_businesses.json", "r", encoding="utf-8") as f:
    existing_data = json.load(f)

print(f"Existing businesses: {len(existing_data)}")

# Load new Hotels.ng data
with open("data/nigeria_hotels_ng.json", "r", encoding="utf-8") as f:
    new_hotels = json.load(f)

print(f"New Hotels.ng entries: {len(new_hotels)}")

# Get existing hotel names for dedup
existing_names = set()
for item in existing_data:
    if item.get("category") == "hotel":
        existing_names.add(item.get("name", "").lower().strip())

print(f"Existing hotels: {len(existing_names)}")

# Merge new hotels (skip duplicates)
merged_count = 0
for hotel in new_hotels:
    name_key = hotel.get("name", "").lower().strip()
    if name_key not in existing_names:
        existing_data.append(hotel)
        existing_names.add(name_key)
        merged_count += 1

print(f"Merged {merged_count} new hotels")
print(f"Total businesses after merge: {len(existing_data)}")

# Count hotels
total_hotels = sum(1 for item in existing_data if item.get("category") == "hotel")
print(f"Total hotels: {total_hotels}")

# Save merged data
with open("data/nigeria_all_businesses.json", "w", encoding="utf-8") as f:
    json.dump(existing_data, f, indent=2, ensure_ascii=False)

print("Saved merged dataset to data/nigeria_all_businesses.json")
