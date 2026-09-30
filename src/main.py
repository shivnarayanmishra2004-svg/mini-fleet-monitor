from fastapi import FastAPI, HTTPException
from typing import List
from .models import DeviceCreate, Heartbeat, DeviceStatus, FleetSummary
from .store import devices, heartbeats, get_device_status

app = FastAPI(title="Mini Device Fleet Monitor")

@app.post("/devices", status_code=201)
def register_device(device: DeviceCreate):
    if device.id in devices:
        raise HTTPException(status_code=400, detail="Device already registered")
    devices[device.id] = device
    return {"message": "Device registered successfully"}

@app.post("/devices/{device_id}/heartbeat")
def receive_heartbeat(device_id: str, heartbeat: Heartbeat):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    heartbeats[device_id] = heartbeat
    return {"message": "Heartbeat accepted"}

@app.get("/devices", response_model=List[DeviceStatus])
def list_devices():
    return [
        DeviceStatus(
            id=d.id, 
            name=d.name, 
            status=get_device_status(d_id),
            last_heartbeat=heartbeats[d_id].timestamp if d_id in heartbeats else None
        ) 
        for d_id, d in devices.items()
    ]

@app.get("/devices/{device_id}", response_model=DeviceStatus)
def get_device(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    hb = heartbeats.get(device_id)
    return DeviceStatus(
        id=devices[device_id].id, 
        name=devices[device_id].name, 
        status=get_device_status(device_id),
        last_heartbeat=hb.timestamp if hb else None
    )

@app.get("/summary", response_model=FleetSummary)
def get_summary():
    online = sum(1 for d in devices if get_device_status(d) == "ONLINE")
    return FleetSummary(
        total=len(devices), 
        online=online, 
        offline=len(devices) - online
    )