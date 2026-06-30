import json
from playwright.sync_api import sync_playwright

def main():
    url = "https://ieeexplore.ieee.org/document/4270034"
    refs_url = "https://ieeexplore.ieee.org/rest/document/4270034/references"
    citedby_url = "https://ieeexplore.ieee.org/rest/document/4270034/toc"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("Visiting main page to clear WAF...")
        page.goto(url, wait_until="load")
        page.wait_for_timeout(2000)  # Wait a bit
        
        print("Fetching references endpoint...")
        try:
            page.goto(refs_url, wait_until="load")
            content = page.locator("body").inner_text()
            print("References response length:", len(content))
            print("References content preview (first 1000 chars):")
            print(content[:1000])
            # Save it to check format
            try:
                data = json.loads(content)
                with open("refs_sample.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print("Saved references to refs_sample.json")
            except Exception as e:
                print("Failed to parse references as JSON:", e)
        except Exception as e:
            print("Error loading references:", e)
            
        print("\nFetching TOC endpoint...")
        try:
            page.goto(citedby_url, wait_until="load")
            content = page.locator("body").inner_text()
            print("TOC response length:", len(content))
            print("TOC content preview:")
            print(content[:1000])
            try:
                data = json.loads(content)
                with open("toc_sample.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print("Saved TOC to toc_sample.json")
            except Exception as e:
                print("Failed to parse TOC as JSON:", e)
        except Exception as e:
            print("Error loading TOC:", e)
            
        browser.close()

if __name__ == "__main__":
    main()
