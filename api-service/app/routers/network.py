"""
API Routes for network monitoring endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.network import (
    NetworkDevice,
    NetworkStats,
    NetworkActivity,
    NetworkStatusResponse,
)
from app.services.network_monitor import NetworkMonitorService

router = APIRouter(prefix="/api", tags=["network"])

# Initialize network monitor service
network_monitor = NetworkMonitorService()


@router.get("/network/status", response_model=NetworkStatusResponse)
async def get_network_status():
    """
    Get complete network status including devices, stats, and activities
    """
    try:
        devices = await network_monitor.scan_network()
        stats = await network_monitor.get_system_stats()
        stats.connected_devices = len(devices)
        activities = await network_monitor.get_activities(limit=10)
        chart_data = network_monitor.generate_chart_data()

        return NetworkStatusResponse(
            stats=stats, devices=devices, activities=activities, chart_data=chart_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices", response_model=List[NetworkDevice])
async def get_devices():
    """
    Get list of all connected devices
    """
    try:
        devices = await network_monitor.scan_network()
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}", response_model=NetworkDevice)
async def get_device(device_id: str):
    """
    Get specific device by ID (MAC address without colons)
    """
    try:
        devices = await network_monitor.scan_network()
        for device in devices:
            if device.id == device_id:
                return device
        raise HTTPException(
            status_code=404, detail=f"Device with ID {device_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=NetworkStats)
async def get_stats():
    """
    Get network statistics (speed, uptime, data usage)
    """
    try:
        devices = await network_monitor.scan_network()
        stats = await network_monitor.get_system_stats()
        stats.connected_devices = len(devices)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activities", response_model=List[NetworkActivity])
async def get_activities(limit: int = 10):
    """
    Get recent network activities

    - **limit**: Number of activities to return (default: 10, max: 50)
    """
    if limit > 50:
        limit = 50
    try:
        activities = await network_monitor.get_activities(limit=limit)
        return activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
