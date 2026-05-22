import requests
from bs4 import BeautifulSoup
import json
import time
import random

url = "https://www.businesslist.com.ng/category/estate-agents/lagos"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")

# Find all company containers
companies = soup.select("div.company, li.company")
print(f"Found {len(companies)} company containers")

for company in companies[:3]:
    print("\n" + "="*50)
    print(company.prettify()[:800])
    print("="*50)
