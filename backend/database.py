import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()
# Use Postgres if set
DATABASE_URL = os.environ["DATABASE_URL"]
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

if "sqlite" in DATABASE_URL:
    raise ValueError("DATABASE_URL Points to sqllite, which is not supported. Please use PostgreSQL with PostGIS for testing.")

# SQLAlchemy engine and session setup
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
