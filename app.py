import os
import json
import time
import re
from flask import Flask, render_template, request, jsonify, Response, session
from playwright.sync_api import sync_playwright

# Import scraper helper functions
from ieee_scraper import clean_url, scrape_paper, fetch_connected_papers

# Import database methods
from db import get_cached_paper, cache_paper, register_user, authenticate_user

app = Flask(__name__)
# Configure secure sessions
app.secret_key = os.getenv("SECRET_KEY", "paper_scraper_secure_session_key_987654321")

def get_significant_words(text):
    if not text:
        return set()
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of', 'is', 'are', 'was', 'were', 'that', 'this', 'these', 'those', 'based', 'using', 'proposed', 'method', 'paper', 'results', 'experimental', 'analysis'}
    words = re.findall(r'\b\w{3,}\b', text.lower())
    return set(words) - stopwords

def calculate_similarity(paper_a, paper_b):
    # 1. Keyword overlap
    keywords_a = set()
    for kw_list in paper_a.get("keywords", {}).values():
        if isinstance(kw_list, list):
            keywords_a.update(k.strip().lower() for k in kw_list)
            
    keywords_b = set()
    for kw_list in paper_b.get("keywords", {}).values():
        if isinstance(kw_list, list):
            keywords_b.update(k.strip().lower() for k in kw_list)
            
    kw_jaccard = 0.0
    if keywords_a or keywords_b:
        kw_jaccard = len(keywords_a.intersection(keywords_b)) / len(keywords_a.union(keywords_b))
        
    # 2. Title & Abstract word-level overlap
    text_a = get_significant_words(paper_a.get("title", "")) | get_significant_words(paper_a.get("abstract", ""))
    text_b = get_significant_words(paper_b.get("title", "")) | get_significant_words(paper_b.get("abstract", ""))
    
    text_jaccard = 0.0
    if text_a or text_b:
        text_jaccard = len(text_a.intersection(text_b)) / len(text_a.union(text_b))
        
    # 3. Composite score (70% keywords, 30% text overlap)
    score = (0.7 * kw_jaccard) + (0.3 * text_jaccard)
    shared_kws = list(keywords_a.intersection(keywords_b))
    
    return round(score * 100, 1), shared_kws

def clean_mongo_doc(doc):
    if not doc:
        return doc
    doc = dict(doc)
    doc.pop("_id", None)
    if "scraped_at" in doc and doc["scraped_at"]:
        from datetime import datetime, timedelta
        if isinstance(doc["scraped_at"], datetime):
            ist_time = doc["scraped_at"] + timedelta(hours=5, minutes=30)
            doc["scraped_at"] = ist_time.strftime("%d-%m-%Y %I:%M:%S %p IST")
    return doc

# Helper to extract IEEE Xplore article number from URL
def extract_article_number(url):
    if not url:
        return None
    # Match /document/(\d+) or arnumber=(\d+)
    match = re.search(r'/document/(\d+)', url)
    if match:
        return match.group(1)
    match = re.search(r'arnumber=(\d+)', url)
    if match:
        return match.group(1)
    return None

# Helper to verify auth status
def is_authenticated():
    return "user" in session

# --- Authentication Endpoints ---

@app.route("/auth-status", methods=["GET"])
def auth_status():
    if is_authenticated():
        return jsonify({"authenticated": True, "email": session["user"]})
    return jsonify({"authenticated": False})

@app.route("/signup", methods=["POST"])
def do_signup():
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
        
    success, message = register_user(email, password)
    if success:
        session["user"] = email.lower() # Auto-login after signup
        return jsonify({"success": True, "message": message})
    return jsonify({"error": message}), 400

@app.route("/login", methods=["POST"])
def do_login():
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
        
    success, message = authenticate_user(email, password)
    if success:
        session["user"] = email.lower()
        return jsonify({"success": True, "message": message})
    return jsonify({"error": message}), 400

@app.route("/logout", methods=["POST", "GET"])
def do_logout():
    session.pop("user", None)
    return jsonify({"success": True, "message": "Successfully logged out."})

