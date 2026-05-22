import requests
import json
import time
import random
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv("scraper/.env")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def load_existing_names():
    """Load all existing business names for deduplication"""
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

def scrape_businesslist(category_slug, location_slug="lagos", existing_names=None, max_pages=50):
    """Scrape from BusinessList.com.ng"""
    print(f"\n=== BusinessList.com.ng: {category_slug} in {location_slug} ===")
    results = []
    existing_names = existing_names or set()
    
    for page in range(1, max_pages + 1):
        url = f"https://www.businesslist.com.ng/category/{category_slug}/{location_slug}"
        if page > 1:
            url += f"/{page}"
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 404:
                print(f"  Page {page}: No more pages (404)")
                break
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            companies = soup.select("div.company, li.company")
            
            if not companies:
                print(f"  Page {page}: No companies found")
                break
            
            page_count = 0
            for company in companies:
                name_el = company.select_one("div.company_header h3 a, h3 a, h2 a")
                name = name_el.get_text(strip=True) if name_el else ""
                # Remove numbering like "1 | "
                if " | " in name:
                    name = name.split(" | ", 1)[1].strip()
                
                if not name or name.lower().strip() in existing_names:
                    continue
                
                addr_el = company.select_one("div.address")
                address = addr_el.get_text(strip=True) if addr_el else ""
                
                tagline_el = company.select_one("div.tagline")
                description = tagline_el.get_text(strip=True) if tagline_el else ""
                
                phone_el = company.select_one("div.phone, .contact-phone, .tel")
                phone = phone_el.get_text(strip=True) if phone_el else ""
                
                website_el = company.select_one("a.website, .url a")
                website = website_el.get("href", "") if website_el else ""
                
                results.append({
                    "name": name,
                    "phone": phone,
                    "address": address,
                    "city": location_slug.replace("-", " ").title(),
                    "description": description,
                    "url": f"https://www.businesslist.com.ng{name_el.get('href', '')}" if name_el else "",
                    "website": website,
                    "working_hours": "",
                    "products": "",
                    "verified": False
                })
                existing_names.add(name.lower().strip())
                page_count += 1
            
            print(f"  Page {page}: {page_count} new (total: {len(results)})")
            
            if page_count == 0:
                break
                
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"  Page {page}: Error - {e}")
            break
    
    return results

def scrape_directory_org_ng(category_slug, existing_names=None, max_pages=30):
    """Scrape from directory.org.ng"""
    print(f"\n=== directory.org.ng: {category_slug} ===")
    results = []
    existing_names = existing_names or set()
    
    for page in range(1, max_pages + 1):
        url = f"https://www.directory.org.ng/{category_slug}"
        if page > 1:
            url += f"/page/{page}"
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 404:
                print(f"  Page {page}: No more pages (404)")
                break
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            # Find company listings - adjust selectors based on actual structure
            companies = soup.select("div.company, .listing-item, .result-item")
            
            if not companies:
                companies = soup.select("a[href*='company'], a[href*='listing']")
            
            if not companies:
                print(f"  Page {page}: No companies found")
                break
            
            page_count = 0
            for company in companies:
                name_el = company.select_one("h3 a, h2 a, .title a")
                name = name_el.get_text(strip=True) if name_el else company.get_text(strip=True)
                
                if not name or name.lower().strip() in existing_names:
                    continue
                
                addr_el = company.select_one(".address, .location")
                address = addr_el.get_text(strip=True) if addr_el else ""
                
                desc_el = company.select_one(".description, .desc")
                description = desc_el.get_text(strip=True) if desc_el else ""
                
                results.append({
                    "name": name,
                    "phone": "",
                    "address": address,
                    "city": "Lagos",
                    "description": description,
                    "url": name_el.get("href", "") if name_el else company.get("href", ""),
                    "website": "",
                    "working_hours": "",
                    "products": "",
                    "verified": False
                })
                existing_names.add(name.lower().strip())
                page_count += 1
            
            print(f"  Page {page}: {page_count} new (total: {len(results)})")
            
            if page_count == 0:
                break
                
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"  Page {page}: Error - {e}")
            break
    
    return results

