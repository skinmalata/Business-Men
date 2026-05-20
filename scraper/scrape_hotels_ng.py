import requests
import json
import time
import random
import os
import re
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def create_session():
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def load_existing_names():
    existing = set()
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    for filename in os.listdir(data_dir):
        if filename.startswith("nigeria_") and filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        name = item.get("name", "").lower().strip()
                        if name:
                            existing.add(name)
            except:
                pass
    print(f"Loaded {len(existing)} existing names for dedup")
    return existing

def get_hotel_links_from_page(session, url):
    """Extract unique hotel links from a listing page."""
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
                # Extract hotel ID to deduplicate
                match = re.search(r'/hotel/(\d+)-', href)
                if match:
                    hotel_id = match.group(1)
                    if hotel_id not in unique_hotels:
                        full_url = href if href.startswith("http") else f"https://hotels.ng{href}"
                        unique_hotels[hotel_id] = full_url
        
        return list(unique_hotels.values())
    except Exception as e:
        print(f"    Error fetching page {url}: {e}")
        return []

def scrape_hotel_detail(session, url):
    """Extract hotel details from individual hotel page."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Get name from h1
        name_el = soup.select_one("h1")
        name = name_el.get_text(strip=True) if name_el else ""
        if not name:
            return None
        
        # Get location from title
        title = soup.select_one("title")
        title_text = title.get_text(strip=True) if title else ""
        location = ""
        if "|" in title_text:
            parts = title_text.split("|")
            if len(parts) >= 2:
                location_part = parts[1].strip()
                location = location_part.replace("Hotel in", "").replace("Hotels in", "").strip()
        
        # Get phones from tel: links
        tel_links = soup.select('a[href^="tel:"]')
        phones = []
        for link in tel_links:
            phone = link.get("href", "").replace("tel:", "").strip()
            if phone and phone not in phones:
                phones.append(phone)
        
        # Get description from JSON-LD
        description = ""
        address = ""
        json_ld_scripts = soup.select('script[type="application/ld+json"]')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if data.get("@type") == "Hotel":
                    description = data.get("description", "")
                    # Clean HTML tags from description
                    description = re.sub(r'<[^>]+>', '', description).strip()
                    
                    # Try to extract address from description or other fields
                    if "address" in data:
                        addr = data["address"]
                        if isinstance(addr, dict):
                            address = addr.get("streetAddress", "") + " " + addr.get("addressLocality", "") + " " + addr.get("addressRegion", "")
                        elif isinstance(addr, str):
                            address = addr
                    break
            except:
                pass
        
        # Fallback to meta description if no JSON-LD
        if not description:
            meta_desc = soup.select_one('meta[name="description"]')
            description = meta_desc.get("content", "") if meta_desc else ""
        
        # Fallback to OG description
        if not description:
            og_desc = soup.select_one('meta[property="og:description"]')
            description = og_desc.get("content", "") if og_desc else ""
        
        return {
            "name": name,
            "phone": ", ".join(phones),
            "address": address.strip() if address else location,
            "city": location,
            "description": description[:500],  # Limit description length
            "url": url,
            "website": "",
            "verified": False,
            "category": "hotel"
        }
    except Exception as e:
        print(f"    Error scraping {url}: {e}")
        return None

def main():
    existing_names = load_existing_names()
    all_new = []
    
    # Cities to scrape - start with subset for testing
    cities = [
        ("lagos", "Lagos", 50),  # ~3,659 hotels, starting with 50 pages
        # ("abuja", "Abuja FCT", 30),  # Uncomment after Lagos completes
        # ("port-harcourt", "Rivers", 20),  # Uncomment after Abuja completes
    ]
    
    for city_slug, city_name, max_pages in cities:
        print(f"\n{'='*60}")
        print(f"City: {city_name} ({city_slug}) - Max pages: {max_pages}")
        print(f"{'='*60}")
        
        session = create_session()
        all_hotel_urls = []
        
        # Collect hotel URLs from listing pages
        print(f"\n  Collecting hotel URLs from {max_pages} pages...")
        for page in range(1, max_pages + 1):
            if page == 1:
                url = f"https://hotels.ng/hotels-in-{city_slug}"
            else:
                url = f"https://hotels.ng/hotels-in-{city_slug}/{page}"
            
            links = get_hotel_links_from_page(session, url)
            all_hotel_urls.extend(links)
            
            if (page % 10 == 0) or (page == 1):
                print(f"    Page {page}/{max_pages}: {len(links)} hotels (total unique: {len(set(all_hotel_urls))})")
            
            # Rate limiting
            time.sleep(random.uniform(1, 2))
        
        print(f"\n  Total unique hotel URLs collected: {len(set(all_hotel_urls))}")
        
        # Scrape hotel details
        print(f"\n  Scraping hotel details...")
        city_results = 0
        unique_urls = list(set(all_hotel_urls))
        
        for i, url in enumerate(unique_urls):
            detail = scrape_hotel_detail(session, url)
            if detail:
                name_key = detail["name"].lower().strip()
                if name_key not in existing_names:
                    all_new.append(detail)
                    existing_names.add(name_key)
                    city_results += 1
            
            if (i + 1) % 10 == 0:
                print(f"    Progress: {i+1}/{len(unique_urls)} ({city_results} new so far)")
                # Save checkpoint
                if all_new:
                    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
                    output = os.path.join(data_dir, "nigeria_hotels_ng.json")
                    with open(output, "w", encoding="utf-8") as f:
                        json.dump(all_new, f, indent=2, ensure_ascii=False)
                    print(f"    Checkpoint saved: {len(all_new)} total")
            
            # Rate limiting
            time.sleep(random.uniform(1, 3))
        
        print(f"\n  {city_name}: {city_results} new entries")
        
        # Save after each city
        if all_new:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            output = os.path.join(data_dir, "nigeria_hotels_ng.json")
            with open(output, "w", encoding="utf-8") as f:
                json.dump(all_new, f, indent=2, ensure_ascii=False)
            print(f"  Saved {len(all_new)} total to {output}")
        
        time.sleep(random.uniform(3, 5))
    
    print(f"\n{'='*60}")
    print(f"TOTAL NEW HOTELS: {len(all_new)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
