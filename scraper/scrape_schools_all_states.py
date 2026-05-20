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

# Nigerian states and major cities for BusinessList.com.ng
CITIES = {
    "Abia": ["aba", "umuahia"],
    "Adamawa": ["yola"],
    "Akwa Ibom": ["uyo"],
    "Anambra": ["awka", "onitsha"],
    "Bauchi": ["bauchi"],
    "Bayelsa": ["yenagoa"],
    "Benue": ["makurdi"],
    "Borno": ["maiduguri"],
    "Cross River": ["calabar"],
    "Delta": ["asaba", "warri"],
    "Ebonyi": ["abakaliki"],
    "Edo": ["benin-city"],
    "Ekiti": ["ado-ekiti"],
    "Enugu": ["enugu"],
    "Gombe": ["gombe"],
    "Imo": ["owerri"],
    "Jigawa": ["dutse"],
    "Kaduna": ["kaduna", "zaria"],
    "Kano": ["kano"],
    "Katsina": ["katsina"],
    "Kebbi": ["birnin-kebbi"],
    "Kogi": ["lokoja"],
    "Kwara": ["ilorin"],
    "Lagos": ["lagos", "ikeja"],
    "Nasarawa": ["lafia"],
    "Niger": ["minna"],
    "Ogun": ["abeokuta"],
    "Ondo": ["akure"],
    "Osun": ["osogbo"],
    "Oyo": ["ibadan"],
    "Plateau": ["jos"],
    "Rivers": ["port-harcourt"],
    "Sokoto": ["sokoto"],
    "Taraba": ["jalingo"],
    "Yobe": ["damaturu"],
    "Zamfara": ["gusau"],
    "Abuja FCT": ["abuja"],
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

def get_school_urls(session, city_slug, max_pages=25):
    """Get school listing URLs from BusinessList.com.ng for a city."""
    urls = []
    for page in range(1, max_pages + 1):
        url = f"https://www.businesslist.com.ng/category/schools/city:{city_slug}"
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
            
            print(f"      Page {page}: {page_count} URLs (total: {len(urls)})")
            
            if page_count == 0:
                break
                
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"      Page {page}: Error - {e}")
            break
    
    return urls

def scrape_school_detail(session, url, state_name):
    """Scrape school details from BusinessList.com.ng."""
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
            "city": state_name,
            "description": description,
            "url": url,
            "website": website,
            "verified": False,
            "category": "school"
        }
        
    except Exception as e:
        return None

def scrape_finelib_schools(session, city_slug, state_name, existing_names, max_pages=10):
    """Scrape schools from Finelib.com for a city."""
    results = []
    
    for page in range(1, max_pages + 1):
        url = f"https://www.finelib.com/cities/{city_slug}/education"
        if page > 1:
            url += f"/{page}"
        
        try:
            resp = session.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                break
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Find school listings
            listings = soup.select(".listing, .result, .item, [class*='listing'], [class*='result']")
            if not listings:
                # Try alternative selectors
                listings = soup.select("h3 a, h2 a, .title a")
            
            page_results = 0
            for item in listings:
                if isinstance(item, str):
                    continue
                    
                link = item if item.name == 'a' else item.select_one('a')
                if not link:
                    continue
                    
                href = link.get("href", "")
                if not href or "finelib.com" not in href:
                    continue
                
                full_url = href if href.startswith("http") else f"https://www.finelib.com{href}"
                
                # Scrape detail page
                detail = scrape_finelib_detail(session, full_url, state_name)
                if detail:
                    name_key = detail["name"].lower().strip()
                    if name_key not in existing_names:
                        results.append(detail)
                        existing_names.add(name_key)
                        page_results += 1
                
                time.sleep(random.uniform(1, 2))
            
            print(f"      Page {page}: {page_results} new schools (total: {len(results)})")
            
            if page_results == 0 and page > 1:
                break
                
            time.sleep(random.uniform(2, 3))
            
        except Exception as e:
            print(f"      Page {page}: Error - {e}")
            break
    
    return results

def scrape_finelib_detail(session, url, state_name):
    """Scrape school detail from Finelib.com."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Get name
        name_el = soup.select_one("h1, .company_name, .title")
        name = name_el.get_text(strip=True) if name_el else ""
        if not name:
            return None
        
        # Get address
        addr_el = soup.select_one(".address, .location, .addr")
        address = addr_el.get_text(strip=True) if addr_el else ""
        
        # Get phone
        phone_els = soup.select("a[href^='tel:'], .phone, .contact-phone")
        phones = []
        for p in phone_els:
            phone = p.get_text(strip=True) or p.get("href", "").replace("tel:", "")
            if phone and phone not in phones:
                phones.append(phone)
        
        # Get description
        desc_el = soup.select_one(".description, .about, .tagline")
        description = desc_el.get_text(strip=True) if desc_el else ""
        
        # Get website
        website = ""
        web_els = soup.select(".website a, a[href^='http']")
        for w in web_els:
            href = w.get("href", "")
            if href and "finelib.com" not in href and href.startswith("http"):
                website = href
                break
        
        return {
            "name": name,
            "phone": ", ".join(phones),
            "address": address,
            "city": state_name,
            "description": description,
            "url": url,
            "website": website,
            "verified": False,
            "category": "school"
        }
    except:
        return None

def main():
    existing_names = load_existing_names()
    all_new = []
    
    session = create_session()
    
    # Use BusinessList.com.ng - schools category
    print("Scraping schools from BusinessList.com.ng...")
    
    for state, cities in CITIES.items():
        print(f"\n{'='*60}")
        print(f"State: {state}")
        print(f"{'='*60}")
        
        for city_slug in cities:
            print(f"\n  City: {city_slug}")
            
            urls = get_school_urls(session, city_slug, max_pages=20)
            
            if not urls:
                print(f"    No URLs found for {city_slug}")
                continue
            
            print(f"\n    Scraping {len(urls)} school details...")
            
            city_results = 0
            for i, url in enumerate(urls):
                detail = scrape_school_detail(session, url, state)
                if detail:
                    name_key = detail["name"].lower().strip()
                    if name_key not in existing_names:
                        all_new.append(detail)
                        existing_names.add(name_key)
                        city_results += 1
                
                if (i + 1) % 10 == 0:
                    print(f"      Progress: {i+1}/{len(urls)} ({city_results} new)")
                
                time.sleep(random.uniform(2, 4))
            
            print(f"\n    {city_slug}: {city_results} new entries")
            
            # Save checkpoint
            if all_new:
                data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
                output = os.path.join(data_dir, "nigeria_schools_bl.json")
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(all_new, f, indent=2, ensure_ascii=False)
                print(f"    Checkpoint saved: {len(all_new)} total")
            
            time.sleep(random.uniform(3, 5))
    
    print(f"\n{'='*60}")
    print(f"TOTAL NEW SCHOOLS: {len(all_new)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
