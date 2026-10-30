import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.parser import fetch_playlist_by_url
from app.matcher import compare_playlists

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TasteOfMusic")

app = FastAPI(title="TasteOfMusic — Сравнение плейлистов Яндекс Музыки", version="1.1.0")

class CompareRequest(BaseModel):
    url1: str
    url2: str

def resolve_playlist(url: str, default_name: str) -> Dict[str, Any]:
    """Fetch and parse playlist data from URL."""
    cleaned = (url or "").strip()
    if not cleaned:
        raise HTTPException(
            status_code=400,
            detail=f"Для {default_name} не указана ссылка на плейлист."
        )
    try:
        return fetch_playlist_by_url(cleaned)
    except Exception as e:
        logger.error(f"Error fetching {cleaned}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка загрузки ({default_name}): {str(e)}. Проверьте правильность и доступность ссылки."
        )

@app.post("/api/compare")
def compare_playlists_endpoint(req: CompareRequest):
    """Compare two playlists by URLs and calculate overlaps and metrics."""
    p1 = resolve_playlist(req.url1, "Плейлиста 1")
    p2 = resolve_playlist(req.url2, "Плейлиста 2")
    result = compare_playlists(p1, p2)
    return result

# Serve static frontend files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
@app.head("/")
@app.get("/index.html")
@app.head("/index.html")
def serve_index():
    index_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "TasteOfMusic Backend is running. Frontend static files missing."}
