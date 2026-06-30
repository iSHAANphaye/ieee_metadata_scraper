from playwright.sync_api import sync_playwright
import json

def test_fetch(page, endpoint):
    print(f"Testing fetch({endpoint})...")
    try:
        data = page.evaluate(f"""
            fetch('{endpoint}')
                .then(r => r.ok ? r.json() : {{error: 'Status ' + r.status}})
                .catch(e => ({{error: e.message}}))
        """)
        if "error" in data:
            print(f"  Result: Error - {data['error']}")
        else:
            print(f"  Result: Success! Keys: {list(data.keys()) if isinstance(data, dict) else 'List of ' + str(len(data))}")
            if isinstance(data, dict):
                for k, v in data.items():
                    print(f"    Key: {k} | Type: {type(v)} | Preview: {str(v)[:100]}")
            return data
    except Exception as e:
        print(f"  Result: Exception - {e}")
    return None

def main():
    url = "https://ieeexplore.ieee.org/document/4270034"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("Visiting main page to clear WAF...")
        page.goto(url, wait_until="load")
        page.wait_for_timeout(3000)
        
        # Test endpoints
        endpoints = [
            "/rest/document/4270034/references",
            "/rest/document/4270034/citations",
            "/rest/document/4270034/citedby",
            "/rest/document/4270034/referencedby"
        ]
        
        for ep in endpoints:
            test_fetch(page, ep)
            
        browser.close()

if __name__ == "__main__":
    main()
