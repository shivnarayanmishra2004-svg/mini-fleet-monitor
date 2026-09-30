from datetime import datetime, timezone
import os

# In-memory data stores
devices = {}
heartbeats = {}

TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 30))

def get_device_status(device_id: str) -> str:
    if device_id not in heartbeats:
        return "OFFLINE"
    
    last_hb = heartbeats[device_id].timestamp
    # Ensure timezone awareness for safe comparison
    if last_hb.tzinfo is None:
        last_hb = last_hb.replace(tzinfo=timezone.utc)
        
    now = datetime.now(timezone.utc)
    diff = (now - last_hb).total_seconds()
    
    return "ONLINE" if diff <= TIMEOUT_SECONDS else "OFFLINE"
