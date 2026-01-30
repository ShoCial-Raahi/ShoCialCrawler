from typing import Dict, List, Optional
from models.product import Product

class MemoryStore:
    def __init__(self):
        # Structure: { session_id: [Product, Product, ...] }
        self._sessions: Dict[str, List[Product]] = {}

    def create_session(self, session_id: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []

    def add_product(self, session_id: str, product: Product):
        if session_id not in self._sessions:
            self.create_session(session_id)
        
        # Prevent duplicates based on SKU within the same session
        existing_skus = {p.sku for p in self._sessions[session_id]}
        if product.sku not in existing_skus:
            self._sessions[session_id].append(product)

    def get_products(self, session_id: str) -> List[Product]:
        return self._sessions.get(session_id, [])

    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

    def update_product(self, session_id: str, sku: str, updated_data: dict):
        products = self._sessions.get(session_id, [])
        for i, p in enumerate(products):
            if p.sku == sku:
                # Create a copy with updated fields
                updated_product = p.copy(update=updated_data)
                products[i] = updated_product
                return True
        return False

    def delete_product(self, session_id: str, sku: str):
        if session_id in self._sessions:
            self._sessions[session_id] = [p for p in self._sessions[session_id] if p.sku != sku]

# Global instance
store = MemoryStore()
