from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from typing import List
from .models import DeviceCreate, Heartbeat, DeviceStatus, FleetSummary
from .store import devices, heartbeats, get_device_status
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fleet-api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Fleet API... Allocating resources.")
    yield
    logger.info("Graceful shutdown initiated. Cleaning up Fleet API resources...")
    devices.clear()
    heartbeats.clear()

app = FastAPI(title="Mini Device Fleet Monitor", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fleet Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            async function fetchData() {
                try {
                    const [summaryRes, devicesRes] = await Promise.all([
                        fetch('/summary'), fetch('/devices')
                    ]);
                    const summary = await summaryRes.json();
                    const devices = await devicesRes.json();

                    document.getElementById('total').innerText = summary.total;
                    document.getElementById('online').innerText = summary.online;
                    document.getElementById('offline').innerText = summary.offline;

                    let html = '';
                    devices.forEach(d => {
                        const isOnline = d.status === 'ONLINE';
                        const color = isOnline ? 'bg-green-500' : 'bg-red-500';
                        const ping = d.last_heartbeat ? new Date(d.last_heartbeat).toLocaleTimeString() : 'N/A';
                        html += `
                        <div class="bg-gray-800 p-4 rounded shadow flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-bold text-white">${d.name} <span class="text-xs text-gray-400">(${d.id})</span></h3>
                                <p class="text-sm text-gray-400">Last Ping: ${ping}</p>
                            </div>
                            <div class="px-3 py-1 rounded-full text-xs font-bold text-white ${color}">
                                ${d.status}
                            </div>
                        </div>`;
                    });
                    document.getElementById('device-list').innerHTML = html;
                } catch (e) { console.error('Fetch error:', e); }
            }
            setInterval(fetchData, 2000);
            window.onload = fetchData;
        </script>
    </head>
    <body class="bg-gray-900 text-gray-200 p-8 font-sans">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold mb-6 text-white">📡 Fleet Monitor Dashboard</h1>
            
            <div class="grid grid-cols-3 gap-4 mb-8">
                <div class="bg-gray-800 p-6 rounded shadow text-center border-t-4 border-blue-500">
                    <h2 class="text-xl text-gray-400">Total Devices</h2>
                    <p class="text-4xl font-bold text-white mt-2" id="total">-</p>
                </div>
                <div class="bg-gray-800 p-6 rounded shadow text-center border-t-4 border-green-500">
                    <h2 class="text-xl text-gray-400">Online</h2>
                    <p class="text-4xl font-bold text-green-400 mt-2" id="online">-</p>
                </div>
                <div class="bg-gray-800 p-6 rounded shadow text-center border-t-4 border-red-500">
                    <h2 class="text-xl text-gray-400">Offline</h2>
                    <p class="text-4xl font-bold text-red-400 mt-2" id="offline">-</p>
                </div>
            </div>

            <h2 class="text-2xl font-bold mb-4 text-white">Live Devices</h2>
            <div id="device-list" class="grid grid-cols-2 gap-4"></div>
        </div>
    </body>
    </html>
    """

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
    return [DeviceStatus(
        id=d.id, name=d.name, status=get_device_status(d_id),
        last_heartbeat=heartbeats[d_id].timestamp if d_id in heartbeats else None
    ) for d_id, d in devices.items()]

@app.get("/devices/{device_id}", response_model=DeviceStatus)
def get_device(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    hb = heartbeats.get(device_id)
    return DeviceStatus(
        id=devices[device_id].id, name=devices[device_id].name, status=get_device_status(device_id),
        last_heartbeat=hb.timestamp if hb else None
    )

@app.get("/summary", response_model=FleetSummary)
def get_summary():
    online = sum(1 for d in devices if get_device_status(d) == "ONLINE")
    return FleetSummary(total=len(devices), online=online, offline=len(devices) - online)