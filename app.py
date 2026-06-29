import os
import json
from flask import Flask, render_template, request, jsonify, Response
from playwright.sync_api import sync_playwright

# Import scraper helper functions
from ieee_scraper import clean_url, scrape_paper

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def do_scrape():
    data = request.json or {}
    url_input = data.get("url", "").strip()
    if not url_input:
        return jsonify({"error": "No URL provided."}), 400
        
    cleaned_url = clean_url(url_input)
    if not cleaned_url:
        return jsonify({"error": "Invalid IEEE Xplore URL. Please check the link and try again."}), 400
        
    try:
        with sync_playwright() as p:
            # Launch chromium in headless mode
            browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            paper_info = scrape_paper(page, cleaned_url)
            browser.close()
            
        if paper_info:
            return jsonify({"success": True, "data": paper_info})
        else:
            return jsonify({"error": "Failed to scrape metadata. Playwright could not bypass WAF or parse the page."}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
