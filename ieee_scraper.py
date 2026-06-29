import os
import re
import sys
import json
import argparse
import time
from playwright.sync_api import sync_playwright

def clean_url(url):
    """Clean and validate IEEE Xplore URL."""
    url = url.strip()
    if not url:
        return None
    # Ensure it starts with http/https
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    # Check if it's a valid document link
    if 'ieeexplore.ieee.org/document/' not in url:
        # Try to extract a document ID if only an ID was provided
        match = re.search(r'\d+', url)
        if match:
            doc_id = match.group(0)
            url = f"https://ieeexplore.ieee.org/document/{doc_id}"
            print(f"-> Normalized URL to: {url}")
        else:
            print(f"Warning: URL '{url}' does not seem to be a valid IEEE Xplore document link. Skipping.")
            return None
    return url

def extract_metadata_from_html(html):
    """Extract and parse xplGlobal.document.metadata JSON from page HTML."""
    if "xplGlobal.document.metadata" not in html:
        return None
    
    try:
        start_idx = html.find("xplGlobal.document.metadata")
        brace_idx = html.find("{", start_idx)
        if brace_idx != -1:
            metadata, _ = json.JSONDecoder().raw_decode(html[brace_idx:])
            return metadata
    except Exception as e:
        print(f"Error parsing metadata JSON: {e}")
    return None

