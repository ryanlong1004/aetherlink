from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class NetworkDevice(BaseModel):
    """Network device model with connection quality metrics"""

    id: str
    name: str
    ip: str
    mac: str
    status: Literal["online", "offline"]
    type: str
    vendor: Optional[str] = None
    last_seen: Optional[datetime] = None
    # Connection quality metrics
    latency: Optional[float] = None  # ms
    packet_loss: Optional[float] = None  # percentage
    connection_quality: Optional[Literal["excellent", "good", "fair", "poor"]] = None
    first_seen: Optional[datetime] = None
    total_connections: Optional[int] = None

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
                "latency": 12.5,
                "packet_loss": 0.0,
                "connection_quality": "excellent",
                "first_seen": "2025-11-05T08:00:00",
                "total_connections": 15,
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


class AlertType(str, Enum):
    """Alert type enumeration"""

    NEW_DEVICE = "new_device"
    DEVICE_OFFLINE = "device_offline"
    POOR_CONNECTION = "poor_connection"
    DUPLICATE_IP = "duplicate_ip"
    HIGH_LATENCY = "high_latency"
    PACKET_LOSS = "packet_loss"


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert(BaseModel):
    """Network alert model"""

    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert-1",
                "type": "poor_connection",
                "severity": "warning",
                "title": "Poor Connection Quality",
                "message": "Device iPhone 13 has high latency (250ms)",
                "device_id": "aabbccddeeff",
                "device_name": "iPhone 13",
                "timestamp": "2025-11-06T18:30:00",
                "acknowledged": False,
            }
        }


class AlertRule(BaseModel):
    """Alert rule configuration"""

    id: str
    type: AlertType
    enabled: bool = True
    # Thresholds
    latency_threshold: Optional[float] = 200.0  # ms
    packet_loss_threshold: Optional[float] = 10.0  # percentage
    offline_threshold: Optional[int] = 300  # seconds

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rule-1",
                "type": "high_latency",
                "enabled": True,
                "latency_threshold": 200.0,
            }
        }


class AlertsResponse(BaseModel):
    """Alerts API response"""

    alerts: list[Alert]
    unacknowledged_count: int
