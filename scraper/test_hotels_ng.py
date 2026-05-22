import requests
from bs4 import BeautifulSoup
import json
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resp = requests.get('https://hotels.ng/hotels-in-lagos', headers=headers, timeout=15)

soup = BeautifulSoup(resp.text, 'html.parser')

# Look for JSON data embedded in script tags
script_tags = soup.find_all('script')
for script in script_tags:
    if script.string and ('hotel' in script.string.lower() or 'property' in script.string.lower()):
        json_match = re.search(r'(\{.*"hotel.*\})', script.string, re.DOTALL)
        if json_match:
            print('Found JSON in script tag')
            print(json_match.group(1)[:500])
            break

# Look for links to individual hotel pages
hotel_links = soup.select('a[href*="/hotel/"]')
print(f'Found {len(hotel_links)} hotel links')
for link in hotel_links[:5]:
    print(f'  - {link.get("href")} - {link.get_text(strip=True)[:50]}')

# Look for any data-* attributes on hotel elements
hotel_cards = soup.select('.hotel-card, .property-card, .listing-item, .result-item')
print(f'Found {len(hotel_cards)} hotel cards')

# Check for pagination
pagination = soup.select('.pagination, .page-link, [class*="page"]')
print(f'Found {len(pagination)} pagination elements')

# Look for API endpoints in JavaScript
api_patterns = re.findall(r'["\'](/api/[^"\']+)["\']', resp.text)
print(f'Found {len(api_patterns)} API endpoints')
for api in api_patterns[:10]:
    print(f'  - {api}')
