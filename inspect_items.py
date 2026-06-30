from playwright.sync_api import sync_playwright
import json

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
        
        # Fetch references
        print("Fetching /references...")
        try:
            refs_data = page.evaluate("fetch('/rest/document/4270034/references').then(r => r.json())")
            refs = refs_data.get("references", [])
            print("Total references:", len(refs))
            if len(refs) > 0:
                print("First reference keys:", list(refs[0].keys()))
                print("First reference details:")
                for k, v in refs[0].items():
                    print(f"  {k}: {v}")
                # Print references that have links or articleNumbers
                linked_refs = [r for r in refs if r.get("links")]
                print("References with links:", len(linked_refs))
                if len(linked_refs) > 0:
                    print("Sample linked reference:", linked_refs[0])
        except Exception as e:
            print("Error parsing references:", e)
            
        # Fetch citations
        print("\nFetching /citations...")
        try:
            cit_data = page.evaluate("fetch('/rest/document/4270034/citations').then(r => r.json())")
            paper_cit = cit_data.get("paperCitations", {})
            print("Paper citations groups:", list(paper_cit.keys()))
            ieee_cits = paper_cit.get("ieee", [])
            print("Total IEEE citations:", len(ieee_cits))
            if len(ieee_cits) > 0:
                print("First IEEE citation keys:", list(ieee_cits[0].keys()))
                print("First IEEE citation details:")
                for k, v in ieee_cits[0].items():
                    print(f"  {k}: {v}")
                # Print citations with links
                linked_cits = [c for c in ieee_cits if c.get("links")]
                print("Citations with links:", len(linked_cits))
                if len(linked_cits) > 0:
                    print("Sample linked citation:", linked_cits[0])
        except Exception as e:
            print("Error parsing citations:", e)
            
        browser.close()

if __name__ == "__main__":
    main()
