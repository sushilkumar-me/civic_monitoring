import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use environment variable for production (Render), fallback to local for development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost/civic_monitoring")

# Fix for Render/Heroku which might provide 'postgres://' instead of 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

