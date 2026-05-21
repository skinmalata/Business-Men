import json
import re

def clean_title(text):
    if not text:
        return ""
    text = re.sub(r'Verified ID\s*', '', text)
    text = re.sub(r'\d+\+ YEARS ON JIJI\s*', '', text)
    text = re.sub(r'\d+ YEARS ON JIJI\s*', '', text)
    text = re.sub(r'ENTERPRISE\s*', '', text)
    text = re.sub(r'PREMIUM\s*', '', text)
    text = re.sub(r'DIAMOND\s*', '', text)
    text = re.sub(r'Popular\s*', '', text)
    text = re.sub(r'Quick reply\s*', '', text)
    text = re.sub(r'\u20a6\s*[\d,]+\s*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_price(text):
    if not text:
        return ""
    text = text.split('\n')[0]
    text = text.replace('\u20a6', '').replace(',', '').strip()
    text = re.sub(r'[^\d]', '', text)
    return text

def clean_location(text):
    if not text:
        return ""
    text = re.sub(r'^Promoted\s*', '', text)
    text = re.sub(r',\s*\d+\s*(hour|day|min|week)s?\s*ago.*$', '', text)
    text = re.sub(r'\d+\s*views?\s*$', '', text)
    text = text.strip().rstrip(',')
    return text

with open("data/marketplace_jiji_products.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Before: {len(data)} products")

for p in data:
    p["title"] = clean_title(p.get("title", ""))
    p["price"] = clean_price(p.get("price", ""))
    p["location"] = clean_location(p.get("location", ""))
    # Remove empty fields
    if not p.get("description"):
        p["description"] = ""
    if not p.get("seller_name"):
        p["seller_name"] = ""

# Remove products with empty titles
data = [p for p in data if p.get("title")]

with open("data/marketplace_jiji_products.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"After: {len(data)} products")

# Show clean samples
cats = {}
for p in data:
    cat = p.get("category", "?")
    cats[cat] = cats.get(cat, 0) + 1

print("\nBy category:")
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

print("\nSample products:")
for p in data[:5]:
    print(f"  {p['title'][:50]} | N{p['price']} | {p['location']}")
