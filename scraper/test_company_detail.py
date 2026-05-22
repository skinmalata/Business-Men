import requests
from bs4 import BeautifulSoup

# Test scraping a single company page for full details
url = "https://www.businesslist.com.ng/company/268151/navigator-real-estate-limited"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

resp = requests.get(url, headers=headers, timeout=15)
print(f"Status: {resp.status_code}")

soup = BeautifulSoup(resp.text, "html.parser")

# Extract all text content
print("\n=== Full Company Details ===")

# Name
name_el = soup.select_one("h1, .company_name, .title")
print(f"Name: {name_el.get_text(strip=True) if name_el else 'N/A'}")

# Phone
phone_els = soup.select(".phone, .contact-phone, .tel, a[href^='tel:']")
for p in phone_els:
    print(f"Phone: {p.get_text(strip=True)}")

# Address
addr_el = soup.select_one(".address, .location, .addr")
print(f"Address: {addr_el.get_text(strip=True) if addr_el else 'N/A'}")

# Website
web_el = soup.select_one(".website a, a[href^='http']")
if web_el:
    print(f"Website: {web_el.get('href', 'N/A')}")

# Description
desc_el = soup.select_one(".description, .about, .tagline")
print(f"Description: {desc_el.get_text(strip=True)[:200] if desc_el else 'N/A'}")

# Hours
hours_el = soup.select_one(".hours, .opening_hours")
print(f"Hours: {hours_el.get_text(strip=True) if hours_el else 'N/A'}")

# Save HTML for inspection
with open("test_company_page.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("\nSaved company page HTML to test_company_page.html")
