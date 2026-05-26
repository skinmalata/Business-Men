import json
import glob
import os

os.chdir("..")  # Go to project root

# Files to merge (prioritize larger, more complete datasets)
files_to_merge = [
    "data/nigeria_hospitals_federal.json",
    "data/nigeria_hospitals.json",
    "data/nigeria_hotels.json",
    "data/nigeria_realestate.json",
    "data/nigeria_shopping.json",
    "data/nigeria_agriculture.json",
    "data/nigeria_automobile.json",
    "data/nigeria_business.json",
    "data/nigeria_schools.json",
    "data/nigeria_construction.json",
    "data/nigeria_food.json",
    "data/nigeria_oilgas.json",
    "data/nigeria_transportation.json",
    "data/nigeria_realestate_v2.json",
    "data/nigeria_hospitals_v2.json",
    "data/nigeria_automotive_v2.json",
    "data/nigeria_construction_v2.json",
    "data/nigeria_food_v2.json",
    "data/nigeria_energy_v2.json",
    "data/nigeria_businesslist_all.json",
    "data/nigeria_multi_source_new.json",
    "data/nigeria_instagram_businesses.json",
]

all_data = []
categories = {
    "hospital": ["hospital", "clinic", "medical", "health", "doctor", "pharmacy"],
    "hotel": ["hotel", "lodge", "guesthouse", "resort", "inn", "motel"],
    "restaurant": ["restaurant", "food", "cafe", "eatery", "dining", "fast food"],
    "school": ["school", "college", "university", "academy", "institute", "education"],
    "realestate": ["estate", "property", "real estate", "housing", "realtor"],
    "automobile": ["auto", "car", "vehicle", "motor", "garage", "automotive"],
    "construction": ["construction", "building", "contractor", "engineering", "architect"],
    "shopping": ["shop", "store", "market", "mall", "retail", "supermarket"],
    "agriculture": ["farm", "agriculture", "agro", "poultry", "livestock", "crop"],
    "oilgas": ["oil", "gas", "petroleum", "energy", "fuel"],
    "business": ["business", "service", "consulting", "office", "company"],
}

def categorize(item):
    name = item.get("name", "").lower()
    desc = item.get("description", "").lower()
    category = item.get("category", "")
    
    # Use existing category if present
    if category:
        return category
    
    # Try to infer from name/description
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in name or kw in desc:
                return cat
    
    return "general"

print("Loading data files...")
for f in files_to_merge:
    if os.path.exists(f):
        try:
            data = json.load(open(f, encoding="utf-8"))
            if isinstance(data, list):
                all_data.extend(data)
                print(f"  {f}: {len(data)} entries")
            else:
                print(f"  {f}: Not a list, skipping")
        except Exception as e:
            print(f"  {f}: Error - {e}")
    else:
        print(f"  {f}: File not found")

print(f"\nTotal loaded: {len(all_data)} entries")

# Deduplicate by name
print("Deduplicating...")
seen = set()
unique = []
for item in all_data:
    name = item.get("name", "").lower().strip()
    if not name or name in seen:
        continue
    seen.add(name)
    
    # Add category if missing
    if "category" not in item:
        item["category"] = categorize(item)
    
    # Ensure required fields
    item.setdefault("phone", "")
    item.setdefault("address", "")
    item.setdefault("city", "Lagos")
    item.setdefault("description", "")
    item.setdefault("website", "")
    item.setdefault("verified", False)
    
    unique.append(item)

print(f"Unique entries: {len(unique)}")

# Count by category
cat_counts = {}
for item in unique:
    cat = item.get("category", "general")
    cat_counts[cat] = cat_counts.get(cat, 0) + 1

print("\nEntries by category:")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

# Save
output = "data/nigeria_all_businesses.json"
with open(output, "w", encoding="utf-8") as f:
    json.dump(unique, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(unique)} entries to {output}")
