import requests
import json
import time
import random
import os
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
    retry_strategy = Retry(total=3, backoff_factor=10, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def load_existing_names():
    existing = set()
    data_dir = "data"
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

def get_company_urls(session, category_slug, location_slug, max_pages=30):
    urls = []
    for page in range(1, max_pages + 1):
        url = f"https://www.businesslist.com.ng/category/{category_slug}/{location_slug}"
        if page > 1:
            url += f"/{page}"
        
        try:
            resp = session.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 404:
                break
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("div.company_header h3 a, h3 a[href*='/company/']")
            
            if not links:
                break
            
            page_count = 0
            for link in links:
                href = link.get("href", "")
                if "/company/" in href:
                    full_url = f"https://www.businesslist.com.ng{href}"
                    if full_url not in urls:
                        urls.append(full_url)
                        page_count += 1
            
            print(f"    Page {page}: {page_count} URLs (total: {len(urls)})")
            
            if page_count == 0:
                break
                
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"    Page {page}: Error - {e}")
            break
    
    return urls

def scrape_detail(session, url):
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        name_el = soup.select_one("h1, .company_name, .title")
        name = name_el.get_text(strip=True) if name_el else ""
        if " - " in name:
            name = name.split(" - ")[0].strip()
        
        if not name:
            return None
        
        phone_els = soup.select("a[href^='tel:'], .phone, .contact-phone, .tel")
        phones = []
        for p in phone_els:
            phone = p.get_text(strip=True) or p.get("href", "").replace("tel:", "")
            if phone and phone not in phones:
                phones.append(phone)
        
        addr_el = soup.select_one(".address, .location, .addr")
        address = addr_el.get_text(strip=True) if addr_el else ""
        address = address.replace("View Map", "").replace("Get Directions", "").strip()
        
        desc_el = soup.select_one(".description, .about, .tagline")
        description = desc_el.get_text(strip=True) if desc_el else ""
        
        website = ""
        web_els = soup.select(".website a, a[href^='http']")
        for w in web_els:
            href = w.get("href", "")
            if href and "businesslist.com.ng" not in href and href.startswith("http"):
                website = href
                break
        
        return {
            "name": name,
            "phone": ", ".join(phones),
            "address": address,
            "description": description,
            "url": url,
            "website": website,
            "verified": False
        }
        
    except Exception as e:
        return None

def main():
    existing_names = load_existing_names()
    all_new = []
    
    cities = [
        ("lagos", "Lagos"),
        ("abuja", "Abuja FCT"),
        ("port-harcourt", "Rivers"),
    ]
    
    for city_slug, city_name in cities:
        print(f"\n{'='*60}")
        print(f"City: {city_name} ({city_slug})")
        print(f"{'='*60}")
        
        session = create_session()
        
        urls = get_company_urls(session, "hotels", city_slug, max_pages=30)
        
        if not urls:
            print(f"  No URLs found for {city_name}")
            continue
        
        print(f"\n  Scraping {len(urls)} hotel details...")
        
        city_results = 0
        for i, url in enumerate(urls):
            detail = scrape_detail(session, url)
            if detail:
                detail["city"] = city_name
                detail["category"] = "hotel"
                name_key = detail["name"].lower().strip()
                if name_key not in existing_names:
                    all_new.append(detail)
                    existing_names.add(name_key)
                    city_results += 1
            
            if (i + 1) % 5 == 0:
                print(f"    Progress: {i+1}/{len(urls)}")
            
            time.sleep(random.uniform(2, 4))
        
        print(f"\n  {city_name}: {city_results} new entries")
        
        # Save after each city
        if all_new:
            output = f"data/nigeria_hotels_scraped.json"
            with open(output, "w", encoding="utf-8") as f:
                json.dump(all_new, f, indent=2, ensure_ascii=False)
            print(f"  Saved {len(all_new)} total to {output}")
        
        time.sleep(random.uniform(5, 10))
    
    print(f"\n{'='*60}")
    print(f"TOTAL NEW HOTELS: {len(all_new)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
