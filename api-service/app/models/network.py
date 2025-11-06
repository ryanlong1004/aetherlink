from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class NetworkDevice(BaseModel):
    """Network device model"""

    id: str
    name: str
    ip: str
    mac: str
    status: Literal["online", "offline"]
    type: str
    vendor: Optional[str] = None
    last_seen: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "aabbccddeeff",
                "name": "iPhone 13",
                "ip": "192.168.1.10",
                "mac": "aa:bb:cc:dd:ee:ff",
                "status": "online",
                "type": "phone",
                "vendor": "Apple",
                "last_seen": "2025-11-06T18:30:00",
            }
        }


class NetworkStats(BaseModel):
    """Network statistics model"""

    connected_devices: int
    network_speed: float  # Mbps
    data_usage: float  # GB
    uptime: str

    class Config:
        json_schema_extra = {
            "example": {
                "connected_devices": 12,
                "network_speed": 450.5,
                "data_usage": 120.6,
                "uptime": "47d 12h",
            }
        }


class NetworkActivity(BaseModel):
    """Network activity model"""

    id: str
    device: str
    action: str
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "activity-1",
                "device": "iPhone 13",
                "action": "Connected to network",
                "timestamp": "2025-11-06T18:30:00",
            }
        }


class ChartDataPoint(BaseModel):
    """Chart data point model"""

    time: str
    download: float
    upload: float


class NetworkStatusResponse(BaseModel):
    """Complete network status response"""

    stats: NetworkStats
    devices: list[NetworkDevice]
    activities: list[NetworkActivity]
    chart_data: list[ChartDataPoint]

    class Config:
        json_schema_extra = {
            "example": {
                "stats": {
                    "connected_devices": 12,
                    "network_speed": 450.5,
                    "data_usage": 120.6,
                    "uptime": "47d 12h",
                },
                "devices": [
                    {
                        "id": "aabbccddeeff",
                        "name": "iPhone 13",
                        "ip": "192.168.1.10",
                        "mac": "aa:bb:cc:dd:ee:ff",
                        "status": "online",
                        "type": "phone",
                        "vendor": "Apple",
                    }
                ],
                "activities": [
                    {
                        "id": "activity-1",
                        "device": "iPhone 13",
                        "action": "Connected to network",
                        "timestamp": "2025-11-06T18:30:00",
                    }
                ],
                "chart_data": [{"time": "Now", "download": 50.5, "upload": 10.2}],
            }
        }
