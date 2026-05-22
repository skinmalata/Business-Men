import requests
from bs4 import BeautifulSoup
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Binary search for last page
low = 200
high = 300
last_valid = 200

while low <= high:
    mid = (low + high) // 2
    url = f'https://hotels.ng/hotels-in-lagos/{mid}'
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        hotel_links = soup.select('a[href*="/hotel/"]')
        unique_hotels = set()
        for link in hotel_links:
            href = link.get('href', '')
            if '/hotel/' in href:
                hotel_id = href.split('/hotel/')[1].split('-')[0] if '/hotel/' in href else None
                if hotel_id:
                    unique_hotels.add(hotel_id)
        
        if len(unique_hotels) > 0:
            last_valid = mid
            print(f'Page {mid}: {len(unique_hotels)} hotels (valid)')
            low = mid + 1
        else:
            print(f'Page {mid}: 0 hotels (invalid)')
            high = mid - 1
        
        time.sleep(1)
    except Exception as e:
        print(f'Page {mid}: Error - {e}')
        high = mid - 1

print(f'\nLast valid page: {last_valid}')
print(f'Estimated total hotels: {last_valid * 23}')
