import requests
from bs4 import BeautifulSoup
import json
import re
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Test page 2 of Lagos hotels
resp = requests.get('https://hotels.ng/hotels-in-lagos/2', headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

hotel_links = soup.select('a[href*="/hotel/"]')
unique_hotels = {}
for link in hotel_links:
    href = link.get('href', '')
    if '/hotel/' in href:
        hotel_id = href.split('/hotel/')[1].split('-')[0] if '/hotel/' in href else None
        if hotel_id:
            unique_hotels[hotel_id] = href

print(f'Page 2: {len(hotel_links)} total links, {len(unique_hotels)} unique hotels')
print('Sample hotels from page 2:')
for url in list(unique_hotels.values())[:5]:
    print(f'  {url}')

# Check next page link
next_page = soup.select_one('a[rel="next"]')
if next_page:
    print(f'\nNext page: {next_page.get("href")}')

# Check for pagination numbers
page_links = soup.select('.pagination a[href*="/hotels-in-lagos/"]')
print(f'\nPagination page links: {len(page_links)}')
for p in page_links[:15]:
    href = p.get('href', '')
    text = p.get_text(strip=True)
    if text and text.isdigit():
        print(f'  Page {text}: {href}')
