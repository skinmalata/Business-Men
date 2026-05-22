import requests
import json
import time
import random
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv("scraper/.env")

# Create session with retry logic
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=5,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

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

def get_company_urls_from_listing(category_slug, location_slug="lagos", max_pages=50):
    """Get all company URLs from listing pages"""
    print(f"\n=== Getting company URLs: {category_slug} in {location_slug} ===")
    urls = []
    
    for page in range(1, max_pages + 1):
        url = f"https://www.businesslist.com.ng/category/{category_slug}/{location_slug}"
        if page > 1:
            url += f"/{page}"
        
        try:
            resp = session.get(url, headers=HEADERS, timeout=20)
            if resp.status_code == 404:
                print(f"  Page {page}: No more pages")
                break
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("div.company_header h3 a, h3 a[href*='/company/']")
            
            if not links:
                print(f"  Page {page}: No links found")
                break
            
            page_count = 0
            for link in links:
                href = link.get("href", "")
                if "/company/" in href:
                    full_url = f"https://www.businesslist.com.ng{href}"
                    if full_url not in urls:
                        urls.append(full_url)
                        page_count += 1
            
            print(f"  Page {page}: {page_count} URLs (total: {len(urls)})")
            
            if page_count == 0:
                break
                
            time.sleep(random.uniform(2, 4))
            
        except requests.exceptions.ConnectionError as e:
            print(f"  Page {page}: Connection error - {e}")
            print("  Waiting 30s before retry...")
            time.sleep(30)
            # Try one more time
            try:
                resp = session.get(url, headers=HEADERS, timeout=20)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    links = soup.select("div.company_header h3 a, h3 a[href*='/company/']")
                    page_count = 0
                    for link in links:
                        href = link.get("href", "")
                        if "/company/" in href:
                            full_url = f"https://www.businesslist.com.ng{href}"
                            if full_url not in urls:
                                urls.append(full_url)
                                page_count += 1
                    print(f"  Page {page} (retry): {page_count} URLs (total: {len(urls)})")
                    if page_count == 0:
                        break
                    time.sleep(random.uniform(2, 4))
                else:
                    break
            except Exception as e2:
                print(f"  Page {page}: Retry failed - {e2}")
                break
        except Exception as e:
            print(f"  Page {page}: Error - {e}")
            break
    
    return urls

def scrape_company_detail(url):
    """Scrape full details from a company page"""
    try:
        resp = session.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Name
        name_el = soup.select_one("h1, .company_name, .title")
        name = name_el.get_text(strip=True) if name_el else ""
        # Clean up name (remove location suffix)
        if " - " in name:
            name = name.split(" - ")[0].strip()
        
        if not name:
            return None
        
        # Phones
        phone_els = soup.select("a[href^='tel:'], .phone, .contact-phone, .tel")
        phones = []
        for p in phone_els:
            phone = p.get_text(strip=True) or p.get("href", "").replace("tel:", "")
            if phone and phone not in phones:
                phones.append(phone)
        
        # Address
        addr_el = soup.select_one(".address, .location, .addr")
        address = addr_el.get_text(strip=True) if addr_el else ""
        # Clean up address
        address = address.replace("View Map", "").replace("Get Directions", "").strip()
        
        # Description
        desc_el = soup.select_one(".description, .about, .tagline")
        description = desc_el.get_text(strip=True) if desc_el else ""
        
        # Website
        website = ""
        web_els = soup.select(".website a, a[href^='http']")
        for w in web_els:
            href = w.get("href", "")
            if href and "businesslist.com.ng" not in href and href.startswith("http"):
                website = href
                break
        
        # Hours
        hours_el = soup.select_one(".hours, .opening_hours")
        hours = hours_el.get_text(strip=True) if hours_el else ""
        
        # Determine city from address
        city = "Lagos"
        if "lagos" in address.lower():
            city = "Lagos"
        elif "ibadan" in address.lower():
            city = "Oyo"
        elif "abuja" in address.lower():
            city = "Abuja FCT"
        elif "port harcourt" in address.lower():
            city = "Rivers"
        
        return {
            "name": name,
            "phone": ", ".join(phones),
            "address": address,
            "city": city,
            "description": description,
            "url": url,
            "website": website,
            "working_hours": hours,
            "products": "",
            "verified": False
        }
        
    except Exception as e:
        print(f"    Error scraping {url}: {e}")
        return None

