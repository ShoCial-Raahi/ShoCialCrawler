from playwright.sync_api import sync_playwright

def scrape(config):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(config["base_url"])

        products = []
        product_elements = page.query_selector_all(config["product_list_selector"])

        for product_element in product_elements:
            product = {}
            for field, selector in config["fields"].items():
                product[field] = product_element.query_selector(selector).inner_text()
            products.append(product)

        browser.close()
        return products
