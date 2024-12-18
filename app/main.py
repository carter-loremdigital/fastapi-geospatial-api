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
CACHE_TTL = 600 # Cache TTL in seconds

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function for removing expired cache items
def clean_cache():
    current_time = time.time()
    keys_to_remove = [key for key, value in cache.items() if current_time > value["expiry"]]
    for key in keys_to_remove:
        del cache[key]

# Define "/near-me" API endpoint
@app.get("/near-me")
def get_nearby_events(lat: float, lon: float, radius: float = Query(10.0), db: Session = Depends(get_db)):
    # Remove expired cache entries
    clean_cache()

    # Check if request cached
    cache_key = f"near_me:{lat}:{lon}:{radius}"

    if cache_key in cache:
        return {"events": cache[cache_key]["data"]}

    # Convert radius from miles to meters
    radius_in_meters = radius * 1609.34

    # Fetch nearby events
    nearby_events = (
        db.query(Event.id, Event.name, ST_Distance(Event.location, func.ST_MakePoint(lon, lat)))
        .filter(ST_DWithin(Event.location, func.ST_MakePoint(lon, lat), radius_in_meters)) # Filter by distance
        .order_by(ST_Distance(Event.location, func.ST_MakePoint(lon, lat))) # Sort by distance (closest to furthest)
        .all()
    )

    # Parse results into JSON format
    result = [
        {"id": event[0], "name": event[1], "distance": event[2] / 1609.34}
        for event in nearby_events
    ]

    # Cache the result
    cache[cache_key] = {"data": result, "expiry": time.time() + CACHE_TTL}

    return {"events": result}
