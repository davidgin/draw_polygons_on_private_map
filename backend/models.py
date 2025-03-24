from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from .database import Base

class PolygonModel(Base):
    __tablename__ = "polygons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False)
    polygon = Column(Geometry("POLYGON"), nullable=False)
