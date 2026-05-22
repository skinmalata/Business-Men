import requests
from bs4 import BeautifulSoup

url = "https://www.businesslist.com.ng/category/real-estate/lagos"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

resp = requests.get(url, headers=headers, timeout=15)
print(f"Status: {resp.status_code}")

soup = BeautifulSoup(resp.text, "html.parser")

# Try various selectors
selectors = [
    ".company-item",
    ".listing-item", 
    ".business-item",
    "li.company",
    ".item",
    ".result",
    "div.company",
    "div.listing",
    "a[href*='/company/']",
]

for sel in selectors:
    items = soup.select(sel)
    if items:
        print(f"Selector '{sel}': {len(items)} items")
        for item in items[:2]:
            print(f"  - {item.get_text(strip=True)[:80]}")

# Save HTML for inspection
with open("test_bl.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("\nSaved HTML to test_bl.html for inspection")
