import os
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from src.logger import logger

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")

    if not all([db_user, db_password, db_name]):
        raise RuntimeError(
            "PostgreSQL configuration is required. Set DATABASE_URL or DB_USER, DB_PASSWORD, DB_NAME."
        )

    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

if not DATABASE_URL.startswith("postgresql"):
    raise RuntimeError("DATABASE_URL must use PostgreSQL: postgresql://...")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME") or "<unknown>"
    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                logger.info(
                    "PostgreSQL connection verified: %s:%s/%s",
                    db_host,
                    db_port,
                    db_name,
                )
            break
        except OperationalError as exc:
            if attempt == max_attempts:
                logger.critical(
                    "Could not connect to PostgreSQL after %s attempts.",
                    max_attempts,
                    exc_info=exc,
                )
                raise
            logger.warning(
                "PostgreSQL is not ready yet (attempt %s/%s). Retrying...",
                attempt,
                max_attempts,
                exc_info=exc,
            )
            time.sleep(2 * attempt)

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as exc:
        logger.critical("Database initialization failed.", exc_info=exc)
        raise
