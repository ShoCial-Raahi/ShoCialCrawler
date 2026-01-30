from typing import Dict, Any, Optional
from models.product import Product
from normalizer.clean import Cleaner, Validator as RawValidator

class DataNormalizer:
    @staticmethod
    def normalize_and_validate(raw_data: Dict[str, Any], url: str, vendor: str) -> Optional[Product]:
        
        # 1. Clean fields
        price = Cleaner.clean_price(raw_data.get("price_inr", 0))
        name = Cleaner.clean_text(raw_data.get("product_name", ""))
        sku = Cleaner.clean_text(raw_data.get("sku", ""))
        desc = Cleaner.clean_text(raw_data.get("description", ""))
        
        # 2. Check strict validation
        validation_payload = {
            "product_name": name,
            "price_inr": price,
            "sku": sku,
            "images": raw_data.get("images", [])
        }
        
        if not RawValidator.validate_product(validation_payload):
            return None
            
        # 3. Create Product Object
        return Product(
            sku=sku,
            catalog=raw_data.get("catalog"),
            product_name=name,
            price_inr=price,
            fabric=raw_data.get("fabric"),
            description=desc,
            images=raw_data.get("images", []),
            product_url=url,
            source_site=vendor
        )
