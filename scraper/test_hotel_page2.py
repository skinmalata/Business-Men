import requests
from bs4 import BeautifulSoup
import json
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resp = requests.get('https://hotels.ng/hotel/26241-ibis-lagos-airport-lagos', headers=headers, timeout=15)

# Look for embedded JSON data in script tags
soup = BeautifulSoup(resp.text, 'html.parser')
scripts = soup.find_all('script')

for i, script in enumerate(scripts):
    if script.string:
        # Look for hotel data patterns
        if 'hotel' in script.string.lower() and ('name' in script.string.lower() or 'address' in script.string.lower()):
            # Try to find JSON objects
            json_matches = re.findall(r'(\{[^{}]*"name"[^{}]*\})', script.string)
            if json_matches:
                print(f'Script {i} has potential hotel data:')
                for match in json_matches[:3]:
                    print(f'  {match[:200]}')
                print()

# Look for window.__INITIAL_STATE__ or similar patterns
state_patterns = re.findall(r'window\.__[A-Z_]+__\s*=\s*({[^;]+})', resp.text)
if state_patterns:
    print(f'Found {len(state_patterns)} state patterns')
    for state in state_patterns[:2]:
        print(f'  {state[:500]}')

# Look for API calls in JavaScript
api_urls = re.findall(r'["\'](/api/v[0-9]+/[^"\']+)["\']', resp.text)
print(f'\nFound {len(api_urls)} API URLs')
for url in api_urls[:10]:
    print(f'  {url}')

# Check for data in meta tags or Open Graph
og_tags = soup.select('meta[property^="og:"]')
print(f'\nOpen Graph tags: {len(og_tags)}')
for tag in og_tags:
    print(f'  {tag.get("property")}: {tag.get("content")[:100]}')

# Look for the actual hotel name in the page
title = soup.select_one('title')
print(f'\nPage title: {title.get_text(strip=True) if title else "Not found"}')

# Look for h1 tags
h1s = soup.select('h1')
print(f'H1 tags: {len(h1s)}')
for h1 in h1s:
    print(f'  {h1.get_text(strip=True)[:100]}')
