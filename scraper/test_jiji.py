import json
import time
from playwright.sync_api import sync_playwright

def test_jiji():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Capture API requests
        api_calls = []
        def handle_request(request):
            url = request.url
            if "jiji" in url and ("api" in url.lower() or "graphql" in url.lower() or "ads" in url.lower()):
                api_calls.append({"url": url, "method": request.method, "type": request.resource_type})
        page.on("request", handle_request)

        # Capture API responses
        api_responses = []
        def handle_response(response):
            url = response.url
            if "jiji" in url and ("api" in url.lower() or "graphql" in url.lower() or "ads" in url.lower() or "advert" in url.lower()):
                try:
                    data = response.json()
                    api_responses.append({"url": url, "status": response.status, "data": data})
                except:
                    pass
        page.on("response", handle_response)

        # Test 1: Category listing page
        print("=== Loading category page ===")
        page.goto("https://jiji.ng/lagos/home-garden", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        print(f"\nCaptured {len(api_calls)} API calls:")
        for c in api_calls[:20]:
            print(f"  [{c['method']}] {c['url'][:150]} ({c['type']})")

        print(f"\nCaptured {len(api_responses)} API responses:")
        for r in api_responses[:10]:
            url = r["url"][:120]
            data = r["data"]
            print(f"\n  [{r['status']}] {url}")
            if isinstance(data, dict):
                for k, v in list(data.items())[:5]:
                    if isinstance(v, list):
                        print(f"    {k}: [{len(v)} items]")
                        if v and isinstance(v[0], dict):
                            print(f"      First: {json.dumps(v[0], ensure_ascii=False)[:200]}")
                    else:
                        print(f"    {k}: {str(v)[:200]}")

        # Get product links from listing
        print("\n=== Product links ===")
        links = page.query_selector_all("a[href*='.html']")
        products = []
        for link in links:
            href = link.get_attribute("href") or ""
            if "/lagos" in href and ".html" in href and "page=" not in href.split(".html")[0]:
                title = link.get_attribute("title") or link.inner_text().strip()[:80]
                if title and href not in [p["href"] for p in products]:
                    products.append({"href": href, "title": title})

        print(f"Found {len(products)} product links")
        for pr in products[:5]:
            print(f"  {pr['title']} -> {pr['href']}")

        # Test 2: Product detail page
        if products:
            detail_url = "https://jiji.ng" + products[0]["href"]
            print(f"\n=== Loading product detail: {detail_url} ===")

            api_calls2 = []
            api_responses2 = []
            page2 = context.new_page()
            def handle_request2(request):
                url = request.url
                if "jiji" in url and ("api" in url.lower() or "graphql" in url.lower() or "advert" in url.lower() or "seller" in url.lower() or "phone" in url.lower()):
                    api_calls2.append({"url": url, "method": request.method})
            page2.on("request", handle_request2)
            def handle_response2(response):
                url = response.url
                if "jiji" in url and ("api" in url.lower() or "graphql" in url.lower() or "advert" in url.lower() or "seller" in url.lower() or "phone" in url.lower()):
                    try:
                        data = response.json()
                        api_responses2.append({"url": url, "status": response.status, "data": data})
                    except:
                        pass
            page2.on("response", handle_response2)

            page2.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
            page2.wait_for_timeout(5000)

            print(f"\nAPI calls on detail page: {len(api_calls2)}")
            for c in api_calls2[:20]:
                print(f"  [{c['method']}] {c['url'][:150]}")

            print(f"\nAPI responses on detail page: {len(api_responses2)}")
            for r in api_responses2[:10]:
                print(f"\n  [{r['status']}] {r['url'][:150]}")
                print(f"  Data: {json.dumps(r['data'], ensure_ascii=False)[:500]}")

            # Check page content for phone/contact
            body_text = page2.inner_text("body")
            print(f"\nPage text (first 2000 chars):\n{body_text[:2000]}")

            # Look for phone numbers
            phone_els = page2.query_selector_all("a[href^='tel:']")
            print(f"\nPhone links found: {len(phone_els)}")
            for el in phone_els[:5]:
                print(f"  {el.get_attribute('href')} -> {el.inner_text().strip()}")

        browser.close()

if __name__ == "__main__":
    test_jiji()
