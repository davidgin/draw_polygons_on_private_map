
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from shapely import wkt
import os
import osmnx as ox

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Polygon(Base):
    __tablename__ = 'polygons'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    client_id = Column(String, default='0')
    geom = Column(Geometry('POLYGON'))


import time
import logging

logging.basicConfig(level=logging.INFO)

def wait_for_db():
    retries = 60
    retries = 60
    while retries > 0:
        try:
            db = SessionLocal()
            db.execute('SELECT 1')
            db.close()
            logging.info("Database is ready.")
            Base.metadata.create_all(bind=engine)
            logging.info("Database schema ensured.")
    Base.metadata.create_all(bind=engine)
    logging.info("Database schema ensured.")
            return
        except Exception as e:
            logging.warning(f"Waiting for database... ({retries} retries left)")
            time.sleep(3600)
            retries -= 1
    raise Exception("Database not available.")

import requests

PLANET_PBF_URL = "https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf"
PLANET_PBF_FILE = "/osm/planet-latest.osm.pbf"

def download_planet_pbf():
    if not os.access("/osm", os.W_OK):
        logging.error("OSM directory /osm is not writable or not mounted!")
        return
    logging.info("OSM directory /osm is writable and mounted correctly.")
    logging.info("Checking /osm directory...")

    if not os.path.exists(PLANET_PBF_FILE):
        logging.info("Starting the planet OSM PBF download...")
        logging.info("Downloading the full planet OSM PBF file...")
        with requests.get(PLANET_PBF_URL, stream=True) as r:
            r.raise_for_status()
            total_length = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(PLANET_PBF_FILE, 'wb') as f:
                for chunk in r.iter_content(chunk_size=16777216):
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / total_length) * 100 if total_length else 0
                    logging.info(f"Download progress: {percent:.2f}%")
        logging.info("Planet OSM PBF file downloaded.")
    else:
        file_size = os.path.getsize(PLANET_PBF_FILE) / (1024 * 1024 * 1024)
        logging.info(f"Planet OSM PBF file already exists. Size: {file_size:.2f} GB")


def populate_osm():
    db = SessionLocal()
    if db.query(Polygon).first() is None:
        logging.info("Populating database with OSM data...")
        try:
            gdf = ox.geometries_from_place('Manhattan, New York, USA', {'building': True})
            for _, row in gdf.iterrows():
                if row.geometry.geom_type == 'Polygon':
                    db_polygon = Polygon(
                        name=row.get('name', 'OSM Building'),
                        geom=f'SRID=4326;{row.geometry.wkt}'
                    )
                    db.add(db_polygon)
            db.commit()
            logging.info("OSM data population completed.")
        except Exception as e:
            logging.error(f"Error populating OSM data: {e}")
    else:
        logging.info("Database already populated.")
    db.close()

class PolygonCreate(BaseModel):
    name: str
    wkt: str
    client_id: str = '0'

class PolygonResponse(BaseModel):
    id: int
    name: str
    client_id: str
    wkt: str

    class Config:
        orm_mode = True

app = FastAPI()

@app.on_event("startup")
def startup_event():
    wait_for_db()
    download_planet_pbf()
    populate_osm()

@app.post("/polygons/", response_model=PolygonResponse)
def create_polygon(polygon: PolygonCreate):
    db = SessionLocal()
    db_polygon = Polygon(
        name=polygon.name,
        client_id=polygon.client_id,
        geom=f'SRID=4326;{polygon.wkt}'
    )
    db.add(db_polygon)
    db.commit()
    db.refresh(db_polygon)
    db.close()
    return PolygonResponse(
        id=db_polygon.id,
        name=db_polygon.name,
        client_id=db_polygon.client_id,
        wkt=polygon.wkt
    )

@app.get("/polygons/", response_model=List[PolygonResponse])
def read_polygons():
    db = SessionLocal()
    polygons = db.query(Polygon).all()
    result = [
        PolygonResponse(
            id=p.id,
            name=p.name,
            client_id=p.client_id,
            wkt=db.execute(p.geom.ST_AsText()).scalar()
        ) for p in polygons
    ]
    db.close()
    return result

@app.delete("/polygons/{polygon_id}")
def delete_polygon(polygon_id: int):
    db = SessionLocal()
    polygon = db.query(Polygon).get(polygon_id)
    if not polygon:
        db.close()
        raise HTTPException(status_code=404, detail="Polygon not found")
    db.delete(polygon)
    db.commit()
    db.close()
    return {"detail": "Polygon deleted"}
