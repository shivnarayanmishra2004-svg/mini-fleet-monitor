import time
import requests
from datetime import datetime, timezone
import threading

API_URL = "http://127.0.0.1:8000"
NUM_DEVICES = 5

def run_device(device_id: str, name: str):
    try:
        requests.post(f"{API_URL}/devices", json={"id": device_id, "name": name})
        print(f"[+] Registered {device_id}")
    except requests.ConnectionError:
        print(f"Failed to connect. Is the API running at {API_URL}?")
        return

    cycles = 0
    while True:
        if device_id == "device-03" and cycles >= 4:
            print(f"[!] {device_id} stopping heartbeats to simulate OFFLINE status.")
            break
            
        now = datetime.now(timezone.utc).isoformat()
        try:
            requests.post(f"{API_URL}/devices/{device_id}/heartbeat", json={"timestamp": now, "status": "OK"})
            print(f"[{device_id}] Heartbeat sent")
        except Exception:
            pass
            
        cycles += 1
        time.sleep(5)

if __name__ == "__main__":
    print(f"Starting simulator connected to {API_URL}...")
    threads = []
    for i in range(1, NUM_DEVICES + 1):
        t = threading.Thread(target=run_device, args=(f"device-0{i}", f"Device {i}"))
        t.daemon = True
        t.start()
        threads.append(t)
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")