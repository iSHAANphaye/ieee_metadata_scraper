# Paper Scraper

A premium, high-performance academic metadata scraper and citation network crawler designed to bypass cloud security protection scripts, cache metadata, and allow users to explore and scrape citation loops infinitely deep.

## 🚀 Key Features

*   **Bypasses AWS WAF**: Automatically resolves anti-bot challenge scripts (`challenge.js`) using headless browser automation.
*   **MongoDB Atlas Caching**: Checks database before starting the scraping engine. Cached documents return instantly (**under 20ms**), saving bandwidth and execution runs.
*   **Hybrid AJAX Scraper**: Solves the verification challenge once per session. Subsequent subpages are fetched programmatically in **under 200ms** by dispatching raw background AJAX fetches inside the already authenticated browser context.
*   **Citation Traversal Workspace**: Displays citations, references, and similar paper listings. Clicking **"Explore Connections"** on any card pushes it to the primary view, updating its lists and enabling you to crawl down the citation loop recursively.
*   **Interactive Breadcrumb History**: Track your crawler trail (`Home > Paper A > Paper B > Paper C`) and jump back to parent papers instantly without re-scraping.
*   **User Session Auth**: Built-in email & password authentication utilizing salted secure password hashing (`werkzeug.security`) and Flask cookie sessions.
*   **Scrape Registry (History)**: Access all previously scraped papers from your account, load them back into the workspace instantly, or purge them from the cache.
*   **Consolidated Exporters**: Download scraped data individually or export combined lists as structured Markdown or JSON packages.

---

## 🛠️ Technology Stack

*   **Backend**: Python, Flask (Server), Playwright (Headless Chromium), BeautifulSoup4, PyMongo.
*   **Database**: MongoDB Atlas.
*   **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphic Dark UI), JavaScript (ES6+), FontAwesome Icons.
*   **Containerization**: Docker, Docker Compose.

---

## 📥 Getting Started (Local Run)

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your machine.

### 2. Install Dependencies
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Environments
Create a `.env` file in the root directory:
```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/paper_scraper_db
SECRET_KEY=your_secure_session_secret_key
```

### 4. Launch Flask Server
Run the Flask application:
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🐳 Getting Started (Docker run)

Ensure you have **Docker Desktop** running.

### Using the startup helper scripts
Simply run the helper script which stops conflicts and starts the container named `paper-scraper` mapped to port `5001`:

*   **On Windows (PowerShell)**:
    ```powershell
    .\run.ps1
    ```
*   **On Linux/macOS (Bash)**:
    ```bash
    chmod +x run.sh
    ./run.sh
    ```

### Or using Docker Compose
To spin up both the web scraper and a local MongoDB fallback container:
```bash
docker compose up --build
```
Open **[http://127.0.0.1:5001](http://127.0.0.1:5001)** in your browser.

---

## ☁️ Deployment on Render

1.  Push your code to **GitHub** (exclude `.env` in `.gitignore`/`.dockerignore`).
2.  Log in to the **Render Dashboard** and select **New + > Web Service**.
3.  Connect your GitHub repository.
4.  Configure Settings:
    *   **Runtime**: Select `Docker`.
    *   **Instance Type**: Select `Free`.
5.  Set Environment Variables in Render:
    *   `MONGO_URI` = `mongodb+srv://...`
    *   `SECRET_KEY` = `your_secret_key`
6.  Click **Deploy**. Render will build the container using the root `Dockerfile` and go live.
