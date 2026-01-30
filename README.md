# ShoCial Vendor Import Studio 🚀

AI-Powered Web Scraper & Product Extractor for Shopify/e-commerce vendors.

## Features

- **Intelligent Crawling**: Automatically discovers product pages using heuristics.
- **AI Extraction**: Uses LLMs (OpenAI/DeepSeek) to extract structured product data from HTML.
- **Robustness**: Runs crawler in isolated subprocess to avoid event loop conflicts (Windows-safe).
- **Real-time UI**: Live progress tracking and preview.
- **Export**: Export data to CSV (Google Sheets integration coming soon).

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/YOUR_USERNAME/social-vendor-import.git
    cd social-vendor-import
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    python -m playwright install
    ```

3. **Configure Environment**:
    - Copy `.env.example` to `.env` (creates it if missing).
    - Add your API Keys:

        ```ini
        OPENAI_API_KEY=your_key_here
        # Optional:
        AI_PROVIDER_BASE_URL=https://api.deepseek.com
        AI_MODEL_NAME=deepseek-chat
        ```

## Usage

1. **Start the Server**:

    ```bash
    python app.py
    ```

2. **Open in Browser**:
    Go to `http://localhost:8000/vendor-import`

3. **Start Crawling**:
    - Enter Vendor Name.
    - Enter Start URL (e.g., `https://example.com/collections/all`).
    - Click **Start AI Crawl**.

## Project Structure

- `app.py`: FastAPI server and process manager.
- `worker.py`: Independent crawler process.
- `crawler/`: Crawling logic (Crawl4AI + BeautifulSoup).
- `extractor/`: AI extraction logic.
- `storage/`: Data persistence (JSON/CSV).
- `static/`: Frontend (HTML/JS).

## License

Proprietary / Internal Use.
