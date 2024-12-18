from sqlalchemy import func  # General SQL functions
from geoalchemy2.functions import ST_Distance, ST_DWithin  # Specific geospatial functions
from fastapi import FastAPI, Query, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Event
import time

app = FastAPI()

# In-memory cache
cache = {}
CACHE_TTL = 600

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def clean_cache():
    current_time = time.time()
    keys_to_remove = [key for key, value in cache.items() if current_time > value["expiry"]]
    for key in keys_to_remove:
        del cache[key]

@app.get("/near-me")
def get_nearby_events(lat: float, lon: float, radius: float = Query(10.0), db: Session = Depends(get_db)):
    clean_cache()
    cache_key = f"near_me:{lat}:{lon}:{radius}"

    if cache_key in cache:
        return {"events": cache[cache_key]["data"]}

    radius_in_meters = radius * 1609.34

    nearby_events = (
        db.query(Event.id, Event.name, ST_Distance(Event.location, func.ST_MakePoint(lon, lat)))
        .filter(ST_DWithin(Event.location, func.ST_MakePoint(lon, lat), radius_in_meters))
        .order_by(ST_Distance(Event.location, func.ST_MakePoint(lon, lat)))
        .all()
    )

    # print(nearby_events)

    result = [
        {"id": event[0], "name": event[1], "distance": event[2] / 1609.34}
        for event in nearby_events
    ]

    cache[cache_key] = {"data": result, "expiry": time.time() + CACHE_TTL}
    
    # print(cache)

    return {"events": result}
