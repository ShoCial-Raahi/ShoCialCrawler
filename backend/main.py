import asyncio
import argparse
import json
import os
import sys
import logging
from typing import List

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.crawler import Crawler
from crawler.fetcher import Fetcher
from extractor.ai_extractor import AIExtractor
from normalizer.validate import DataNormalizer
from storage.export import Exporter
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vendor_import")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "data")
os.makedirs(DATA_DIR, exist_ok=True)

async def run_crawl(vendor_name: str, start_url: str, page_limit: int = 50):
    logger.info(f"Starting crawl for {vendor_name} at {start_url}")
    
    # 1. Discover URLs
    crawler = Crawler(start_urls=[start_url], max_pages=page_limit)
    product_urls = await crawler.crawl()
    
    logger.info(f"Discovered {len(product_urls)} product URLs")
    
    # 2. Extract Data
    extractor = AIExtractor()
    products = []
    
    for i, url in enumerate(product_urls):
        try:
            logger.info(f"Processing ({i+1}/{len(product_urls)}): {url}")
            html = await Fetcher.fetch_page(url)
            if not html:
                logger.error(f"Empty HTML for {url}")
                continue
            
            raw_data = await extractor.extract(html)
            if not raw_data:
                logger.error(f"Failed extraction for {url}")
                continue
                
            product = DataNormalizer.normalize_and_validate(raw_data, url, vendor_name)
            if product:
                products.append(product)
                
                # Progressive Save (for preview)
                save_preview(products)
            else:
                logger.warning(f"Validation failed for {url}")
                
        except Exception as e:
            logger.error(f"Error on {url}: {e}")

    # 3. Final Export
    save_final(products)
    logger.info("Crawl completed successfully")

def save_preview(products: List):
    """Save current progress to frontend/data/latest.json"""
    data = [p.dict() for p in products]
    preview_path = os.path.join(DATA_DIR, "latest.json")
    with open(preview_path, "w") as f:
        json.dump(data, f, indent=2)

def save_final(products: List):
    """Save final CSV and JSON"""
    # CSV
    csv_content = Exporter.to_csv_string(products)
    csv_path = os.path.join(DATA_DIR, "products.csv")
    with open(csv_path, "w", encoding='utf-8') as f:
        f.write(csv_content)
        
    logger.info(f"Saved artifacts to {DATA_DIR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShoCial Vendor Crawler CLI")
    parser.add_argument("--vendor_name", type=str, required=True, help="Name of the vendor")
    parser.add_argument("--start_url", type=str, required=True, help="Starting URL for crawling")
    parser.add_argument("--page_limit", type=int, default=50, help="Max pages to crawl")
    
    args = parser.parse_args()
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(run_crawl(args.vendor_name, args.start_url, args.page_limit))