def scrape_paper(page, url):
    """Scrape a single IEEE paper URL using Playwright."""
    print(f"\nProcessing: {url}")
    try:
        # Load page with 30s timeout
        response = page.goto(url, wait_until="load", timeout=30000)
        
        # Check initial response status
        status = response.status if response else "No response"
        if status == 202:
            print("AWS WAF challenge detected. Waiting for auto-reload...")
        
        # Poll for the metadata script to be loaded and parsed
        metadata = None
        max_attempts = 30  # 15 seconds max wait
        for attempt in range(max_attempts):
            try:
                html = page.content()
                metadata = extract_metadata_from_html(html)
                if metadata and metadata.get("title"):
                    break
            except Exception:
                # Page might be navigating/reloading; suppress error and retry
                pass
            page.wait_for_timeout(500)
        
        if not metadata:
            print("Failed to load metadata. Page might have blocked access or did not render correctly.")
            return None
        
        # Extract title
        title = metadata.get("title") or metadata.get("displayDocTitle") or "Unknown Title"
        
        # Extract abstract
        abstract = metadata.get("abstract") or "No abstract available."
        
        # Extract authors
        authors_list = metadata.get("authors", [])
        authors = [a.get("name") for a in authors_list if a.get("name")]
        authors_str = ", ".join(authors) if authors else "Unknown Authors"
        
        # Extract publication details
        pub_year = metadata.get("publicationYear") or "Unknown Year"
        doi = metadata.get("doi") or "No DOI available"
        
        # Extract keywords
        keywords_data = metadata.get("keywords", [])
        keywords_dict = {}
        for item in keywords_data:
            k_type = item.get("type", "Other Keywords")
            k_list = item.get("kwd", [])
            if k_list:
                keywords_dict[k_type] = k_list
                
        paper_info = {
            "url": url,
            "title": title,
            "authors": authors_str,
            "year": pub_year,
            "doi": doi,
            "abstract": abstract,
            "keywords": keywords_dict
        }
        
        print(f"Successfully scraped: \"{title}\"")
        return paper_info
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def save_to_markdown(papers, filepath, append=False):
    """Save scraped papers metadata as a Markdown file."""
    file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0
    mode = "a" if (append and file_exists) else "w"
    
    with open(filepath, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# IEEE Xplore Papers Metadata\n\n")
            f.write(f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            start_num = 1
        else:
            # Count existing papers to continue numbering
            # A paper entry title is represented as "## <number>. <title>"
            start_num = 1
            try:
                with open(filepath, "r", encoding="utf-8") as rf:
                    content = rf.read()
                    matches = re.findall(r"^## (\d+)\.", content, re.MULTILINE)
                    if matches:
                        start_num = int(matches[-1]) + 1
            except Exception:
                pass
            f.write("\n")  # Add extra space before new entries
            
        for idx, paper in enumerate(papers, start_num):
            if mode == "w" or idx > start_num:
                f.write("---\n\n")
            f.write(f"## {idx}. {paper['title']}\n")
            f.write(f"- **URL**: {paper['url']}\n")
            f.write(f"- **Authors**: {paper['authors']}\n")
            f.write(f"- **Publication Year**: {paper['year']}\n")
            f.write(f"- **DOI**: {paper['doi']}\n\n")
            
            f.write("### Abstract\n")
            f.write(f"{paper['abstract']}\n\n")
            
            f.write("### Keywords\n")
            if paper['keywords']:
                for k_type, k_list in paper['keywords'].items():
                    keywords_str = ", ".join(k_list)
                    f.write(f"- **{k_type}**: {keywords_str}\n")
            else:
                f.write("*No keywords available.*\n")
            f.write("\n")
            
        f.write("---\n")
    
    action_verb = "Appended" if mode == "a" else "Saved"
    print(f"\n{action_verb} metadata for {len(papers)} paper(s) to: {os.path.abspath(filepath)}")

def save_to_json(papers, filepath, append=False):
    """Save scraped papers metadata as a JSON file."""
    file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0
    existing_papers = []
    
    if append and file_exists:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing_papers = json.load(f)
                if not isinstance(existing_papers, list):
                    existing_papers = [existing_papers]
        except Exception as e:
            print(f"Warning: Could not read existing JSON for appending: {e}. Overwriting instead.")
            
    all_papers = existing_papers + papers
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_papers, f, indent=4, ensure_ascii=False)
        
    action_verb = "Appended" if (append and file_exists) else "Saved"
    print(f"\n{action_verb} metadata for {len(papers)} paper(s) to: {os.path.abspath(filepath)}")

def main():
    parser = argparse.ArgumentParser(description="Scrape paper metadata (Title, Abstract, Keywords) from IEEE Xplore.")
    parser.add_argument("--urls", type=str, help="Comma-separated list of IEEE Xplore URLs.")
    parser.add_argument("--file", type=str, help="Path to a text file containing IEEE Xplore URLs (one per line).")
    parser.add_argument("--output", type=str, default="papers_metadata.md", help="Output file path (default: papers_metadata.md).")
    parser.add_argument("--format", type=str, choices=["markdown", "json"], default="markdown", help="Output file format (markdown or json).")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay in seconds between requests (default: 2.0).")
    parser.add_argument("--append", "-a", action="store_true", help="Append papers to the output file instead of overwriting it.")
    
    args = parser.parse_args()
    
    urls_to_process = []
    
    # 1. Parse command line urls if given
    if args.urls:
        urls_to_process.extend([u.strip() for u in args.urls.split(",") if u.strip()])
    
    # 2. Parse file if given
    if args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8") as f:
                urls_to_process.extend([line.strip() for line in f if line.strip()])
        else:
            print(f"Error: URL file not found at '{args.file}'")
            sys.exit(1)
            
    # 3. Interactive fallback if no input provided
    if not urls_to_process:
        print("No URLs provided via --urls or --file.")
        choice = input("Enter IEEE Xplore URL(s) (comma-separated) or path to a text file containing them: ").strip()
        if os.path.exists(choice):
            with open(choice, "r", encoding="utf-8") as f:
                urls_to_process.extend([line.strip() for line in f if line.strip()])
        else:
            urls_to_process.extend([u.strip() for u in choice.split(",") if u.strip()])
            
    # Filter and clean URLs
    valid_urls = []
    for url in urls_to_process:
        cleaned = clean_url(url)
        if cleaned:
            valid_urls.append(cleaned)
            
    if not valid_urls:
        print("No valid IEEE Xplore URLs to process.")
        sys.exit(1)
        
    print(f"Starting scraper for {len(valid_urls)} URL(s)...")
    
    scraped_papers = []
    
    with sync_playwright() as p:
        # Launch chromium in headless mode
        browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
        # Use standard user agent to bypass WAF
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for idx, url in enumerate(valid_urls):
            if idx > 0:
                print(f"Waiting {args.delay} seconds before next request...")
                time.sleep(args.delay)
                
            paper_info = scrape_paper(page, url)
            if paper_info:
                scraped_papers.append(paper_info)
                
        browser.close()
        
    if scraped_papers:
        # Set format output based on extension if overridden in output filename
        fmt = args.format
        if args.output.endswith(".json"):
            fmt = "json"
        elif args.output.endswith(".md") or args.output.endswith(".markdown"):
            fmt = "markdown"
            
        if fmt == "json":
            save_to_json(scraped_papers, args.output, append=args.append)
        else:
            save_to_markdown(scraped_papers, args.output, append=args.append)
    else:
        print("\nNo papers were successfully scraped.")

if __name__ == "__main__":
    main()
