from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os
from pathlib import Path

# Detect DB type: sqlite (default) or postgres
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

if DB_TYPE == "sqlite":
    # Default local sqlite path: project_root/ufc.db
    default_sqlite_path = Path(__file__).resolve().parents[2] / "ufc.db"
    db_path = os.getenv("DB_PATH", str(default_sqlite_path))
    DATABASE_URL = f"sqlite:///{db_path}"

elif DB_TYPE == "postgres":
    # Expect these env vars inside docker/prod
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "ufc")

    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

else:
    raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()