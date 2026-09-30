from fastapi.testclient import TestClient
from src.main import app
from src.store import devices, heartbeats
from datetime import datetime, timedelta, timezone

client = TestClient(app)

def setup_function():
    # Reset in-memory store before each test
    devices.clear()
    heartbeats.clear()

def test_register_device():
    response = client.post("/devices", json={"id": "dev-01", "name": "Lab Device"})
    assert response.status_code == 201
    
def test_heartbeat_updates_status():
    client.post("/devices", json={"id": "dev-01", "name": "Lab Device"})
    
    now = datetime.now(timezone.utc).isoformat()
    res = client.post("/devices/dev-01/heartbeat", json={"timestamp": now, "status": "OK"})
    assert res.status_code == 200
    
    status_res = client.get("/devices/dev-01")
    assert status_res.json()["status"] == "ONLINE"

def test_device_timeout_offline():
    client.post("/devices", json={"id": "dev-02", "name": "Old Device"})
    
    # Simulate a heartbeat 35 seconds ago
    past = (datetime.now(timezone.utc) - timedelta(seconds=35)).isoformat()
    client.post("/devices/dev-02/heartbeat", json={"timestamp": past, "status": "OK"})
    
    status_res = client.get("/devices/dev-02")
    assert status_res.json()["status"] == "OFFLINE"

def test_fleet_summary():
    client.post("/devices", json={"id": "dev-1", "name": "D1"})
    client.post("/devices", json={"id": "dev-2", "name": "D2"})
    
    now = datetime.now(timezone.utc).isoformat()
    client.post("/devices/dev-1/heartbeat", json={"timestamp": now, "status": "OK"})
    
    summary = client.get("/summary").json()
    assert summary["total"] == 2
    assert summary["online"] == 1
    assert summary["offline"] == 1
