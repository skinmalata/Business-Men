import requests
from bs4 import BeautifulSoup

# Try different URL patterns
urls = [
    "https://www.businesslist.com.ng/category/estate-agents/lagos",
    "https://www.businesslist.com.ng/location/lagos/estate-agents",
    "https://www.businesslist.com.ng/estate-agents/lagos",
    "https://www.businesslist.com.ng/search?q=real+estate+lagos",
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for url in urls:
    print(f"\nTrying: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Look for company links
            company_links = soup.select("a[href*='/company/']")
            print(f"Company links found: {len(company_links)}")
            
            for link in company_links[:3]:
                print(f"  - {link.get_text(strip=True)[:80]}")
            
            # Save for inspection
            with open(f"test_{url.split('/')[-2]}.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"Saved to test_{url.split('/')[-2]}.html")
            
    except Exception as e:
        print(f"Error: {e}")
