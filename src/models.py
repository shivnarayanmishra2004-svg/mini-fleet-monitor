from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DeviceCreate(BaseModel):
    id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Friendly name of the device")

class Heartbeat(BaseModel):
    timestamp: datetime
    status: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = {"extra": "allow"}

class DeviceStatus(BaseModel):
    id: str
    name: str
    status: str
    last_heartbeat: Optional[datetime] = None

class FleetSummary(BaseModel):
    total: int
    online: int
    offline: int
