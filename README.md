# 🌍 Polygon Mapping App (FastAPI + PostGIS + Leaflet.js)

This is a full-stack mapping application that allows users to draw polygons on an OpenStreetMap interface, assign them to a client ID, and store them in a spatial PostGIS database. The app inetends to availl the user to draw polygons on a map and store them in a database, with the ability to assign a client ID to each polygon.So that the polygons are associated with a client ID and can be queried later. 
e.g: wharehouses, private stops in private route. It can also be used with  general polygons like ports, airports, etc.
![izmir](https://github.com/user-attachments/assets/2a828405-dcdc-441f-96ed-5e738b2df249) cargo parking  polygon 


- ✅ Draw and save polygons
- ✅ Assign client IDs and names
- ✅ Store polygons as `geometry(POLYGON, 4326)` in PostgreSQL
- ✅ REST API for full CRUD access
- ✅ Serve frontend and backend via FastAPI
- ✅ Import full OSM world map via `osm2pgsql` unless it is already imported
- ✅ Automatically reload frontend every 30 seconds
- ✅secure and scalable docker-compose setup
- ✅ Uses `asyncpg` for async database access
- ✅ Uses `GeoAlchemy2` for spatial data types
- ✅ Uses `Leaflet.js` for interactive mapping
- ✅ Uses `.env` for secure configuration

---

## 📁 Project Structure

``` .
├── backend
│   ├── database.py
│   ├── DOCKEFILE
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
├── db
│   └── DOCKERFILE
├── docker-compose.yml
├── frontend
│   ├── app.js
│   └── index.html
├── initdb
│   ├── 01-init-world.sql
│   └── 02-import-osm.sh
├── LICENSE
└── README.md

---
```

## ⚙️ Setup Instructions

1. **Clone the repository:**

```bash
    git clone https://github.com/davidgin/polygon-mapping.git
    cd polygon-mapping
```bash

P
2. **Create a `.env` file in the root directory:**
    POSTGRES_DB=spatial_db
    POSTGRES_USER=user
    POSTGRES_PASSWORD=pass123
    DATABASE_URL=postgresql+asyncpg://user:pass123@db/spatial_db

```bash
  # Start the services using Docker Compose
  docker-compose up --build -d
```bash

1. **Start the services:**

Run the following command to start the services using Docker Compose:

```bash
docker-compose up --build -d
```bash

This will:

- Download and import the full OSM world map.
- Initialize PostGIS and the polygon table.
- Serve the frontend on [http://localhost:8080](http://localhost:8080).

```markdown
## 🛠️ Development Notes

### Key Features:
- **Interactive Mapping**: Users can draw polygons directly on the map interface.
- **Client Association**: Each polygon can be assigned to a specific client ID for easy management.
- **Spatial Database**: Polygons are stored as `geometry(POLYGON, 4326)` in a PostGIS-enabled PostgreSQL database.
- **REST API**: Full CRUD operations are available for managing polygons and their associations.
- **Frontend-Backend Integration**: The application is served via FastAPI, with a responsive frontend powered by Leaflet.js.
- **Dockerized Setup**: The entire application is containerized for easy deployment and scalability.

### Additional Notes:
- The application automatically reloads the frontend every 30 seconds to reflect changes.
- Ensure that the `.env` file is correctly configured before starting the services.
- The OSM world map import is optional if the database is already populated.

```

   docker-compose up -d--build
   Downloads and imports the full OSM world map
   Initializes PostGIS and polygon table
   Serves the frontend on <http://localhost:8080>

```

## 🚀 Usage

 Access the App

    Visit: http://localhost:8080

    Draw polygons
    Name them
    Assign to client IDs
    View, delete, and edit polygons
    Automatically reload every 30 seconds

Access the API
🔌 API Endpoints Summary

    POST /api/polygons/save — Save polygon
    GET /api/polygons/all — Get all polygons
    GET /api/polygons/client/{id} — Get polygons for a client
    PUT /api/polygons/{id} — Update name/client/WKT
    DELETE /api/polygons/{id} — Delete polygon

📡

## 1. Get All Polygons  

**Endpoint:**  

GET /polygons/

**Description:**  
Returns a list of all polygons filtered by `client_id`.  

**Query Parameters:**  

- `client_id` (UUID, required) - The client ID to filter polygons.  

**Response Example:**  

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "client_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Sample Polygon",
    "geometry": "POLYGON((...))"
  }
]

2. Create a Polygon

Endpoint:

POST /polygons/

Description:
Creates a new polygon in the database.

Request Body:

{
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "New Polygon",
  "geometry": "POLYGON((...))"
}

Response Example:

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "New Polygon",
  "geometry": "POLYGON((...))"
}

3. Get a Polygon by ID

Endpoint:

GET /polygons/{polygon_id}

Description:
Retrieves a specific polygon using its ID.

Path Parameters:

    polygon_id (UUID, required) - The ID of the polygon to retrieve.

Response Example:

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Sample Polygon",
  "geometry": "POLYGON((...))"
}

4. Update a Polygon

Endpoint:

PUT /polygons/{polygon_id}

Description:
Updates an existing polygon.

Path Parameters:

    polygon_id (UUID, required) - The ID of the polygon to update.

Request Body:

{
  "name": "Updated Polygon",
  "geometry": "POLYGON((...))"
}

Response Example:

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Updated Polygon",
  "geometry": "POLYGON((...))"
}

5. Delete a Polygon

Endpoint:

DELETE /polygons/{polygon_id}

Description:
Deletes a polygon from the database.

Path Parameters:

    polygon_id (UUID, required) - The ID of the polygon to delete.

Response Example:

{
  "message": "Polygon deleted successfully"
}

6. Convert WKT to GeoJSON

Endpoint:

POST /convert/wkt-to-geojson/

Description:
Converts a Well-Known Text (WKT) geometry into GeoJSON format.

Request Body:

{
  "wkt": "POLYGON((...))"
}

Response Example:

{
  "type": "Polygon",
  "coordinates": [[[longitude, latitude], [longitude, latitude], ...]]
}

