import requests
from bs4 import BeautifulSoup
import json
import re
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Check the last page to see total pages
# Try page 200 to see if it exists
for page_num in [50, 100, 150, 180, 190, 200]:
    url = f'https://hotels.ng/hotels-in-lagos/{page_num}'
    resp = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    hotel_links = soup.select('a[href*="/hotel/"]')
    unique_hotels = {}
    for link in hotel_links:
        href = link.get('href', '')
        if '/hotel/' in href:
            hotel_id = href.split('/hotel/')[1].split('-')[0] if '/hotel/' in href else None
            if hotel_id:
                unique_hotels[hotel_id] = href
    
    status = resp.status_code
    print(f'Page {page_num}: Status {status}, {len(unique_hotels)} unique hotels')
    
    if len(unique_hotels) == 0:
        print(f'  -> Last valid page is before {page_num}')
        break
    
    time.sleep(1)
