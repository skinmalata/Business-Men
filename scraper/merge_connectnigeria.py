import json
import os
import re

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_phone(phone):
    if not phone:
        return ""
    phone = phone.strip()
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    if phone.startswith('+'):
        phone = phone[1:]
    return phone

# Load existing consolidated data
print("Loading existing data...")
with open("data/nigeria_all_businesses.json", "r", encoding="utf-8") as f:
    existing = json.load(f)
print(f"Existing: {len(existing)} records")

# Build name lookup for dedup
existing_names = {}
for i, b in enumerate(existing):
    name_key = b.get("name", "").lower().strip()
    if name_key and name_key not in existing_names:
        existing_names[name_key] = i

# ConnectNigeria category mapping to website categories
CN_CATEGORY_MAP = {
    "Agriculture": "agriculture",
    "Art": "general",
    "Business & Professional Services": "business",
    "Construction": "construction",
    "Education and Vocation": "schools",
    "Electronics": "general",
    "Entertainment": "general",
    "Fashion and Beauty": "general",
    "Financial Services": "business",
    "Food": "food",
    "Healthcare": "hospitals",
    "Hospitality": "hotels",
    "Information Technology (IT)": "business",
    "Interior Exterior Decoration": "general",
    "Legal Services": "business",
    "Marketing & Advertising": "business",
    "Media": "general",
    "Oil and Gas": "oilgas",
    "Real Estate": "realestate",
    "Religious Services": "general",
    "Research & Development (R&D)": "business",
    "Security Services": "business",
    "Sports": "general",
    "Store": "shopping",
    "Transportation": "transportation",
    "Water Treatment": "general",
    "Web Services": "business",
    "Waste Management": "general",
    "Furniture": "general",
    "Automotive": "automobile",
    "Energy": "oilgas",
    "Manufacturing": "construction",
    "Telecommunications": "general",
}

# Load all ConnectNigeria files
cn_files = [f for f in os.listdir("data") if f.startswith("nigeria_cn_") and f.endswith(".json")]
print(f"\nFound {len(cn_files)} ConnectNigeria files: {cn_files}")

new_count = 0
updated_count = 0

for cn_file in cn_files:
    filepath = os.path.join("data", cn_file)
    print(f"\nProcessing {cn_file}...")
    
    with open(filepath, "r", encoding="utf-8") as f:
        cn_data = json.load(f)
    
    for b in cn_data:
        name_key = b.get("name", "").lower().strip()
        if not name_key:
            continue
        
        # Transform ConnectNigeria record to website format
        record = {
            "name": b.get("name", "").strip(),
            "phone": normalize_phone(b.get("phone", "")),
            "email": b.get("email", "") or "",
            "website": b.get("website", "") or "",
            "address": b.get("address", "") or "",
            "city": b.get("city", "") or "",
            "state": b.get("state", "") or "",
            "description": clean_html(b.get("description", ""))[:500],
            "working_hours": b.get("working_hours", "") or "",
            "products": b.get("products", "") or "",
            "category": CN_CATEGORY_MAP.get(b.get("category", ""), "general"),
            "source_url": b.get("source_url", "") or "",
            "logo": b.get("logo", "") or "",
            "verified": b.get("verified", False),
            "source": "connectnigeria",
        }
        
        # Check if already exists
        if name_key in existing_names:
            idx = existing_names[name_key]
            existing_record = existing[idx]
            # Update if existing record is missing phone/website
            if not existing_record.get("phone") and record["phone"]:
                existing[idx]["phone"] = record["phone"]
                updated_count += 1
            if not existing_record.get("website") and record["website"]:
                existing[idx]["website"] = record["website"]
                updated_count += 1
            if not existing_record.get("working_hours") and record["working_hours"]:
                existing[idx]["working_hours"] = record["working_hours"]
                updated_count += 1
        else:
            existing.append(record)
            existing_names[name_key] = len(existing) - 1
            new_count += 1

print(f"\nResults:")
print(f"  New records added: {new_count}")
print(f"  Existing records updated: {updated_count}")
print(f"  Total records: {len(existing)}")

# Save
print("\nSaving consolidated data...")
with open("data/nigeria_all_businesses.json", "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

print("Done!")
