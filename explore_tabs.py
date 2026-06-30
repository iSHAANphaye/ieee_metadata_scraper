from playwright.sync_api import sync_playwright

def main():
    url = "https://ieeexplore.ieee.org/document/4270034"
    print(f"Loading {url} and clicking tabs to intercept XHR/fetch requests...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Intercept network responses
        responses = {}
        def handle_response(response):
            if "rest/document" in response.url or "api" in response.url:
                try:
                    status = response.status
                    if status == 200:
                        responses[response.url] = response.text()
                        print(f"[XHR/Fetch] Captured: {response.url}")
                except Exception:
                    pass
        
        page.on("response", handle_response)
        
        # Visit main page
        page.goto(url, wait_until="load")
        page.wait_for_timeout(2000)
        
        # Look for references tab/button and click it
        print("Attempting to find and click References tab...")
        try:
            # We can search for buttons or links containing "References"
            ref_button = page.locator("a:has-text('References'), button:has-text('References'), li:has-text('References')").first
            if ref_button.count() > 0:
                print("Found References button. Clicking...")
                ref_button.click()
                page.wait_for_timeout(3000)
            else:
                print("References button not found by text search.")
        except Exception as e:
            print("Error clicking References:", e)

        # Look for Citations tab/button and click it
        print("Attempting to find and click Citations tab...")
        try:
            cit_button = page.locator("a:has-text('Citations'), button:has-text('Citations'), li:has-text('Citations')").first
            if cit_button.count() > 0:
                print("Found Citations button. Clicking...")
                cit_button.click()
                page.wait_for_timeout(3000)
            else:
                print("Citations button not found by text search.")
        except Exception as e:
            print("Error clicking Citations:", e)
            
        print("\n=== Intercepted URL Results ===")
        for req_url in responses.keys():
            print(f"-> {req_url}")
            # Save a snippet of the JSON if it contains citations or references or similar
            if "similar" in req_url or "references" in req_url or "citations" in req_url or "citedby" in req_url:
                # Try to pretty print keys of JSON
                try:
                    data = json.loads(responses[req_url])
                    import json
                    print(f"JSON Keys for {req_url.split('/')[-1]}:", list(data.keys()) if isinstance(data, dict) else f"List of length {len(data)}")
                except Exception:
                    print("Could not parse as JSON.")
                    
        # Let's save the JSON responses to local files for inspection
        import json
        for req_url, content in responses.items():
            name = req_url.split("/")[-1].split("?")[0]
            try:
                data = json.loads(content)
                with open(f"{name}_endpoint.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print(f"Saved {name}_endpoint.json")
            except Exception:
                pass
                
        browser.close()

if __name__ == "__main__":
    import json
    main()
