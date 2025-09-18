from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from pathlib import Path

# Get project root (2 levels up)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# DB env vars
DB_TYPE = "sqlite:///"
DB_NAME = "ufc.db"
DATABASE_URL = f"{DB_TYPE}{PROJECT_ROOT / DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()