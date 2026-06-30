from playwright.sync_api import sync_playwright

def main():
    url = "https://ieeexplore.ieee.org/document/4270034"
    print(f"Loading {url} and intercepting XHR/fetch requests...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Intercept network responses
        responses = []
        def handle_response(response):
            if "rest/document" in response.url or "api" in response.url or response.request.resource_type in ["xhr", "fetch"]:
                try:
                    status = response.status
                    size = len(response.body()) if status == 200 else 0
                    print(f"[XHR/Fetch] URL: {response.url} | Status: {status} | Size: {size}")
                    responses.append((response.url, status, response.text()))
                except Exception:
                    pass
        
        page.on("response", handle_response)
        
        page.goto(url, wait_until="load")
        
        # Wait a bit for all AJAX calls to complete
        print("Waiting for network idle...")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        
        print("\nAll intercepted requests:")
        for url, status, text in responses:
            if "references" in url.lower() or "citation" in url.lower():
                print(f"-> MATCHED: {url} | Status: {status}")
                # Print a snippet of the text
                print("Text preview:", text[:500])
                
        browser.close()

if __name__ == "__main__":
    main()
