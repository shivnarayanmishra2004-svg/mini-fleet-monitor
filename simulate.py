import time
import requests
from datetime import datetime, timezone
import threading

API_URL = "http://127.0.0.1:8000"
NUM_DEVICES = 5
STOP_TARGET = "device-03"

def run_device(device_id: str, name: str):
    try:
        requests.post(f"{API_URL}/devices", json={"id": device_id, "name": name})
        print(f"[+] Registered {device_id}")
    except requests.ConnectionError:
        print("API not running. Please start the server first.")
        return
        
    cycles = 0
    while True:
        if device_id == STOP_TARGET and cycles >= 4:
            print(f"[!] {device_id} is STOPPING heartbeats to simulate an OFFLINE timeout.")
            while True:
                time.sleep(10) # Keep thread alive but silent
                
        now = datetime.now(timezone.utc).isoformat()
        try:
            requests.post(f"{API_URL}/devices/{device_id}/heartbeat", json={
                "timestamp": now,
                "status": "OK",
                "cpu_usage": 40 + cycles
            })
            print(f"[{device_id}] Heartbeat sent")
        except Exception as e:
            pass
            
        cycles += 1
        time.sleep(5)

if __name__ == "__main__":
    print("Starting simulator... Press Ctrl+C to stop.")
    for i in range(1, NUM_DEVICES + 1):
        dev_id = f"device-0{i}"
        t = threading.Thread(target=run_device, args=(dev_id, f"Simulator Device {i}"), daemon=True)
        t.start()
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulator stopped.")
