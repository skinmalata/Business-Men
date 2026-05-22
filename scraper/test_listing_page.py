import requests
from bs4 import BeautifulSoup
import json
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Test the Lagos listing page
resp = requests.get('https://hotels.ng/hotels-in-lagos', headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# Get all unique hotel links
hotel_links = soup.select('a[href*="/hotel/"]')
unique_hotels = {}
for link in hotel_links:
    href = link.get('href', '')
    if '/hotel/' in href:
        hotel_id = href.split('/hotel/')[1].split('-')[0] if '/hotel/' in href else None
        if hotel_id:
            unique_hotels[hotel_id] = href

print(f'Found {len(hotel_links)} total links, {len(unique_hotels)} unique hotels')

# Get first 5 unique hotel URLs
hotel_urls = list(unique_hotels.values())[:5]
print('\nSample hotel URLs:')
for url in hotel_urls:
    print(f'  {url}')

# Check pagination
pagination = soup.select('.pagination a, .page-link, [class*="page"] a')
print(f'\nPagination elements: {len(pagination)}')
for p in pagination[:10]:
    print(f'  {p.get("href")} - {p.get_text(strip=True)}')

# Check for "next page" or page numbers
next_page = soup.select_one('a[class*="next"], a[rel="next"]')
if next_page:
    print(f'\nNext page: {next_page.get("href")}')

# Look for area/district links
area_links = soup.select('a[href*="/hotels-in-"]')
areas = {}
for link in area_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if 'hotels-in-' in href and text:
        areas[href] = text

print(f'\nArea links: {len(areas)}')
for href, text in list(areas.items())[:10]:
    print(f'  {text}: {href}')
