import requests
from bs4 import BeautifulSoup
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resp = requests.get('https://hotels.ng/hotel/26241-ibis-lagos-airport-lagos', headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# Get hotel name
name = soup.select_one('h1, .hotel-name, .property-name')
name_text = name.get_text(strip=True) if name else 'Not found'
print(f'Name: {name_text}')

# Get address
address = soup.select_one('.address, .location, .hotel-address')
address_text = address.get_text(strip=True) if address else 'Not found'
print(f'Address: {address_text}')

# Get phone
phone = soup.select_one('a[href^="tel:"], .phone')
phone_text = phone.get_text(strip=True) if phone else 'Not found'
print(f'Phone: {phone_text}')

# Look for JSON-LD structured data
json_ld = soup.select_one('script[type="application/ld+json"]')
if json_ld:
    data = json.loads(json_ld.string)
    print(f'JSON-LD: {json.dumps(data, indent=2)[:1000]}')

# Look for all links with tel:
tel_links = soup.select('a[href^="tel:"]')
print(f'\nTel links: {len(tel_links)}')
for link in tel_links:
    print(f'  - {link.get("href")} - {link.get_text(strip=True)}')

# Look for meta tags with hotel info
meta_tags = soup.select('meta[property*="hotel"], meta[name*="hotel"]')
print(f'\nMeta tags: {len(meta_tags)}')
for meta in meta_tags:
    print(f'  - {meta.get("property")} or {meta.get("name")}: {meta.get("content")}')
