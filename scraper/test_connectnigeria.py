import json
import time
from playwright.sync_api import sync_playwright

def test_scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Intercept network requests to find API calls
        api_urls = []
        def handle_request(request):
            if "api" in request.url.lower() or "business" in request.url.lower() or "json" in request.url.lower():
                api_urls.append({"url": request.url, "method": request.method, "type": request.resource_type})
        page.on("request", handle_request)

        print("=== Loading /businesses ===")
        page.goto("https://www.connectnigeria.com/businesses", wait_until="networkidle", timeout=60000)
        time.sleep(5)

        print(f"\n=== Captured {len(api_urls)} relevant network requests ===")
        for r in api_urls[:20]:
            print(f"  [{r['method']}] {r['url']} ({r['type']})")

        # Check page content
        title = page.title()
        print(f"\nPage title: {title}")

        # Look for business cards/listings
        selectors_to_try = [
            ".business-card", ".business-item", ".listing-item",
            ".company-card", ".company-item", ".business-list",
            "[class*='business']", "[class*='listing']", "[class*='company']",
            "a[href*='/businesses/']", "a[href*='/business/']",
        ]

        for sel in selectors_to_try:
            els = page.query_selector_all(sel)
            if els:
                print(f"\nSelector '{sel}': {len(els)} elements")
                for el in els[:3]:
                    text = el.inner_text()[:120]
                    href = el.get_attribute("href") or ""
                    print(f"  - {text} | href={href}")

        # Get all links on page
        links = page.query_selector_all("a[href]")
        business_links = []
        for link in links:
            href = link.get_attribute("href") or ""
            if "/businesses/" in href or "/business/" in href:
                text = link.inner_text().strip()[:80]
                if text and href not in business_links:
                    business_links.append({"href": href, "text": text})

        print(f"\n=== Found {len(business_links)} business-related links ===")
        for bl in business_links[:15]:
            print(f"  {bl['href']} -> {bl['text']}")

        # Check for pagination
        pagination = page.query_selector_all(".pagination a, [class*='page'] a, [class*='pagination']")
        if pagination:
            print(f"\nPagination elements: {len(pagination)}")
            for p_el in pagination[:10]:
                print(f"  - {p_el.inner_text().strip()} -> {p_el.get_attribute('href')}")

        # Try clicking a category
        print("\n=== Testing Agriculture category ===")
        page.goto("https://www.connectnigeria.com/businesses/category/Agriculture", wait_until="networkidle", timeout=60000)
        time.sleep(5)

        api_urls2 = []
        page2 = context.new_page()
        def handle_request2(request):
            if "api" in request.url.lower() or "business" in request.url.lower() or "json" in request.url.lower():
                api_urls2.append({"url": request.url, "method": request.method, "type": request.resource_type})
        page2.on("request", handle_request2)
        page2.goto("https://www.connectnigeria.com/businesses/category/Agriculture", wait_until="networkidle", timeout=60000)
        time.sleep(5)

        print(f"\n=== Category page: {len(api_urls2)} relevant requests ===")
        for r in api_urls2[:20]:
            print(f"  [{r['method']}] {r['url']} ({r['type']})")

        # Get business links from category
        links2 = page2.query_selector_all("a[href]")
        biz_links2 = []
        for link in links2:
            href = link.get_attribute("href") or ""
            if "/businesses/" in href and "/category/" not in href:
                text = link.inner_text().strip()[:80]
                if text:
                    biz_links2.append({"href": href, "text": text})

        print(f"\n=== Category business links: {len(biz_links2)} ===")
        for bl in biz_links2[:10]:
            print(f"  {bl['href']} -> {bl['text']}")

        # Try to scrape a detail page
        if biz_links2:
            detail_url = biz_links2[0]["href"]
            if not detail_url.startswith("http"):
                detail_url = "https://www.connectnigeria.com" + detail_url
            print(f"\n=== Scraping detail: {detail_url} ===")

            page3 = context.new_page()
            page3.goto(detail_url, wait_until="networkidle", timeout=60000)
            time.sleep(3)

            # Get all text content
            body_text = page3.inner_text("body")
            print(f"\nDetail page text (first 2000 chars):\n{body_text[:2000]}")

            # Look for contact info
            for sel in ["a[href^='tel:']", "a[href^='mailto:']", ".phone", ".email", ".address", ".website"]:
                els = page3.query_selector_all(sel)
                if els:
                    print(f"\nSelector '{sel}': {len(els)}")
                    for el in els[:3]:
                        print(f"  - {el.inner_text().strip()} | {el.get_attribute('href')}")

        browser.close()

if __name__ == "__main__":
    test_scrape()
