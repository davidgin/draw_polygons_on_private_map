import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.models import Base
from backend.database import get_db
import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:55432/test_db"


# Use PostgreSQL + PostGIS test DB
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:55432/test_db"
engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Override FastAPI's get_db dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Create tables before tests
@pytest_asyncio.fixture(scope="module", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

polygon_id = None

@pytest.mark.asyncio
async def test_create_polygon(client):
    global polygon_id
    response = await client.post("/api/polygons/save", json={
        "name": "Test Polygon",
        "client_id": 123,
        "wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"
    })
    assert response.status_code == 200
    data = response.json()
    polygon_id = data["id"]
    assert data["name"] == "Test Polygon"
    assert data["client_id"] == 123

@pytest.mark.asyncio
async def test_get_all_polygons(client):
    response = await client.get("/api/polygons/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_by_client(client):
    response = await client.get("/api/polygons/client/123")
    assert response.status_code == 200
    data = response.json()
    assert all(p["client_id"] == 123 for p in data)

@pytest.mark.asyncio
async def test_update_polygon(client):
    global polygon_id
    response = await client.put(f"/api/polygons/{polygon_id}", json={
        "name": "Updated Polygon",
        "client_id": 123,
        "wkt": "POLYGON((0 0, 2 0, 2 2, 0 2, 0 0))"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Polygon"

@pytest.mark.asyncio
async def test_invalid_wkt(client):
    response = await client.post("/api/polygons/save", json={
        "name": "Bad WKT",
        "client_id": 999,
        "wkt": "INVALID((0 0))"
    })
    assert response.status_code == 400
    assert "Invalid WKT" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_polygon(client):
    global polygon_id
    response = await client.delete(f"/api/polygons/{polygon_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Deleted"

@pytest.mark.asyncio
async def test_delete_missing_polygon(client):
    response = await client.delete("/api/polygons/9999")
    assert response.status_code == 404
    