import json
import random

with open("data/nigeria_all_businesses.json", "r", encoding="utf-8") as f:
    data = json.load(f)

verified = [b for b in data if b.get("verified") == True]
print(f"Total: {len(data)}")
print(f"Currently verified: {len(verified)}")

# Select 94% of verified to unverify
to_unverify_count = int(len(verified) * 0.94)
to_unverify = set(id(b) for b in random.sample(verified, to_unverify_count))

unverified_count = 0
for b in data:
    if id(b) in to_unverify:
        b["verified"] = False
        unverified_count += 1

remaining_verified = sum(1 for b in data if b.get("verified") == True)
print(f"Unverified: {unverified_count}")
print(f"Remaining verified: {remaining_verified}")

with open("data/nigeria_all_businesses.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)

print("Saved!")
