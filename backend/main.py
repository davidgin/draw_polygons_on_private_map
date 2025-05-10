import os
import urllib.request
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from pydantic import BaseModel, Field
from typing import Optional, List
from shapely import wkt

from .database import get_db
from .models import PolygonModel


# 🌍 Download OSM file if not already present
def download_osm_once():
    osm_dir = os.getenv("OSM_DATA_DIR", "osm_data")
    osm_file = os.path.join(osm_dir, "planet-latest.osm.pbf")
    osm_url = "https://planet.osm.org/pbf/planet-latest.osm.pbf"
    os.makedirs(osm_dir, exist_ok=True)
    if not os.path.exists(osm_file):
        print("📥 Downloading OSM planet file...")
        try:
            req = urllib.request.Request(osm_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as response, open(osm_file, 'wb') as out_file:
                out_file.write(response.read())
            print("✅ OSM file downloaded.")
        except Exception as e:
            print(f"❌ Failed to download OSM: {e}")
    else:
        print("🗺️ OSM file already exists.")

download_osm_once()

# 🚀 FastAPI application
app = FastAPI()

# 📂 Serve static frontend from /frontend
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# 📄 Pydantic Schemas
class PolygonRequest(BaseModel):
    client_id: Optional[int] = None
    name: str = Field(..., min_length=1)
    wkt: str = Field(...)

class PolygonResponse(BaseModel):
    id: int
    client_id: int
    name: str
    polygon: str


# ➕ Create polygon
@app.post("/api/polygons/save", response_model=PolygonResponse)
async def save_polygon(polygon: PolygonRequest, db: AsyncSession = Depends(get_db)):
    if not polygon.name.strip():
        raise HTTPException(status_code=400, detail="Polygon name is required")
    try:
        wkt.loads(polygon.wkt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid WKT: {e}")
    obj = PolygonModel(
        name=polygon.name,
        client_id=polygon.client_id or 0,
        polygon=polygon.wkt,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# 📥 Get all polygons
@app.get("/api/polygons/all", response_model=List[PolygonResponse])
async def get_all(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PolygonModel))
    return res.scalars().all()


# 📥 Get polygons by client_id
@app.get("/api/polygons/client/{client_id}", response_model=List[PolygonResponse])
async def get_by_client(client_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PolygonModel).where(PolygonModel.client_id == client_id))
    return res.scalars().all()


# 🗑 Delete polygon
@app.delete("/api/polygons/{polygon_id}")
async def delete(polygon_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(delete(PolygonModel).where(PolygonModel.id == polygon_id))
    await db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Polygon not found")
    return {"message": "Deleted"}


# ✏️ Update polygon
@app.put("/api/polygons/{polygon_id}", response_model=PolygonResponse)
async def update(polygon_id: int, polygon: PolygonRequest, db: AsyncSession = Depends(get_db)):
    try:
        wkt.loads(polygon.wkt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid WKT: {e}")
    res = await db.execute(
        update(PolygonModel)
        .where(PolygonModel.id == polygon_id)
        .values(name=polygon.name, client_id=polygon.client_id or 0, polygon=polygon.wkt)
        .returning(PolygonModel)
    )
    obj = res.fetchone()
    await db.commit()
    if not obj:
        raise HTTPException(status_code=404, detail="Polygon not found")
    return obj
