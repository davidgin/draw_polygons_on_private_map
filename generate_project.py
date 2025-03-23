import os
import shutil

project_structure = {
    "polygon-mapping/": [
        "backend/",
        "frontend/",
        "db/",
        "osm/",
    ],
    "polygon-mapping/backend/": [
        "main.py",
        "Dockerfile",
        "requirements.txt",
    ],
    "polygon-mapping/frontend/": [
        "index.html",
        "Dockerfile",
    ],
    "polygon-mapping/db/": [
        "init.sql",
        "Dockerfile",
    ],
    "polygon-mapping/docker-compose.yml": None,
    "polygon-mapping/README.md": None,
}

def create_project_structure()

docker_compose_yml = """
version: '3.8'

services:
  db:
    image: postgis/postgis
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    depends_on:
      - db
    volumes:
      - ${HOME}/osm:/osm

  frontend:
    build: ./frontend
    ports:
      - "8081:80"
    depends_on:
      - backend

volumes:
  pg_data:
"""

with open("polygon-mapping/docker-compose.yml", "w") as f:
    f.write(docker_compose_yml):
    for path, files in project_structure.items():
        os.makedirs(path, exist_ok=True)
        if files:
            for file in files:
                open(os.path.join(path, file), "a").close()

create_project_structure()

backend_main_py = """
import os
import time
import logging
import requests
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Polygon(Base):
    __tablename__ = "polygons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    geom = Column(String, nullable=False)

def wait_for_db():
    retries = 60
    while retries > 0:
        try:
            db = SessionLocal()
            db.execute('SELECT 1')
            db.close()
            logging.info("Database is ready.")
            Base.metadata.create_all(bind=engine)
            logging.info("Database schema ensured.")
            return
        except OperationalError:
            logging.warning(f"Waiting for database... ({retries} retries left)")
            time.sleep(3600)
            retries -= 1
    raise Exception("Database not available.")

PLANET_PBF_URL = "https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf"
PLANET_PBF_FILE = "/osm/planet-latest.osm.pbf"

def download_planet_pbf():
    if not os.access("/osm", os.W_OK):
        logging.error("OSM directory /osm is not writable or not mounted!")
        return
    logging.info("Checking /osm directory...")
    if not os.path.exists(PLANET_PBF_FILE):
        logging.info("Starting the planet OSM PBF download...")
        with requests.get(PLANET_PBF_URL, stream=True) as r:
            r.raise_for_status()
            total_length = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(PLANET_PBF_FILE, 'wb') as f:
                for chunk in r.iter_content(chunk_size=16777216):  # 16MB
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / total_length) * 100 if total_length else 0
                    logging.info(f"Download progress: {percent:.2f}%")
        logging.info("Planet OSM PBF file downloaded.")
    else:
        file_size = os.path.getsize(PLANET_PBF_FILE) / (1024 * 1024 * 1024)
        logging.info(f"Planet OSM PBF file already exists. Size: {file_size:.2f} GB")

app = FastAPI()

@app.on_event("startup")
def startup_event():
    wait_for_db()
    download_planet_pbf()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Polygon Mapping API"}

@app.get("/polygons/")
def list_polygons(db: SessionLocal = Depends(SessionLocal)):
    return db.query(Polygon).all()
"""

# Writing backend main.py
with open("polygon-mapping/backend/main.py", "w") as f:
    f.write(backend_main_py)

