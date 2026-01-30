import re
from typing import Dict, Any

class Cleaner:
    @staticmethod
    def clean_price(price: Any) -> int:
        if isinstance(price, int):
            return price
        if isinstance(price, str):
            # Remove currency symbols, commas, etc.
            cleaned = re.sub(r'[^\d]', '', price)
            try:
                return int(cleaned)
            except ValueError:
                return 0
        return 0

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        return text.strip()

class Validator:
    @staticmethod
    def validate_product(data: Dict[str, Any]) -> bool:
        # Must have Name, Price > 0
        if not data.get("product_name"):
            return False
        if not data.get("price_inr") or data.get("price_inr") == 0:
            return False
            
        # Optional: Check if images exist
        if not data.get("images") or len(data["images"]) == 0:
            # We might allow products without images but flag them? 
            # For now, let's keep it strict-ish or lax depending on user req.
            # User said "Drop products missing SKU or price"
            pass
            
        if not data.get("sku"):
             # Sometimes AI fails to generate SKU if not present. 
             # We might want to auto-generate one or fail. 
             # User rule: "Drop products missing SKU or price"
             return False
             
        return True
