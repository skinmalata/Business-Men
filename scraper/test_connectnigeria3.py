import json
import time
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

def test_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        api_responses = []
        def handle_response(response):
            if "api.connectnigeria.com/api" in response.url:
                try:
                    data = response.json()
                    api_responses.append({"url": response.url, "data": data})
                    print(f"\n[API] {response.status} {response.url[:120]}")
                except:
                    pass
        page.on("response", handle_response)

        print("Loading /businesses...")
        page.goto("https://www.connectnigeria.com/businesses", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)

        print(f"\n=== {len(api_responses)} API responses ===")
        for r in api_responses:
            data = r["data"]
            print(f"\n--- {r['url'][:150]} ---")
            if isinstance(data, dict):
                print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])

        # Get categories
        print("\n\n=== Categories ===")
        cats = page.query_selector_all("a[href*='/businesses/category/']")
        seen = set()
        for c in cats:
            text = c.inner_text().strip()
            href = c.get_attribute("href") or ""
            if text and text not in seen and "See more" not in text and "Filters" not in text:
                seen.add(text)
                print(f"  {text} -> {href}")

        # Get business links
        print("\n\n=== Business links ===")
        links = page.query_selector_all("a[href*='/businesses/']")
        biz = []
        for l in links:
            href = l.get_attribute("href") or ""
            text = l.inner_text().strip()
            if "/category/" not in href and href not in [b["href"] for b in biz]:
                biz.append({"href": href, "text": text})
        for b in biz[:10]:
            print(f"  {b['href']} -> {b['text']}")

        # Test detail page
        if biz:
            detail = "https://www.connectnigeria.com" + biz[0]["href"]
            print(f"\n\n=== Detail: {detail} ===")

            api2 = []
            page2 = context.new_page()
            def handle_response2(response):
                if "api.connectnigeria.com/api" in response.url:
                    try:
                        data = response.json()
                        api2.append({"url": response.url, "data": data})
                    except:
                        pass
            page2.on("response", handle_response2)

            page2.goto(detail, wait_until="domcontentloaded", timeout=60000)
            page2.wait_for_timeout(5000)

            for r in api2:
                print(f"\n--- {r['url'][:150]} ---")
                print(json.dumps(r["data"], indent=2, ensure_ascii=False)[:3000])

            body = page2.inner_text("body")
            print(f"\n\nPage text:\n{body[:2000]}")

        browser.close()

if __name__ == "__main__":
    test_api()
