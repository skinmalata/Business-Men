import json
import time
from playwright.sync_api import sync_playwright

def test_categories():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Capture API responses
        api_responses = []
        def handle_response(response):
            if "api.connectnigeria.com" in response.url:
                try:
                    data = response.json()
                    api_responses.append({"url": response.url, "data": data})
                except:
                    pass
        page.on("response", handle_response)

        print("=== Loading /businesses ===")
        page.goto("https://www.connectnigeria.com/businesses", wait_until="networkidle", timeout=60000)
        time.sleep(3)

        print(f"\n=== Captured {len(api_responses)} API responses ===")
        for r in api_responses:
            url = r["url"]
            data = r["data"]
            print(f"\nURL: {url}")
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == "data" and isinstance(v, list):
                        print(f"  {k}: [{len(v)} items]")
                        for item in v[:2]:
                            print(f"    - {json.dumps(item, ensure_ascii=False)[:200]}")
                    elif isinstance(v, (dict, list)):
                        print(f"  {k}: {json.dumps(v, ensure_ascii=False)[:200]}")
                    else:
                        print(f"  {k}: {v}")

        # Get all category links
        print("\n=== All category links ===")
        links = page.query_selector_all("a[href*='/businesses/category/']")
        categories = []
        for link in links:
            href = link.get_attribute("href") or ""
            text = link.inner_text().strip()
            if text and text not in ["Filters", "See 22 more categories"]:
                categories.append({"href": href, "text": text})
                print(f"  {text} -> {href}")

        # Now test a category page
        if categories:
            cat = categories[0]
            cat_url = "https://www.connectnigeria.com" + cat["href"]
            print(f"\n=== Testing category: {cat['text']} ({cat_url}) ===")

            api_responses2 = []
            page2 = context.new_page()
            def handle_response2(response):
                if "api.connectnigeria.com" in response.url:
                    try:
                        data = response.json()
                        api_responses2.append({"url": response.url, "data": data})
                    except:
                        pass
            page2.on("response", handle_response2)

            page2.goto(cat_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

            print(f"\n=== Category API responses: {len(api_responses2)} ===")
            for r in api_responses2:
                url = r["url"]
                data = r["data"]
                print(f"\nURL: {url}")
                if isinstance(data, dict):
                    for k, v in data.items():
                        if k == "data" and isinstance(v, list):
                            print(f"  {k}: [{len(v)} items]")
                            for item in v[:2]:
                                print(f"    - {json.dumps(item, ensure_ascii=False)[:300]}")
                        elif isinstance(v, (dict, list)):
                            print(f"  {k}: {json.dumps(v, ensure_ascii=False)[:200]}")
                        else:
                            print(f"  {k}: {v}")

            # Check for business links on category page
            biz_links = page2.query_selector_all("a[href*='/businesses/']")
            print(f"\nBusiness links on category page: {len(biz_links)}")
            for bl in biz_links[:5]:
                href = bl.get_attribute("href")
                text = bl.inner_text().strip()[:80]
                print(f"  {href} -> {text}")

            # Test detail page
            if biz_links:
                detail_href = None
                for bl in biz_links:
                    href = bl.get_attribute("href") or ""
                    if "/category/" not in href and href.startswith("/businesses/"):
                        detail_href = href
                        break

                if detail_href:
                    detail_url = "https://www.connectnigeria.com" + detail_href
                    print(f"\n=== Detail page: {detail_url} ===")

                    api_responses3 = []
                    page3 = context.new_page()
                    def handle_response3(response):
                        if "api.connectnigeria.com" in response.url:
                            try:
                                data = response.json()
                                api_responses3.append({"url": response.url, "data": data})
                            except:
                                pass
                    page3.on("response", handle_response3)

                    page3.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(3)

                    print(f"\nDetail API responses: {len(api_responses3)}")
                    for r in api_responses3:
                        print(f"\nURL: {r['url']}")
                        print(f"Data: {json.dumps(r['data'], indent=2, ensure_ascii=False)[:1500]}")

                    # Get page text
                    body_text = page3.inner_text("body")
                    print(f"\nDetail page text (first 1500):\n{body_text[:1500]}")

        browser.close()

if __name__ == "__main__":
    test_categories()
