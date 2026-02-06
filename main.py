from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import json
import pandas as pd
import time
import os
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class KeywordRequest(BaseModel):
    seed: str
    service: str = "google"
    limit: int = 500

services = {
    "google": "http://suggestqueries.google.com/complete/search?client=chrome&q=",
    "youtube": "http://suggestqueries.google.com/complete/search?client=chrome&ds=yt&q=",
    "amazon": "http://completion.amazon.co.uk/search/complete?method=completion&search-alias=aps&q="
}

def safe_api_call(url):
    try:
        time.sleep(0.1)
        r = requests.get(url, verify=False, timeout=8)
        data = r.json()
        return data[1] if len(data) > 1 else []
    except:
        return []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate_keywords(req: KeywordRequest):
    keywords = [req.seed]
    
    # Main API call
    url = services.get(req.service, services["google"]) + req.seed
    suggestions = safe_api_call(url)
    keywords.extend(suggestions)
    
    # Quick prefixes (fast loading ke liye limited)
    prefixes = ['how ', 'best ', 'top ', 'free ']
    for prefix in prefixes:
        url = services["google"] + prefix + req.seed
        keywords.extend(safe_api_call(url)[:5])  # Limited per call
    
    # Clean unique
    keywords = list(dict.fromkeys([k for k in keywords if req.seed.lower() in k.lower()]))
    keywords = keywords[:req.limit]
    
    # CSV save
    filename = f"keywords_{req.seed.replace(' ', '_')}_{int(time.time())}.csv"
    df = pd.DataFrame({'Keywords': keywords})
    df.to_csv(filename, index=False)
    
    return {
        "success": True,
        "total": len(keywords),
        "keywords": keywords[:50],
        "download": filename
    }

@app.get("/download/{filename}")
async def download(filename: str):
    if os.path.exists(filename):
        return FileResponse(filename, filename=filename, media_type='text/csv')
    return {"error": "File not found"}
