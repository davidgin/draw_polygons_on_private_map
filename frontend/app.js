const map = L.map("map").setView([0, 0], 2);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

const drawn = new L.FeatureGroup();
map.addLayer(drawn);

const drawControl = new L.Control.Draw({ edit: { featureGroup: drawn }, draw: { polygon: true } });
map.addControl(drawControl);

map.on("draw:created", function (e) {
  const layer = e.layer;
  drawn.addLayer(layer);

  const clientId = document.getElementById("client_id").value || null;
  const name = document.getElementById("polygon_name").value.trim();
  const coords = layer.getLatLngs()[0].map(p => `${p.lng} ${p.lat}`);
  const wkt = "POLYGON((" + coords.join(", ") + "))";

  if (!name) return (document.getElementById("msg").textContent = "Polygon name is required");

  fetch("/api/polygons/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: clientId, name, wkt }),
  }).then(() => alert("Polygon saved"));
});

function drawPolygon(polygon) {
  const coords = polygon.polygon.replace("POLYGON((", "").replace("))", "")
    .split(", ").map(pair => pair.split(" ").map(Number)).map(([lng, lat]) => [lat, lng]);
  const poly = L.polygon(coords, { color: "blue" }).addTo(drawn);
  poly.bindPopup(`Name: ${polygon.name} | ID: ${polygon.id}`);
  poly.on("click", () => {
    if (confirm("Delete this polygon?")) {
      fetch(`/api/polygons/${polygon.id}`, { method: "DELETE" })
        .then(() => { alert("Deleted"); reload(); });
    }
  });
  poly.on("dblclick", () => {
    const newName = prompt("New name:", polygon.name);
    if (newName) {
      fetch(`/api/polygons/${polygon.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName, client_id: polygon.client_id, wkt: polygon.polygon }),
      }).then(() => reload());
    }
  });
}

function loadAll() {
  fetch("/api/polygons/all").then(res => res.json()).then(data => data.forEach(drawPolygon));
}

function loadClient() {
  const id = document.getElementById("client_id").value;
  if (!id) return alert("Enter client ID");
  fetch(`/api/polygons/client/${id}`).then(res => res.json()).then(data => data.forEach(drawPolygon));
}

function reload() {
  drawn.clearLayers();
  loadAll();
}

setInterval(reload, 30000);
