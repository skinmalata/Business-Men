import json
import time
import random
import re
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_title(text):
    """Remove Jiji badge noise from titles"""
    if not text:
        return ""
    # Remove badge patterns
    text = re.sub(r'Verified ID\s*', '', text)
    text = re.sub(r'\d+\+ YEARS ON JIJI\s*', '', text)
    text = re.sub(r'\d+ YEARS ON JIJI\s*', '', text)
    text = re.sub(r'ENTERPRISE\s*', '', text)
    text = re.sub(r'PREMIUM\s*', '', text)
    text = re.sub(r'DIAMOND\s*', '', text)
    text = re.sub(r'Popular\s*', '', text)
    text = re.sub(r'Quick reply\s*', '', text)
    # Remove currency patterns
    text = re.sub(r'\u20a6\s*[\d,]+\s*', '', text)
    # Clean up
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_price(text):
    """Extract numeric price"""
    if not text:
        return ""
    # Remove everything after first newline
    text = text.split('\n')[0]
    # Remove currency symbol and commas
    text = text.replace('\u20a6', '').replace(',', '').strip()
    # Keep only digits
    text = re.sub(r'[^\d]', '', text)
    return text

def clean_location(text):
    """Extract just the location"""
    if not text:
        return ""
    # Remove "Promoted" prefix
    text = re.sub(r'^Promoted\s*', '', text)
    # Remove time ago and views
    text = re.sub(r',\s*\d+\s*(hour|day|min|week)s?\s*ago.*$', '', text)
    text = re.sub(r'\d+\s*views?\s*$', '', text)
    text = text.strip().rstrip(',')
    return text

