from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geography
from app.database import Base

# Define event schema
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(Geography(geometry_type="POINT", srid=4326))
