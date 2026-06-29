import json
import re
from playwright.sync_api import sync_playwright

def main():
    url = "https://ieeexplore.ieee.org/document/4270034"
    print(f"Navigating to {url} using Playwright...")

    with sync_playwright() as p:
        # Launch browser. We can try headless first. If WAF blocks headless, we'll try headed.
        # Often headless is fine if we wait, or we can use stealth headers.
        browser = p.chromium.launch(headless=True)
        # Create a new context with a standard browser user agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Navigate to the page
        print("Loading page...")
        response = page.goto(url)
        print("Status code:", response.status if response else "No response")
        
        # Wait for the page to load or challenge to be solved
        print("Waiting for page load and network idle...")
        page.wait_for_load_state("networkidle")
        
        # Take a screenshot to verify what it sees (headless debugging)
        page.screenshot(path="screenshot.png")
        print("Screenshot saved to screenshot.png")
        
        # Get page title
        print("Page Title in browser:", page.title())
        
        # Let's check the page source for global.document.metadata
        html = page.content()
        print("HTML length:", len(html))
        
        # Look for global.document.metadata in script tags
        # Using BeautifulSoup to extract script contents
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')
        
        metadata_found = False
        for script in scripts:
            if script.string and "global.document.metadata" in script.string:
                print("Found global.document.metadata script block!")
                # Search for the object assignment
                # Format is usually: global.document.metadata={...};
                match = re.search(r"global\.document\.metadata\s*=\s*(\{.*?\});", script.string, re.DOTALL)
                if match:
                    metadata_str = match.group(1)
                    try:
                        metadata = json.loads(metadata_str)
                        print("Successfully parsed metadata JSON!")
                        print("Keys in metadata:", list(metadata.keys()))
                        # Save metadata JSON to verify structure
                        with open("metadata_sample.json", "w", encoding="utf-8") as f:
                            json.dump(metadata, f, indent=4)
                        print("Saved metadata to metadata_sample.json")
                        metadata_found = True
                        break
                    except Exception as e:
                        print("Error parsing JSON:", e)
                        # Print a snippet of the matched group
                        print("Matched string preview:", metadata_str[:500])
                else:
                    print("Regex match failed on script string.")
                    print("Script content preview:", script.string[:500])

        if not metadata_found:
            print("Could not find global.document.metadata script block.")
            # Let's save a snippet of the HTML body to see what is loaded
            body_text = soup.body.get_text() if soup.body else ""
            print("Body text preview:")
            print(body_text[:1000])
            with open("raw_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved raw HTML to raw_page.html")
            
        browser.close()

if __name__ == "__main__":
    main()