def main():
    existing_names = load_existing_names()
    all_new = []
    
    # Load checkpoint if exists
    checkpoint_file = "scraper/checkpoint.json"
    start_cat = 0
    start_city = 0
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, "r") as f:
                cp = json.load(f)
                start_cat = cp.get("category_index", 0)
                start_city = cp.get("city_index", 0)
                all_new = cp.get("results", [])
                existing_names = set(cp.get("existing_names", []))
                print(f"Resuming from checkpoint: category {start_cat}, city {start_city}")
        except:
            pass
    
    # Cities to scrape (BusinessList location slugs)
    cities = [
        ("lagos", "Lagos"),
        ("abuja", "Abuja FCT"),
        ("port-harcourt", "Rivers"),
        ("ikeja", "Lagos"),
        ("lagos-island", "Lagos"),
        ("victoria-island", "Lagos"),
        ("enugu", "Enugu"),
        ("ibadan", "Oyo"),
        ("kano", "Kano"),
        ("kaduna", "Kaduna"),
        ("benin-city", "Edo"),
        ("owerri", "Imo"),
        ("calabar", "Cross River"),
        ("warri", "Delta"),
        ("abeokuta", "Ogun"),
        ("akure", "Ondo"),
        ("jos", "Plateau"),
        ("ilorin", "Kwara"),
        ("uyo", "Akwa Ibom"),
        ("asaba", "Delta"),
    ]
    
    # Categories to scrape from BusinessList
    categories = [
        ("estate-agents", "realestate"),
        ("doctors", "hospitals"),
        ("restaurants", "food"),
        ("shopping", "shopping"),
        ("construction", "construction"),
        ("schools", "schools"),
        ("travel", "hotels"),
        ("automotive", "automobile"),
        ("agriculture", "agriculture"),
        ("business-services", "business"),
    ]
    
    def save_checkpoint(cat_idx, city_idx):
        cp = {
            "category_index": cat_idx,
            "city_index": city_idx,
            "results": all_new,
            "existing_names": list(existing_names)
        }
        with open(checkpoint_file, "w") as f:
            json.dump(cp, f)
    
    for cat_idx in range(start_cat, len(categories)):
        bl_slug, category_key = categories[cat_idx]
        print(f"\n{'='*60}")
        print(f"Category: {category_key} ({bl_slug})")
        print(f"{'='*60}")
        
        # Recreate session every category to clear DNS cache
        global session
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        
        category_results = []
        city_start = start_city if cat_idx == start_cat else 0
        
        for city_idx in range(city_start, len(cities)):
            city_slug, city_name = cities[city_idx]
            print(f"\n  --- City: {city_name} ({city_slug}) ---")
            
            # Step 1: Get all company URLs
            urls = get_company_urls_from_listing(bl_slug, city_slug, max_pages=20)
            
            if not urls:
                print(f"    No URLs found")
                save_checkpoint(cat_idx, city_idx + 1)
                time.sleep(random.uniform(3, 5))  # Wait before next city
                continue
            
            print(f"    Found {len(urls)} company URLs. Scraping details...")
            
            # Step 2: Scrape each company page
            for i, url in enumerate(urls):
                if i % 10 == 0 and i > 0:
                    print(f"    Progress: {i}/{len(urls)}")
                
                detail = scrape_company_detail(url)
                if detail:
                    detail["city"] = city_name
                    name_key = detail["name"].lower().strip()
                    if name_key not in existing_names:
                        all_new.append(detail)
                        category_results.append(detail)
                        existing_names.add(name_key)
                
                time.sleep(random.uniform(1.5, 3))
            
            print(f"    {city_name}: {len([d for d in category_results if d['city'] == city_name])} new entries")
            save_checkpoint(cat_idx, city_idx + 1)
            time.sleep(random.uniform(3, 6))  # Longer delay between cities
        
        print(f"\n  {category_key}: {len(category_results)} total new entries")
        
        # Save progress after each category
        if all_new:
            output = f"data/nigeria_businesslist_{category_key}.json"
            with open(output, "w", encoding="utf-8") as f:
                json.dump(all_new, f, indent=2, ensure_ascii=False)
            print(f"  Saved {len(all_new)} total to {output}")
        
        start_city = 0  # Reset for next category
        time.sleep(random.uniform(2, 4))
    
    print(f"\n{'='*60}")
    print(f"TOTAL NEW ENTRIES: {len(all_new)}")
    print(f"{'='*60}")
    
    # Final save
    output = "data/nigeria_businesslist_all.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_new, f, indent=2, ensure_ascii=False)
    
    print(f"Saved all to {output}")
    
    # Clean up checkpoint
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

if __name__ == "__main__":
    main()
