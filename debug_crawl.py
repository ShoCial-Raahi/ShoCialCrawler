import asyncio
from crawler.fetcher import Fetcher
from crawler.url_discovery import URLDiscovery

async def test_crawl():
    url = "https://keevaaexports.com/hit_collections"
    print(f"--- Starting Debug Crawl for {url} ---")
    
    print("1. Fetching page...")
    try:
        html = await Fetcher.fetch_page(url)
        print(f"   > Fetch complete. HTML length: {len(html) if html else 0}")
        
        if not html:
            print("!!! ERROR: HTML is empty. Fetcher failed to retrieve content.")
            return

        print("2. Extracting Links...")
        links = URLDiscovery.extract_links(html, url)
        print(f"   > Found {len(links)} total links.")
        
        print(f"3. Analyzing Links (First 50 of {len(links)}):")
        for i, link in enumerate(list(links)[:50]):
            print(f"   - {link}")
            
        print("4. Testing Product Detection:")
        product_count = 0
        for link in links:
            if URLDiscovery.is_product_url(link):
                product_count += 1
                if product_count <= 5:
                     print(f"   + Valid Product URL: {link}")
        
        print(f"   > Total Products identified: {product_count}")

    except Exception as e:
        print(f"!!! CRITICAL EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crawl())
