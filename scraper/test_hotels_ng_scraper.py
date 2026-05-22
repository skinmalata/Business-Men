import requests
import json
import time
import random
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def get_hotel_links_from_page(session, url):
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, "html.parser")
        hotel_links = soup.select('a[href*="/hotel/"]')
        
        unique_hotels = {}
        for link in hotel_links:
            href = link.get("href", "")
            if "/hotel/" in href:
                match = re.search(r'/hotel/(\d+)-', href)
                if match:
                    hotel_id = match.group(1)
                    if hotel_id not in unique_hotels:
                        full_url = href if href.startswith("http") else f"https://hotels.ng{href}"
                        unique_hotels[hotel_id] = full_url
        
        return list(unique_hotels.values())
    except Exception as e:
        print(f"    Error: {e}")
        return []

def scrape_hotel_detail(session, url):
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        name_el = soup.select_one("h1")
        name = name_el.get_text(strip=True) if name_el else ""
        if not name:
            return None
        
        title = soup.select_one("title")
        title_text = title.get_text(strip=True) if title else ""
        location = ""
        if "|" in title_text:
            parts = title_text.split("|")
            if len(parts) >= 2:
                location_part = parts[1].strip()
                location = location_part.replace("Hotel in", "").replace("Hotels in", "").strip()
        
        tel_links = soup.select('a[href^="tel:"]')
        phones = []
        for link in tel_links:
            phone = link.get("href", "").replace("tel:", "").strip()
            if phone and phone not in phones:
                phones.append(phone)
        
        description = ""
        address = ""
        json_ld_scripts = soup.select('script[type="application/ld+json"]')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if data.get("@type") == "Hotel":
                    description = data.get("description", "")
                    description = re.sub(r'<[^>]+>', '', description).strip()
                    if "address" in data:
                        addr = data["address"]
                        if isinstance(addr, dict):
                            address = addr.get("streetAddress", "") + " " + addr.get("addressLocality", "") + " " + addr.get("addressRegion", "")
                        elif isinstance(addr, str):
                            address = addr
                    break
            except:
                pass
        
        if not description:
            meta_desc = soup.select_one('meta[name="description"]')
            description = meta_desc.get("content", "") if meta_desc else ""
        
        return {
            "name": name,
            "phone": ", ".join(phones),
            "address": address.strip() if address else location,
            "city": location,
            "description": description[:500],
            "url": url,
            "website": "",
            "verified": False,
            "category": "hotel"
        }
    except Exception as e:
        print(f"    Error: {e}")
        return None

# Test with first 3 pages of Lagos
session = requests.Session()
all_urls = []

print("Collecting URLs from first 3 pages...")
for page in range(1, 4):
    if page == 1:
        url = "https://hotels.ng/hotels-in-lagos"
    else:
        url = f"https://hotels.ng/hotels-in-lagos/{page}"
    
    links = get_hotel_links_from_page(session, url)
    all_urls.extend(links)
    print(f"  Page {page}: {len(links)} hotels")
    time.sleep(1)

unique_urls = list(set(all_urls))
print(f"\nTotal unique URLs: {len(unique_urls)}")

# Scrape first 5 hotels
print("\nScraping first 5 hotels...")
hotels = []
for i, url in enumerate(unique_urls[:5]):
    print(f"  Scraping {i+1}/5: {url}")
    detail = scrape_hotel_detail(session, url)
    if detail:
        hotels.append(detail)
        print(f"    Name: {detail['name']}")
        print(f"    City: {detail['city']}")
        print(f"    Phone: {detail['phone']}")
        print(f"    Address: {detail['address'][:80]}")
        print()
    time.sleep(1)

print(f"\nSuccessfully scraped {len(hotels)} hotels")
print("\nSample hotel:")
if hotels:
    print(json.dumps(hotels[0], indent=2, ensure_ascii=False))