def scrape_products(max_products=100):
    products = []
    seen_urls = set()

    categories = [
        ("home-garden", "Home & Furniture"),
        ("electronics", "Electronics"),
        ("fashion-and-beauty", "Fashion"),
        ("mobile-phones-tablets", "Phones & Tablets"),
        ("vehicles", "Vehicles"),
        ("repair-and-construction", "Repair & Construction"),
        ("office-and-commercial-equipment-tools", "Commercial Equipment"),
        ("health-and-beauty", "Beauty & Personal Care"),
        ("agriculture-and-foodstuff", "Food & Agriculture"),
        ("hobbies-art-sport", "Leisure & Sports"),
        ("babies-and-kids", "Babies & Kids"),
        ("animals-and-pets", "Animals & Pets"),
        ("services", "Services"),
        ("jobs", "Jobs"),
        ("real-estate", "Real Estate"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        for cat_slug, cat_name in categories:
            if len(products) >= max_products:
                break

            print(f"\n=== {cat_name} ===")

            page = context.new_page()

            try:
                page.goto(f"https://jiji.ng/lagos/{cat_slug}", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(5000)

                # Get product links
                links = page.query_selector_all("a.qa-advert-list-item")
                if not links:
                    links = page.query_selector_all("a[href*='.html']")

                product_urls = []
                for link in links:
                    href = link.get_attribute("href") or ""
                    if href and ".html" in href and "/lagos" in href:
                        clean_href = href.split("?")[0]
                        if clean_href not in seen_urls:
                            seen_urls.add(clean_href)
                            title = link.get_attribute("title") or ""
                            if not title:
                                title = link.inner_text().strip()[:150]
                            product_urls.append({"url": href, "title": title})

                print(f"  Found {len(product_urls)} products")

                # Scrape detail pages
                to_scrape = min(10, len(product_urls), max_products - len(products))
                for i in range(to_scrape):
                    prod = product_urls[i]
                    detail_url = "https://jiji.ng" + prod["url"]

                    detail_page = context.new_page()
                    try:
                        detail_page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
                        detail_page.wait_for_timeout(4000)

                        product = extract_product_detail(detail_page, prod["title"], cat_name, detail_url)
                        if product:
                            products.append(product)
                            print(f"  [{len(products)}] {product['title'][:50]} | {product['price']} | {product['location']}")

                    except Exception as e:
                        print(f"    Error: {str(e)[:60]}")
                    finally:
                        detail_page.close()
                        time.sleep(random.uniform(1.5, 3))

            except Exception as e:
                print(f"  Error: {str(e)[:60]}")
            finally:
                page.close()
                time.sleep(random.uniform(2, 4))

        browser.close()

    return products

def extract_product_detail(page, fallback_title, category, url):
    try:
        # Extract from JSON-LD structured data
        json_ld = page.evaluate("""() => {
            const scripts = document.querySelectorAll('script[type="application/ld+json"]');
            for (const s of scripts) {
                try { return JSON.parse(s.textContent); } catch(e) {}
            }
            return null;
        }""")

        title = ""
        price = ""
        description = ""
        location = ""
        images = []
        seller_name = ""
        seller_type = ""
        phone = ""
        condition = ""

        if json_ld:
            title = json_ld.get("name", "") or fallback_title
            offers = json_ld.get("offers", {})
            if isinstance(offers, dict):
                price = str(offers.get("price", ""))
            description = json_ld.get("description", "") or ""
            address = json_ld.get("address", {})
            if isinstance(address, dict):
                location = address.get("addressLocality", "") or address.get("addressRegion", "") or ""
            img = json_ld.get("image", "")
            if img:
                images = img if isinstance(img, list) else [img]
            seller = json_ld.get("seller", {})
            if isinstance(seller, dict):
                seller_name = seller.get("name", "")

        # Fallback from DOM
        if not title or title == fallback_title:
            # Try h1
            h1 = page.query_selector("h1")
            if h1:
                title = h1.inner_text().strip()
            else:
                title = fallback_title

        if not price:
            price_el = page.query_selector("[class*='price'], .b-page-advert__price")
            if price_el:
                price = price_el.inner_text().strip()

        if not description:
            # Try multiple selectors
            for sel in [".b-advert-details__value", "[class*='description']", ".b-page-advert__description"]:
                desc_el = page.query_selector(sel)
                if desc_el:
                    description = desc_el.inner_text().strip()[:500]
                    break

        if not location:
            loc_el = page.query_selector("[class*='region'], [class*='location'], .b-page-advert__region")
            if loc_el:
                location = loc_el.inner_text().strip()

        # Get images from gallery
        if not images:
            for sel in [".b-page-advert__gallery img", "[class*='gallery'] img", ".js-gallery img"]:
                gallery_imgs = page.query_selector_all(sel)
                for img in gallery_imgs[:5]:
                    src = img.get_attribute("src") or img.get_attribute("data-src") or ""
                    if src and ("jijistatic" in src or "pictures-nigeria" in src):
                        images.append(src)
                if images:
                    break

        if not images:
            all_imgs = page.query_selector_all("img")
            for img in all_imgs:
                src = img.get_attribute("src") or ""
                if "pictures-nigeria.jijistatic.net" in src and src not in images:
                    images.append(src)
                    if len(images) >= 5:
                        break

        # Seller info
        if not seller_name:
            for sel in ["[class*='seller-name']", "[class*='shop-name']", ".b-shop-card__name"]:
                seller_el = page.query_selector(sel)
                if seller_el:
                    seller_name = seller_el.inner_text().strip()
                    break

        # Seller type
        for badge in page.query_selector_all("[class*='premium'], [class*='verified'], [class*='enterprise'], [class*='diamond'], [class*='badge']"):
            text = badge.inner_text().strip().lower()
            if text and any(k in text for k in ["premium", "verified", "enterprise", "diamond", "vip"]):
                seller_type = text
                break

        # Phone
        for el in page.query_selector_all("a[href^='tel:']"):
            phone = el.get_attribute("href").replace("tel:", "").strip()
            if phone:
                break

        if not title:
            return None

        return {
            "title": clean_title(title),
            "price": clean_price(price),
            "description": clean_text(description)[:500],
            "location": clean_location(location),
            "category": category,
            "images": images[:5],
            "seller_name": clean_text(seller_name),
            "seller_type": seller_type,
            "phone": phone,
            "condition": condition,
            "source_url": url,
            "source": "jiji.ng",
        }

    except Exception as e:
        print(f"    Extract error: {str(e)[:60]}")
        return None

def main():
    print("Scraping Jiji.ng marketplace products...")
    products = scrape_products(max_products=100)

    print(f"\n=== Results: {len(products)} products ===")

    output = "data/marketplace_jiji_products.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output}")

    # Summary
    cats = {}
    for p in products:
        cat = p.get("category", "Unknown")
        cats[cat] = cats.get(cat, 0) + 1
    print("\nBy category:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    with_price = sum(1 for p in products if p.get("price"))
    with_images = sum(1 for p in products if p.get("images"))
    with_location = sum(1 for p in products if p.get("location"))
    print(f"\nWith price: {with_price}")
    print(f"With images: {with_images}")
    print(f"With location: {with_location}")

    # Show sample
    if products:
        print(f"\nSample:")
        p = products[0]
        print(f"  Title: {p['title']}")
        print(f"  Price: {p['price']}")
        print(f"  Location: {p['location']}")
        print(f"  Images: {len(p['images'])}")
        print(f"  Seller: {p['seller_name']}")
        print(f"  Source: {p['source_url'][:80]}")

if __name__ == "__main__":
    main()
