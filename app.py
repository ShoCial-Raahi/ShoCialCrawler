import asyncio
import uuid
import logging
import subprocess
import sys
import json
import os
from typing import List, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from config import Config
from storage.export import Exporter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vendor_import")

app = FastAPI(title="ShoCial Vendor Import Studio")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

# Models for API
class CrawlRequest(BaseModel):
    vendor_name: str
    base_url: str
    start_urls: List[str]
    page_limit: int = 50

# Global status tracker (simple in-memory for recent sessions, helps with discovery)
# But source of truth is now files in data/

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_status_file(session_id):
    return os.path.join(DATA_DIR, f"{session_id}_status.json")

def get_products_file(session_id):
    return os.path.join(DATA_DIR, f"{session_id}_products.json")

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse("static/index.html")

@app.get("/vendor-import", response_class=HTMLResponse)
async def vendor_import_ui():
    return FileResponse("static/index.html")

@app.get("/vendor-import/preview", response_class=HTMLResponse)
async def preview_ui():
    return FileResponse("static/preview.html")

@app.post("/api/crawl/start")
async def start_crawl(request: CrawlRequest):
    session_id = str(uuid.uuid4())[:8]
    
    # Initialize status file
    initial_status = {
        "session_id": session_id,
        "status": "starting",
        "discovered": 0,
        "extracted": 0,
        "failed": 0
    }
    with open(get_status_file(session_id), "w") as f:
        json.dump(initial_status, f)
        
    with open(get_products_file(session_id), "w") as f:
        json.dump([], f)
    
    # Launch Worker Subprocess
    # We pass the python executable to ensure we use the same venv
    cmd = [
        sys.executable, "worker.py",
        "--session_id", session_id,
        "--vendor_name", request.vendor_name,
        "--start_url", request.start_urls[0], # currently UI only sends one
        "--page_limit", str(request.page_limit)
    ]
    
    logger.info(f"Launching worker for {session_id}: {' '.join(cmd)}")
    
    # Popen is non-blocking
    subprocess.Popen(cmd, cwd=os.getcwd())
    
    return {"session_id": session_id, "status": "started"}

@app.get("/api/crawl/status/{session_id}")
async def get_status(session_id: str):
    path = get_status_file(session_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        with open(path, "r") as f:
            status = json.load(f)
        return status
    except Exception as e:
        logger.error(f"Failed to read status: {e}")
        return {"session_id": session_id, "status": "unknown", "discovered": 0, "extracted": 0, "failed": 0}

@app.get("/api/preview/{session_id}")
async def get_preview(session_id: str):
    path = get_products_file(session_id)
    if not os.path.exists(path):
        return {"products": []}
        
    try:
        with open(path, "r") as f:
            products = json.load(f)
            # Products in file are dicts, Exporter expects logic? 
            # Or we just return dicts. The UI expects list of objects.
        return {"products": products}
    except:
        return {"products": []}

@app.get("/api/export/csv/{session_id}")
async def export_csv(session_id: str):
    path = get_products_file(session_id)
    if not os.path.exists(path):
         return HTMLResponse(content="", media_type="text/csv")
         
    try:
        with open(path, "r") as f:
            products_data = json.load(f)
            
        # Convert dicts back to objects if Exporter needs properly typed objects
        # OR update Exporter to handle dicts. 
        # Making a quick Exporter compatible implementation here or converting:
        from models.product import Product
        
        # Helper to convert dict to object if needed, or if Exporter handles dicts we are fine.
        # Assuming Exporter.to_csv_string expects objects with attributes.
        # Let's verify usage of Exporter. But for now, let's assume objects.
        products = []
        for p in products_data:
            try:
                products.append(Product(**p))
            except:
                pass 
        
        csv_content = Exporter.to_csv_string(products)
        
        return HTMLResponse(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=products_{session_id}.csv"}
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return HTMLResponse(content=f"Error: {e}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    # Verify worker.py exists
    if not os.path.exists("worker.py"):
        print("CRITAL ERROR: worker.py not found!")
    else:
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
