from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Define database URL
DATABASE_URL = "postgresql://api_user:password@localhost/geospatial_api"

# Set up database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
