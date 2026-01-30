import csv
import io
import pandas as pd
from typing import List
from models.product import Product

class Exporter:
    @staticmethod
    def to_csv_string(products: List[Product]) -> str:
        if not products:
            return ""
        
        # Create a list of dictionaries for pandas
        data = [p.dict() for p in products]
        
        # Handle list of images -> pipe separated string
        for item in data:
            item['images'] = "|".join(item['images'])
            
        df = pd.DataFrame(data)
        
        # Desired column order
        columns = [
            "sku", "catalog", "product_name", "price_inr", 
            "fabric", "description", "images", "product_url"
        ]
        
        # Ensure we only have these columns and they exist
        existing_cols = [c for c in columns if c in df.columns]
        df = df[existing_cols]
        
        return df.to_csv(index=False)

    @staticmethod
    def append_to_sheet(sheet_id: str, products: List[Product], credentials_file: str):
        # Placeholder for Google Sheets API integration
        # Real implementation requires google-auth and google-api-python-client
        pass
