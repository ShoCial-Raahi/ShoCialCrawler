import asyncio
from typing import List, Set
from crawler.fetcher import Fetcher
from crawler.url_discovery import URLDiscovery

class Crawler:
    def __init__(self, start_urls: List[str], max_pages: int = 10):
        self.start_urls = start_urls
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        self.product_urls: Set[str] = set()

    async def crawl(self, progress_callback=None):
        queue = list(self.start_urls)
        
        while queue and len(self.visited) < self.max_pages:
            if progress_callback:
                try:
                    await progress_callback(len(self.product_urls), len(self.visited))
                except Exception as e:
                    print(f"Callback error: {e}")
            url = queue.pop(0)
            if url in self.visited:
                continue
            
            print(f"Crawling: {url}")
            try:
                html = await Fetcher.fetch_page(url)
                if not html:
                    print(f"!!! Error: Empty HTML for {url}")
                    continue
                
                print(f"  > HTML Length: {len(html)}")
                self.visited.add(url)
                
                # Discover links
                links = URLDiscovery.extract_links(html, url)
                print(f"  > Found {len(links)} raw links on {url}")
                
                # Filter useful links (simple heuristic for now: stays on same domain)
                base_domain = url.split('/')[2] # basic domain check
                
                for link in links:
                    if base_domain in link:
                        if URLDiscovery.is_product_url(link):
                            print(f"    + Found Product: {link}")
                            self.product_urls.add(link)
                            if progress_callback:
                                await progress_callback(len(self.product_urls), len(self.visited))
                        elif link not in self.visited:
                            # Add to queue if it looks like a category or listing page
                            # Relaxed filter: Allow anything that isn't obviously a utility page
                            keywords = ["collection", "category", "shop", "product", "item", "page"]
                            if any(k in link for k in keywords) or "sarees" in link: # Hack for specific user case if needed, but generic is better
                                # Generic fallback: if it looks like a subpath of start URL
                                queue.append(link)
                            else:
                                # Logging rejection for debug
                                # print(f"    - Skipped non-listing: {link}")
                                pass

            except Exception as e:
                print(f"Failed to crawl {url}: {e}")

        print(f"Discovered {len(self.product_urls)} product URLs")
        return list(self.product_urls)
