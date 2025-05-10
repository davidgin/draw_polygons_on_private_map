import os
import sys
import time
import subprocess
import urllib.request

OSM_SOURCES = {
    "test": {
        "url": "https://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf",
        "path": "/osm_data/new-york-latest.osm.pbf"
    },
    "prod": {
        "url": "https://planet.osm.org/pbf/planet-latest.osm.pbf",
        "path": "/osm_data/planet-latest.osm.pbf"
    }
}

def wait_for_postgres(user, db):
    print(f"⏳ Waiting for database '{db}' to be ready...")
    for _ in range(30):
        result = subprocess.run(
            ["pg_isready", "-U", user, "-d", db],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return
        time.sleep(2)
    print("❌ Database not ready in time")
    sys.exit(1)

def download_file_with_resume(url, path):
    print(f"📥 Downloading {url} to {path}...")
    tmp_path = path + ".part"
    resume_header = {}
    if os.path.exists(tmp_path):
        resume_size = os.path.getsize(tmp_path)
        resume_header = {"Range": f"bytes={resume_size}-"}
        print(f"🔄 Resuming from byte {resume_size}...")
    req = urllib.request.Request(url, headers=resume_header)
    with urllib.request.urlopen(req) as response, open(tmp_path, 'ab') as out:
        total = int(response.info().get("Content-Length", 0))
        downloaded = 0
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            done = int(50 * downloaded / total) if total else 0
            sys.stdout.write(f"\r[{'█' * done}{'.' * (50 - done)}]")
            sys.stdout.flush()
    print("\n✅ Download complete")
    os.rename(tmp_path, path)

def main():
    env = os.getenv("ENV", "test")
    user = os.getenv("POSTGRES_USER", "test")
    db = os.getenv("POSTGRES_DB", "test_db")
    print(f"📄 Using DB: {db}, USER: {user}, ENV: {env}***************************************************************************")

    print("🌍 Starting OSM import script...")
    print(f"🔧 Running in {env.upper()} mode")

    if env not in OSM_SOURCES:
        print("❌ Invalid ENV, expected 'test' or 'prod'")
        sys.exit(1)

    osm = OSM_SOURCES[env]
    marker = f"/var/lib/postgresql/.osm_imported_{env}"
    if os.path.exists(marker):
        print(f"✅ OSM already imported for {env}. Skipping.")
        return

    if not os.path.exists(os.path.dirname(osm["path"])):
        os.makedirs(os.path.dirname(osm["path"]), exist_ok=True)

    if not os.path.exists(osm["path"]):
        download_file_with_resume(osm["url"], osm["path"])
    else:
        print(f"📁 OSM file already exists: {osm['path']}")

    wait_for_postgres(user, db)

    print("📦 Importing OSM data into PostGIS...")
    subprocess.run([
        "osm2pgsql", "--create", "--slim",
        "--username", user,
        "--database", db,
        osm["path"]
    ], check=True)

    open(marker, "w").close()
    print(f"✅ OSM import complete for {env}.")

if __name__ == "__main__":
    main()
