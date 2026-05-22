import json

data = json.load(open("../data/nigeria_businesslist_all.json"))
print(f"Total: {len(data)}")
print("\nSample entries:")
for d in data[:10]:
    phone = d.get("phone", "No phone")[:30] if d.get("phone") else "No phone"
    print(f"  {d['name']} | {d['city']} | {phone}")