def scrape_businessfinder(category_slug, existing_names=None, max_pages=30):
    """Scrape from businessfinder.ng"""
    print(f"\n=== businessfinder.ng: {category_slug} ===")
    results = []
    existing_names = existing_names or set()
    
    for page in range(1, max_pages + 1):
        url = f"https://www.businessfinder.ng/?s={category_slug.replace('-', '+')}"
        if page > 1:
            url += f"&paged={page}"
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 404:
                print(f"  Page {page}: No more pages (404)")
                break
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            companies = soup.select(".listing-item, .grid-listing-item, .classic-view-grid")
            
            if not companies:
                print(f"  Page {page}: No companies found")
                break
            
            page_count = 0
            for company in companies:
                name_el = company.select_one("h4 a, h3 a, .title a")
                name = name_el.get_text(strip=True) if name_el else ""
                
                if not name or name.lower().strip() in existing_names:
                    continue
                
                addr_el = company.select_one(".address, .listing-address")
                address = addr_el.get_text(strip=True) if addr_el else ""
                
                desc_el = company.select_one(".description, .excerpt")
                description = desc_el.get_text(strip=True) if desc_el else ""
                
                results.append({
                    "name": name,
                    "phone": "",
                    "address": address,
                    "city": "Lagos",
                    "description": description,
                    "url": name_el.get("href", "") if name_el else "",
                    "website": "",
                    "working_hours": "",
                    "products": "",
                    "verified": False
                })
                existing_names.add(name.lower().strip())
                page_count += 1
            
            print(f"  Page {page}: {page_count} new (total: {len(results)})")
            
            if page_count == 0:
                break
                
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"  Page {page}: Error - {e}")
            break
    
    return results

def scrape_finelib(category_slug, existing_names=None, max_pages=30):
    """Scrape from Finelib.com"""
    print(f"\n=== Finelib.com: {category_slug} ===")
    results = []
    existing_names = existing_names or set()
    
    for page in range(1, max_pages + 1):
        url = f"https://www.finelib.com/categories/{category_slug}/lagos"
        if page > 1:
            url += f"/page-{page}"
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 404:
                print(f"  Page {page}: No more pages (404)")
                break
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            companies = soup.select(".listing-item, .result, .company")
            
            if not companies:
                print(f"  Page {page}: No companies found")
                break
            
            page_count = 0
            for company in companies:
                name_el = company.select_one("h3 a, h2 a, .title a")
                name = name_el.get_text(strip=True) if name_el else ""
                
                if not name or name.lower().strip() in existing_names:
                    continue
                
                addr_el = company.select_one(".address, .location")
                address = addr_el.get_text(strip=True) if addr_el else ""
                
                desc_el = company.select_one(".description, .desc")
                description = desc_el.get_text(strip=True) if desc_el else ""
                
                results.append({
                    "name": name,
                    "phone": "",
                    "address": address,
                    "city": "Lagos",
                    "description": description,
                    "url": name_el.get("href", "") if name_el else "",
                    "website": "",
                    "working_hours": "",
                    "products": "",
                    "verified": False
                })
                existing_names.add(name.lower().strip())
                page_count += 1
            
            print(f"  Page {page}: {page_count} new (total: {len(results)})")
            
            if page_count == 0:
                break
                
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"  Page {page}: Error - {e}")
            break
    
    return results

def main():
    existing_names = load_existing_names()
    all_new = []
    
    # Category mappings for each source
    categories = {
        "realestate": {
            "businesslist": "estate-agents",
            "directory_org_ng": "real_estate",
            "businessfinder": "real-estate",
            "finelib": "real-estate"
        },
        "hospitals": {
            "businesslist": "doctors",
            "directory_org_ng": "health_medical",
            "businessfinder": "hospitals",
            "finelib": "hospitals"
        },
        "hotels": {
            "businesslist": "restaurants",
            "directory_org_ng": "travel_lodging_tourism",
            "businessfinder": "hotels",
            "finelib": "hotels"
        }
    }
    
    # Start with just real estate in Lagos for testing
    for cat_key, sources in categories.items():
        print(f"\n{'='*60}")
        print(f"Category: {cat_key}")
        print(f"{'='*60}")
        
        # BusinessList
        try:
            results = scrape_businesslist(sources["businesslist"], "lagos", existing_names, max_pages=20)
            all_new.extend(results)
            print(f"  BusinessList: {len(results)} total")
        except Exception as e:
            print(f"  BusinessList failed: {e}")
        
        time.sleep(random.uniform(3, 6))
        
        # directory.org.ng
        try:
            results = scrape_directory_org_ng(sources["directory_org_ng"], existing_names, max_pages=20)
            all_new.extend(results)
            print(f"  directory.org.ng: {len(results)} total")
        except Exception as e:
            print(f"  directory.org.ng failed: {e}")
        
        time.sleep(random.uniform(3, 6))
        
        # businessfinder
        try:
            results = scrape_businessfinder(sources["businessfinder"], existing_names, max_pages=20)
            all_new.extend(results)
            print(f"  businessfinder: {len(results)} total")
        except Exception as e:
            print(f"  businessfinder failed: {e}")
        
        time.sleep(random.uniform(3, 6))
        
        # finelib
        try:
            results = scrape_finelib(sources["finelib"], existing_names, max_pages=20)
            all_new.extend(results)
            print(f"  finelib: {len(results)} total")
        except Exception as e:
            print(f"  finelib failed: {e}")
        
        time.sleep(random.uniform(3, 6))
    
    print(f"\n{'='*60}")
    print(f"TOTAL NEW: {len(all_new)}")
    print(f"{'='*60}")
    
    # Save
    output = "data/nigeria_multi_source_new.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_new, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to {output}")

if __name__ == "__main__":
    main()
