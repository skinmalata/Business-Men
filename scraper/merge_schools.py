import json

# Load existing consolidated data
with open("data/nigeria_all_businesses.json", "r", encoding="utf-8") as f:
    existing_data = json.load(f)

print(f"Existing businesses: {len(existing_data)}")

# Load new schools data
with open("data/nigeria_schools_bl.json", "r", encoding="utf-8") as f:
    new_schools = json.load(f)

print(f"New schools entries: {len(new_schools)}")

# Get existing school names for dedup
existing_names = set()
for item in existing_data:
    if item.get("category") == "school":
        existing_names.add(item.get("name", "").lower().strip())

print(f"Existing schools: {len(existing_names)}")

# Merge new schools (skip duplicates)
merged_count = 0
for school in new_schools:
    name_key = school.get("name", "").lower().strip()
    if name_key not in existing_names:
        existing_data.append(school)
        existing_names.add(name_key)
        merged_count += 1

print(f"Merged {merged_count} new schools")
print(f"Total businesses after merge: {len(existing_data)}")

# Count schools
total_schools = sum(1 for item in existing_data if item.get("category") == "school")
print(f"Total schools: {total_schools}")

# Count by state
states = {}
for item in existing_data:
    if item.get("category") == "school":
        state = item.get("city", "Unknown")
        states[state] = states.get(state, 0) + 1

print("\nSchools by state:")
for state, count in sorted(states.items(), key=lambda x: -x[1]):
    print(f"  {state}: {count}")

# Save merged data
with open("data/nigeria_all_businesses.json", "w", encoding="utf-8") as f:
    json.dump(existing_data, f, indent=2, ensure_ascii=False)

print("\nSaved merged dataset to data/nigeria_all_businesses.json")