@app.route("/delete-account", methods=["POST"])
def delete_account():
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
    
    email = session["user"]
    from db import delete_user_data
    success, message = delete_user_data(email)
    if success:
        session.pop("user", None)
        return jsonify({"success": True, "message": message})
    return jsonify({"error": message}), 500

@app.route("/history", methods=["GET"])
def get_history():
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
    
    from db import get_papers_col
    col = get_papers_col()
    if col is None:
        return jsonify({"error": "Database not available"}), 500
        
    try:
        cursor = col.find({"scraped_by": session["user"]}).sort("scraped_at", -1)
        papers = []
        from datetime import timedelta
        for doc in cursor:
            doc["articleNumber"] = doc["_id"]
            if doc.get("scraped_at"):
                ist_time = doc["scraped_at"] + timedelta(hours=5, minutes=30)
                doc["scraped_at"] = ist_time.strftime("%d-%m-%Y %I:%M:%S %p IST")
            doc.pop("_id", None)
            papers.append(doc)
        return jsonify({"success": True, "data": papers})
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve history: {str(e)}"}), 500

@app.route("/history/delete/<art_num>", methods=["DELETE"])
def delete_history_item(art_num):
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
        
    from db import get_papers_col
    col = get_papers_col()
    if col is None:
        return jsonify({"error": "Database not available"}), 500
        
    try:
        res = col.delete_one({"_id": str(art_num), "scraped_by": session["user"]})
        if res.deleted_count > 0:
            return jsonify({"success": True, "message": "Item deleted from history."})
        return jsonify({"error": "Item not found or unauthorized."}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to delete item: {str(e)}"}), 500


@app.route("/recommend-local/<art_num>", methods=["GET"])
def recommend_local(art_num):
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
        
    from db import get_papers_col
    col = get_papers_col()
    if col is None:
        return jsonify({"error": "Database not available"}), 500
        
    try:
        target = col.find_one({"_id": str(art_num), "scraped_by": session["user"]})
        if not target:
            return jsonify({"error": "Target paper not found in cache."}), 404
            
        cursor = col.find({"_id": {"$ne": str(art_num)}, "scraped_by": session["user"]})
        
        matches = []
        for paper in cursor:
            score, shared_kws = calculate_similarity(target, paper)
            if score > 0:
                paper["articleNumber"] = paper["_id"]
                paper.pop("_id", None)
                if paper.get("scraped_at"):
                    paper["scraped_at"] = paper["scraped_at"].strftime("%d-%m-%Y %I:%M:%S %p IST")
                matches.append({
                    "paper": paper,
                    "score": score,
                    "shared_keywords": shared_kws
                })
                
        matches.sort(key=lambda x: x["score"], reverse=True)
        return jsonify({"success": True, "data": matches})
    except Exception as e:
        return jsonify({"error": f"Failed to compute recommendations: {str(e)}"}), 500


@app.route("/search-similar-ieee/<art_num>", methods=["GET"])
def search_similar_ieee(art_num):
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
        
    from db import get_papers_col
    col = get_papers_col()
    if col is None:
        return jsonify({"error": "Database not available"}), 500
        
    try:
        target = col.find_one({"_id": str(art_num), "scraped_by": session["user"]})
        if not target:
            return jsonify({"error": "Target paper not found in cache."}), 404
            
        kws = []
        for kw_list in target.get("keywords", {}).values():
            if isinstance(kw_list, list):
                kws.extend(kw_list)
        
        unique_kws = []
        for k in kws:
            k_clean = k.strip()
            if k_clean and k_clean not in unique_kws:
                unique_kws.append(k_clean)
                
        if len(unique_kws) > 3:
            unique_kws = unique_kws[:3]
            
        if not unique_kws:
            title = target.get("title", "")
            words = [w for w in re.findall(r'\b\w{4,}\b', title) if w.lower() not in {'image', 'using', 'based', 'paper', 'system', 'method', 'analysis', 'study', 'model'}]
            unique_kws = words[:3]
            
        if not unique_kws:
            return jsonify({"success": True, "data": []})
            
        query_text = " AND ".join(f'"{kw}"' for kw in unique_kws)
        print(f"Executing IEEE search similarity query: {query_text}")
        
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            page.goto(target["url"])
            page.wait_for_function("typeof xplGlobal !== 'undefined'", timeout=15000)
            
            js_code = """
            (async () => {
                const res = await fetch('https://ieeexplore.ieee.org/rest/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ queryText: %s, rowsPerPage: 15, pageNumber: 1 })
                });
                return await res.json();
            })()
            """ % json.dumps(query_text)
            
            search_result = page.evaluate(js_code)
            browser.close()
            
        target_title_words = get_significant_words(target.get("title", ""))
        target_abstract_words = get_significant_words(target.get("abstract", ""))
        target_all_words = target_title_words | target_abstract_words
        
        records = search_result.get("records", [])
        results = []
        for rec in records:
            art_id = rec.get("articleNumber")
            doc_link = rec.get("documentLink")
            
            if str(art_id) == str(art_num):
                continue
                
            auths = []
            for a in rec.get("authors", []):
                name = a.get("preferredName")
                if name:
                    auths.append(name)
            authors_str = ", ".join(auths) if auths else "Unknown Authors"
            
            # Compute text similarity metrics with concept matching and calibration
            rec_title_words = get_significant_words(rec.get("articleTitle", ""))
            rec_abstract_words = get_significant_words(rec.get("abstract", ""))
            rec_all_words = rec_title_words | rec_abstract_words
            
            title_overlap = len(target_title_words.intersection(rec_title_words))
            title_score = title_overlap / len(target_title_words) if target_title_words else 0.0
            
            concept_overlap = len(target_title_words.intersection(rec_all_words))
            concept_score = concept_overlap / len(target_title_words) if target_title_words else 0.0
            
            jaccard_overlap = len(target_all_words.intersection(rec_all_words))
            jaccard_union = len(target_all_words.union(rec_all_words))
            jaccard_score = jaccard_overlap / jaccard_union if jaccard_union else 0.0
            
            # Weighted formula: Title match (45%), Concept presence (45%), Abstract text overlap (10%)
            raw_score = (0.45 * title_score) + (0.45 * concept_score) + (0.10 * jaccard_score)
            
            # Calibrate using square root (0.5 power) to scale scores to a friendly 60-70%+ range
            match_percentage = min(98.0, round((raw_score ** 0.5) * 100, 1))
            shared_terms = sorted(list(target_all_words.intersection(rec_all_words)))
            
            results.append({
                "title": rec.get("articleTitle") or "Untitled Paper",
                "authors": authors_str,
                "year": rec.get("publicationYear") or "Unknown Year",
                "articleNumber": art_id,
                "url": f"https://ieeexplore.ieee.org{doc_link}" if doc_link else (f"https://ieeexplore.ieee.org/document/{art_id}" if art_id else None),
                "scrapable": bool(art_id),
                "matchScore": match_percentage,
                "sharedTerms": shared_terms
            })
            
        # Sort results by matchScore descending
        results.sort(key=lambda x: x["matchScore"], reverse=True)
            
        return jsonify({"success": True, "data": results, "query": query_text})
    except Exception as e:
        return jsonify({"error": f"Failed to search similar papers on IEEE: {str(e)}"}), 500


@app.route("/search-by-keywords", methods=["POST"])
def search_by_keywords():
    if not is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json or {}
    raw_query = data.get("queryText", "").strip()
    active_art_num = data.get("activeArticleNumber")
    if not raw_query:
        return jsonify({"error": "Query keywords are required."}), 400
        
    # Split by commas or newlines first to extract individual keyword phrases
    parts = re.split(r'[\n\r,]+', raw_query)
    keywords = []
    for part in parts:
        part_clean = part.strip()
        if not part_clean:
            continue
        # Wrap multi-word phrases in quotes to preserve exact phrase match in IEEE Xplore
        if ' ' in part_clean and not (part_clean.startswith('"') and part_clean.endswith('"')):
            part_clean = f'"{part_clean}"'
        keywords.append(part_clean)
        
    # If no commas or newlines, split by spaces
    if len(keywords) == 1 and not (raw_query.startswith('"') and raw_query.endswith('"')):
        space_parts = [p.strip() for p in raw_query.split(' ') if p.strip()]
        if len(space_parts) > 1:
            keywords = space_parts
            
    query_text = " AND ".join(keywords)
    if not query_text:
        return jsonify({"error": "Valid query keywords are required."}), 400
        
    try:
        # Determine target paper or query text words for similarity comparison
        target = None
        if active_art_num:
            from db import get_papers_col
            col = get_papers_col()
            if col is not None:
                target = col.find_one({"_id": str(active_art_num), "scraped_by": session["user"]})
                
        if target:
            target_title_words = get_significant_words(target.get("title", ""))
            target_abstract_words = get_significant_words(target.get("abstract", ""))
            target_all_words = target_title_words | target_abstract_words
        else:
            # Fallback: compare against query keywords themselves!
            target_title_words = get_significant_words(query_text)
            target_abstract_words = set()
            target_all_words = target_title_words
            
        print(f"Executing IEEE keyword search: {query_text}")
        
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Navigate to search page or a dummy page on same domain to handle cookie/WAF setup
            page.goto("https://ieeexplore.ieee.org")
            page.wait_for_timeout(2000)
            
            js_code = """
            (async () => {
                const res = await fetch('https://ieeexplore.ieee.org/rest/search', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json, text/plain, */*',
                        'X-Security-Request': 'required'
                    },
                    body: JSON.stringify({ 
                        queryText: %s, 
                        highlight: true, 
                        returnFacets: ["ALL"], 
                        returnType: "SEARCH", 
                        rowsPerPage: 15, 
                        pageNumber: 1 
                    })
                });
                return await res.json();
            })()
            """ % json.dumps(query_text)
            
            search_result = page.evaluate(js_code)
            browser.close()
            
        records = search_result.get("records", [])
        results = []
        for rec in records:
            art_id = rec.get("articleNumber")
            doc_link = rec.get("documentLink")
            
            if active_art_num and str(art_id) == str(active_art_num):
                continue
                
            auths = []
            for a in rec.get("authors", []):
                name = a.get("preferredName")
                if name:
                    auths.append(name)
            authors_str = ", ".join(auths) if auths else "Unknown Authors"
            
            # Compute text similarity metrics with concept matching and calibration
            rec_title_words = get_significant_words(rec.get("articleTitle", ""))
            rec_abstract_words = get_significant_words(rec.get("abstract", ""))
            rec_all_words = rec_title_words | rec_abstract_words
            
            title_overlap = len(target_title_words.intersection(rec_title_words))
            title_score = title_overlap / len(target_title_words) if target_title_words else 0.0
            
            concept_overlap = len(target_title_words.intersection(rec_all_words))
            concept_score = concept_overlap / len(target_title_words) if target_title_words else 0.0
            
            jaccard_overlap = len(target_all_words.intersection(rec_all_words))
            jaccard_union = len(target_all_words.union(rec_all_words))
            jaccard_score = jaccard_overlap / jaccard_union if jaccard_union else 0.0
            
            # Weighted formula: Title match (45%), Concept presence (45%), Abstract text overlap (10%)
            raw_score = (0.45 * title_score) + (0.45 * concept_score) + (0.10 * jaccard_score)
            
            # Calibrate using square root (0.5 power) to scale scores to a friendly 60-70%+ range
            match_percentage = min(98.0, round((raw_score ** 0.5) * 100, 1))
            shared_terms = sorted(list(target_all_words.intersection(rec_all_words)))
            
            results.append({
                "title": rec.get("articleTitle") or "Untitled Paper",
                "authors": authors_str,
                "year": rec.get("publicationYear") or "Unknown Year",
                "articleNumber": art_id,
                "url": f"https://ieeexplore.ieee.org{doc_link}" if doc_link else (f"https://ieeexplore.ieee.org/document/{art_id}" if art_id else None),
                "scrapable": bool(art_id),
                "matchScore": match_percentage,
                "sharedTerms": shared_terms
            })
            
        # Sort results by matchScore descending
        results.sort(key=lambda x: x["matchScore"], reverse=True)
            
        return jsonify({"success": True, "data": results, "query": query_text})
    except Exception as e:
        return jsonify({"error": f"Failed to search papers on IEEE: {str(e)}"}), 500


# --- Scraper & Core Endpoints ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def do_scrape():
    if not is_authenticated():
        return jsonify({"error": "Unauthorized. Please log in first."}), 401
        
    data = request.json or {}
    url_input = data.get("url", "").strip()
    if not url_input:
        return jsonify({"error": "No URL provided."}), 400
        
    cleaned_url = clean_url(url_input)
    if not cleaned_url:
        return jsonify({"error": "Invalid IEEE Xplore URL. Please check the link and try again."}), 400
        
    art_num = extract_article_number(cleaned_url)
    if art_num:
        # Check MongoDB Cache first
        cached = get_cached_paper(art_num)
        if cached:
            print(f"Cache Hit for paper ID: {art_num}")
            # Associate this cached paper with the current user's history registry
            if cached.get("scraped_by") != session["user"]:
                cache_paper(cached, email=session["user"])
                # Reload to get updated document
                cached = get_cached_paper(art_num) or cached
            return jsonify({"success": True, "data": clean_mongo_doc(cached), "cached": True})
            
    # Cache Miss: Scrape via Playwright
    try:
        with sync_playwright() as p:
            # Launch chromium in headless mode with container safety flags
            browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Scrape main paper
            paper_info = scrape_paper(page, cleaned_url)
            
            # If successful, fetch connected papers (references, citations, similar)
            if paper_info and paper_info.get("articleNumber"):
                print("Fetching connected papers...")
                connected = fetch_connected_papers(page, paper_info["articleNumber"])
                paper_info["connected"] = connected
                # Store in MongoDB Cache
                cache_paper(paper_info, email=session["user"])
            else:
                if paper_info:
                    paper_info["connected"] = {"references": [], "citations": [], "similar": []}
            
            browser.close()
            
        if paper_info:
            return jsonify({"success": True, "data": paper_info, "cached": False})
        else:
            return jsonify({"error": "Failed to scrape metadata. Playwright could not bypass WAF or parse the page."}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/scrape-bulk", methods=["POST"])
def do_scrape_bulk():
    if not is_authenticated():
        return jsonify({"error": "Unauthorized. Please log in first."}), 401
        
    data = request.json or {}
    urls = data.get("urls", [])
    delay = data.get("delay", 2.0)
    
    if not urls:
        return jsonify({"error": "No URLs provided for bulk scraping."}), 400
        
    valid_urls = []
    for u in urls:
        cleaned = clean_url(u)
        if cleaned:
            valid_urls.append(cleaned)
            
    if not valid_urls:
        return jsonify({"error": "No valid IEEE Xplore URLs to process."}), 400
        
    scraped_papers = []
    urls_to_scrape = []
    
    # Check MongoDB Cache for each URL
    for url in valid_urls:
        art_num = extract_article_number(url)
        if art_num:
            cached = get_cached_paper(art_num)
            if cached:
                print(f"Cache Hit during bulk: {art_num}")
                scraped_papers.append(clean_mongo_doc(cached))
                continue
        urls_to_scrape.append(url)
        
    # If all requested papers were already cached, return them instantly!
    if not urls_to_scrape:
        return jsonify({"success": True, "data": scraped_papers, "all_cached": True})
        
    # Scrape remaining uncached papers
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Navigate to the first URL normally to resolve cookies and WAF challenge
            first_url = urls_to_scrape[0]
            print(f"Scraping first bulk paper (initiating session): {first_url}")
            paper_info = scrape_paper(page, first_url, fast_mode=False)
            
            if paper_info:
                paper_info["connected"] = {"references": [], "citations": [], "similar": []}
                # Fetch connections list for this subpage to cache it as well
                if paper_info.get("articleNumber"):
                    print("Fetching connected papers for bulk subpage...")
                    connected = fetch_connected_papers(page, paper_info["articleNumber"])
                    paper_info["connected"] = connected
                cache_paper(paper_info, email=session["user"])
                scraped_papers.append(paper_info)
                
            # Scrape remaining subpages using Hybrid AJAX fast_mode=True
            for url in urls_to_scrape[1:]:
                time.sleep(delay)
                print(f"Scraping next bulk paper (fast mode): {url}")
                paper_info = scrape_paper(page, url, fast_mode=True)
                
                if paper_info:
                    paper_info["connected"] = {"references": [], "citations": [], "similar": []}
                    if paper_info.get("articleNumber"):
                        print("Fetching connected papers for bulk subpage...")
                        connected = fetch_connected_papers(page, paper_info["articleNumber"])
                        paper_info["connected"] = connected
                    cache_paper(paper_info, email=session["user"])
                    scraped_papers.append(paper_info)
                    
            browser.close()
            
        return jsonify({"success": True, "data": scraped_papers, "all_cached": False})
    except Exception as e:
        return jsonify({"error": f"An error occurred during bulk scraping: {str(e)}"}), 500

@app.route("/download/markdown", methods=["POST"])
def download_markdown():
    data = request.json or {}
    paper = data.get("paper")
    if not paper:
        return jsonify({"error": "No paper data provided"}), 400
        
    # Generate markdown content
    md = f"# IEEE Xplore Paper Metadata\n\n"
    md += f"## {paper['title']}\n"
    md += f"- **URL**: {paper['url']}\n"
    md += f"- **Authors**: {paper['authors']}\n"
    md += f"- **Publication Year**: {paper['year']}\n"
    md += f"- **DOI**: {paper['doi']}\n\n"
    md += f"### Abstract\n{paper['abstract']}\n\n"
    md += f"### Keywords\n"
    
    if paper.get('keywords'):
        for k_type, k_list in paper['keywords'].items():
            keywords_str = ", ".join(k_list)
            md += f"- **{k_type}**: {keywords_str}\n"
    else:
        md += f"*No keywords available.*\n"
        
    # Create valid filename
    safe_title = "".join([c if c.isalnum() else "_" for c in paper['title'][:30]]).strip("_")
    filename = f"metadata_{safe_title}.md"
    
    return Response(
        md,
        mimetype="text/markdown",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@app.route("/download/combined", methods=["POST"])
def download_combined():
    data = request.json or {}
    papers = data.get("papers", [])
    fmt = data.get("format", "markdown")
    
    if not papers:
        return jsonify({"error": "No papers provided for download."}), 400
        
    if fmt == "json":
        # Stripping MongoDB metadata like _id, scraped_at, scraped_by if present
        cleaned_papers = []
        for p in papers:
            cp = dict(p)
            cp.pop("_id", None)
            cp.pop("scraped_at", None)
            cp.pop("scraped_by", None)
            cleaned_papers.append(cp)
            
        json_content = json.dumps(cleaned_papers, indent=4, ensure_ascii=False)
        return Response(
            json_content,
            mimetype="application/json",
            headers={"Content-disposition": "attachment; filename=scraped_papers.json"}
        )
        
    # Default to markdown
    md = f"# Paper Scraper Metadata Summary\n\n"
    md += f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    for idx, paper in enumerate(papers, 1):
        md += "---\n\n"
        md += f"## {idx}. {paper['title']}\n"
        md += f"- **URL**: {paper['url']}\n"
        md += f"- **Authors**: {paper['authors']}\n"
        md += f"- **Publication Year**: {paper['year']}\n"
        md += f"- **DOI**: {paper['doi']}\n\n"
        
        md += "### Abstract\n"
        md += f"{paper['abstract']}\n\n"
        
        md += "### Keywords\n"
        if paper.get('keywords'):
            for k_type, k_list in paper['keywords'].items():
                keywords_str = ", ".join(k_list)
                md += f"- **{k_type}**: {keywords_str}\n"
        else:
            md += "*No keywords available.*\n"
        md += "\n"
        
    md += "---\n"
    
    return Response(
        md,
        mimetype="text/markdown",
        headers={"Content-disposition": "attachment; filename=scraped_papers.md"}
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
