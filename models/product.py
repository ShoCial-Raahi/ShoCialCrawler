from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    sku: str = Field(..., description="Unique Stock Keeping Unit")
    catalog: Optional[str] = Field(None, description="Catalog or Collection Name")
    product_name: str = Field(..., description="Name of the product")
    price_inr: int = Field(..., description="Price in INR (numeric only)")
    fabric: Optional[str] = Field(None, description="Material or Fabric type")
    description: str = Field(..., description="Product description")
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    product_url: str = Field(..., description="Source URL of the product")
    source_site: str = Field(..., description="Domain or name of the vendor")

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "KV-1001",
                "catalog": "Summer 2025",
                "product_name": "Floral Cotton Dress",
                "price_inr": 1500,
                "fabric": "Cotton",
                "description": "A beautiful lighting floral dress.",
                "images": ["https://example.com/img1.jpg"],
                "product_url": "https://example.com/p/floral-dress",
                "source_site": "example.com"
            }
        }
