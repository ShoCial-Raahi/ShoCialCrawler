from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

class URLDiscovery:
    @staticmethod
    def extract_links(html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            links.add(full_url)
        return list(links)

    @staticmethod
    def is_product_url(url: str) -> bool:
        # Heuristic: URL contains 'product', 'item', 'p/', or ends with digits ID 
        # This is a basic heuristic and might need customization per vendor
        path = urlparse(url).path.lower()
        keywords = ['/products/', '/product/', '/item/', '/p/', '/dp/', '/portfolio/']
        # Exclude specific non-product patterns
        exclude = ['/collections/', '/category/', '/pages/', '/blogs/']
        
        if any(ex in path for ex in exclude):
            return False
            
        return any(k in path for k in keywords) 
