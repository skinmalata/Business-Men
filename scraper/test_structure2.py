import requests
from bs4 import BeautifulSoup

url = "https://www.businesslist.com.ng/category/estate-agents/lagos"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")

# Find all links with /company/ in href
company_links = soup.select("a[href*='/company/']")
print(f"Found {len(company_links)} company links")

for link in company_links[:5]:
    print(f"\nLink: {link.get('href')}")
    print(f"Text: {link.get_text(strip=True)}")
    
    # Find parent container
    parent = link.parent
    while parent and parent.name != 'body':
        if parent.get('class'):
            print(f"Parent classes: {parent.get('class')}")
            break
        parent = parent.parent
