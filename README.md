
# Polygon Mapping Project

## Setup Instructions

### 1️⃣ Generate the project
```bash
python3 generate_project.py
```

### 2️⃣ Navigate into the project
```bash
cd polygon-mapping
```

### 3️⃣ Build and start the project
```bash
docker-compose build --no-cache
docker-compose up -d
```

### 4️⃣ Verify backend logs
```bash
docker-compose logs backend
```

### 5️⃣ Access services
- Frontend: http://localhost:8081
- Backend Docs: http://localhost:8080/docs

### 6️⃣ Reset environment
```bash
docker-compose down -v
docker system prune -af --volumes
```

### 7️⃣ Ensure cleanup
```bash
rm -rf polygon-mapping
```

Then regenerate the project.

# human_for_code_review
