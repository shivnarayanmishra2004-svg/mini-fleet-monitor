import time, requests, threading, signal
from datetime import datetime, timezone

API_URL = "http://127.0.0.1:8000"
NUM_DEVICES = 5
STOP_TARGET = "device-03"
shutdown_event = threading.Event()

def run_device(device_id, name):
    while not shutdown_event.is_set():
        try:
            requests.post(f"{API_URL}/devices", json={"id": device_id, "name": name})
            print(f"[+] Registered {device_id}", flush=True)
            break
        except requests.ConnectionError:
            shutdown_event.wait(2)
            
    cycles = 0
    while not shutdown_event.is_set():
        if device_id == STOP_TARGET and cycles >= 4:
            shutdown_event.wait(5)
            continue
            
        now = datetime.now(timezone.utc).isoformat()
        try:
            requests.post(f"{API_URL}/devices/{device_id}/heartbeat", json={"timestamp": now, "status": "OK"})
            print(f"[{device_id}] Heartbeat sent", flush=True)
        except Exception:
            pass
            
        cycles += 1
        shutdown_event.wait(5)

def handle_sigterm(*args):
    shutdown_event.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)
    threads = [threading.Thread(target=run_device, args=(f"device-0{i}", f"Device {i}")) for i in range(1, NUM_DEVICES + 1)]
    for t in threads: t.start()
    for t in threads: t.join()