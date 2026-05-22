import requests
from bs4 import BeautifulSoup
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Scrape a single hotel page to understand the structure
url = 'https://hotels.ng/hotel/26241-ibis-lagos-airport-lagos'
resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# Get hotel name from h1 or title
name_el = soup.select_one('h1')
name = name_el.get_text(strip=True) if name_el else ''
print(f'Name: {name}')

# Get location from title or breadcrumb
title = soup.select_one('title')
title_text = title.get_text(strip=True) if title else ''
print(f'Title: {title_text}')

# Extract location from title (format: "Hotel Name | Hotel in Location | Hotels.ng")
location = ''
if '|' in title_text:
    parts = title_text.split('|')
    if len(parts) >= 2:
        location_part = parts[1].strip()
        # Remove "Hotel in" prefix
        location = location_part.replace('Hotel in', '').replace('Hotels in', '').strip()
print(f'Location: {location}')

# Get all phone numbers
tel_links = soup.select('a[href^="tel:"]')
phones = []
for link in tel_links:
    phone = link.get('href', '').replace('tel:', '').strip()
    if phone and phone not in phones:
        phones.append(phone)
print(f'Phones: {phones}')

# Get description from meta description
meta_desc = soup.select_one('meta[name="description"]')
description = meta_desc.get('content', '') if meta_desc else ''
print(f'Description: {description[:200]}')

# Get Open Graph description
og_desc = soup.select_one('meta[property="og:description"]')
og_description = og_desc.get('content', '') if og_desc else ''
print(f'OG Description: {og_description[:200]}')

# Look for address in the page
# Check for any elements that might contain address
address_els = soup.select('.address, .location, .hotel-address, [class*="address"], [class*="location"]')
print(f'\nAddress elements found: {len(address_els)}')
for el in address_els[:5]:
    text = el.get_text(strip=True)
    if text and len(text) > 5:
        print(f'  - {text[:100]}')

# Look for amenities or features
amenities = soup.select('.amenity, .feature, [class*="amenity"], [class*="feature"]')
print(f'\nAmenity elements found: {len(amenities)}')
for el in amenities[:5]:
    text = el.get_text(strip=True)
    if text:
        print(f'  - {text[:100]}')

# Check for JSON-LD hotel data
json_ld_scripts = soup.select('script[type="application/ld+json"]')
for script in json_ld_scripts:
    try:
        data = json.loads(script.string)
        if data.get('@type') == 'Hotel' or data.get('@type') == 'LodgingBusiness':
            print(f'\nJSON-LD Hotel data: {json.dumps(data, indent=2)[:500]}')
    except:
        pass
