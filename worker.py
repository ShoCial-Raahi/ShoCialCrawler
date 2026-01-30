import asyncio
import argparse
import json
import logging
import os
import traceback
from typing import List

from crawler.crawler import Crawler
from crawler.fetcher import Fetcher
from extractor.ai_extractor import AIExtractor
from normalizer.validate import DataNormalizer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("worker")

STATUS_FILE = "data/{session_id}_status.json"
PRODUCTS_FILE = "data/{session_id}_products.json"

def save_status(session_id: str, status: dict):
    with open(STATUS_FILE.format(session_id=session_id), "w") as f:
        json.dump(status, f)

def load_products(session_id: str) -> List[dict]:
    path = PRODUCTS_FILE.format(session_id=session_id)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_product(session_id: str, product: dict):
    products = load_products(session_id)
    products.append(product)
    with open(PRODUCTS_FILE.format(session_id=session_id), "w") as f:
        json.dump(products, f)

async def run_crawl(session_id: str, vendor_name: str, start_urls: List[str], page_limit: int):
    status = {
        "session_id": session_id,
        "status": "running",
        "discovered": 0,
        "extracted": 0,
        "failed": 0
    }
    save_status(session_id, status)
    
    try:
        logger.info(f"Worker started for {session_id}")
        
        # 1. Url Discovery
        async def update_progress(discovered, visited):
            status["discovered"] = discovered
            # We can also track "visited" if we add that field to status, but for now just discovered
            save_status(session_id, status)

        crawler = Crawler(start_urls=start_urls, max_pages=page_limit)
        product_urls = await crawler.crawl(progress_callback=update_progress)
        
        status["discovered"] = len(product_urls)
        save_status(session_id, status)
        
        # 2. Extract
        extractor = AIExtractor()
        
        for i, url in enumerate(product_urls):
            try:
                logger.info(f"Processing {i+1}/{len(product_urls)}: {url}")
                html = await Fetcher.fetch_page(url)
                if not html:
                    status["failed"] += 1
                    save_status(session_id, status)
                    continue
                
                raw_data = await extractor.extract(html)
                if not raw_data:
                    status["failed"] += 1
                    save_status(session_id, status)
                    continue
                
                product = DataNormalizer.normalize_and_validate(raw_data, url, vendor_name)
                
                if product:
                    save_product(session_id, product.dict())
                    status["extracted"] += 1
                else:
                    status["failed"] += 1
                    
                save_status(session_id, status)
                
            except Exception as e:
                logger.error(f"Error on {url}: {e}")
                status["failed"] += 1
                save_status(session_id, status)

        status["status"] = "completed"
        save_status(session_id, status)
        logger.info("Worker finished successfully")

    except Exception as e:
        logger.error(f"Worker crashed: {e}")
        traceback.print_exc()
        status["status"] = "failed"
        save_status(session_id, status)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--session_id", required=True)
    parser.add_argument("--vendor_name", required=True)
    parser.add_argument("--start_url", required=True)
    parser.add_argument("--page_limit", type=int, default=10)
    
    args = parser.parse_args()
    
    # Ensure data dir exists
    os.makedirs("data", exist_ok=True)
    
    # Initialize products file
    with open(PRODUCTS_FILE.format(session_id=args.session_id), "w") as f:
        json.dump([], f)
        
    asyncio.run(run_crawl(args.session_id, args.vendor_name, [args.start_url], args.page_limit))
