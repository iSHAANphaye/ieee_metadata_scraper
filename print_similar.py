import json
from playwright.sync_api import sync_playwright

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
        # Wait for the page JS to load
        page.wait_for_timeout(3000)
        
        # Now fetch /similar via page.evaluate
        print("Evaluating fetch('/rest/document/4270034/similar')...")
        try:
            similar_data = page.evaluate("""
                fetch('/rest/document/4270034/similar')
                    .then(response => response.json())
            """)
            with open("similar.json", "w", encoding="utf-8") as f:
                json.dump(similar_data, f, indent=4)
            print("Successfully saved similar.json!")
            if isinstance(similar_data, list):
                print("List length:", len(similar_data))
                if len(similar_data) > 0:
                    print("Sample item:", similar_data[0])
            elif isinstance(similar_data, dict):
                print("Keys:", list(similar_data.keys()))
                if "records" in similar_data:
                    records = similar_data["records"]
                    print("Records count:", len(records))
                    if len(records) > 0:
                        print("Sample record keys:", list(records[0].keys()))
                        print("Sample record title:", records[0].get("title"))
                        print("Sample record docID:", records[0].get("articleNumber"))
        except Exception as e:
            print("Failed to fetch /similar:", e)
            
        # Now fetch /toc via page.evaluate
        print("Evaluating fetch('/rest/document/4270034/toc')...")
        try:
            toc_data = page.evaluate("""
                fetch('/rest/document/4270034/toc')
                    .then(response => response.json())
            """)
            with open("toc.json", "w", encoding="utf-8") as f:
                json.dump(toc_data, f, indent=4)
            print("Successfully saved toc.json!")
            if isinstance(toc_data, dict):
                print("Keys:", list(toc_data.keys()))
                for k, v in toc_data.items():
                    print(f"Key: {k} | Value preview: {str(v)[:150]}")
        except Exception as e:
            print("Failed to fetch /toc:", e)
            
        browser.close()

if __name__ == "__main__":
    main()
