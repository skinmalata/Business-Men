import requests
from bs4 import BeautifulSoup

url = "https://www.businesslist.com.ng/category/estate-agents/lagos"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")

# Find company items
items = soup.select("li.company, .company-item, .listing-item")
print(f"Found {len(items)} items")

if items:
    item = items[0]
    print(f"\nFirst item HTML structure:")
    print(item.prettify()[:1000])
    
    # Try to extract data
    name_el = item.select_one("h3 a, h2 a, .title a, a.title, h4 a")
    print(f"\nName: {name_el.get_text(strip=True) if name_el else 'Not found'}")
    
    phone_el = item.select_one(".phone, .contact-phone, .tel, [class*='phone']")
    print(f"Phone: {phone_el.get_text(strip=True) if phone_el else 'Not found'}")
    
    addr_el = item.select_one(".address, .location, .addr, [class*='address']")
    print(f"Address: {addr_el.get_text(strip=True) if addr_el else 'Not found'}")
    
    desc_el = item.select_one(".description, .desc, .summary, [class*='desc']")
    print(f"Description: {desc_el.get_text(strip=True) if desc_el else 'Not found'}")
