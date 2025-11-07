"""
API Routes for network monitoring endpoints
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
from app.models.network import (
    NetworkDevice,
    NetworkStats,
    NetworkActivity,
    NetworkStatusResponse,
)
from app.services.network_monitor import NetworkMonitorService
from app.services.websocket_manager import manager

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


@router.get("/diagnostics")
async def get_diagnostics():
    """
    Get service diagnostics for monitoring and troubleshooting

    Returns:
    - Cache status and age
    - Device counts (cached vs known)
    - Activity and history counts
    - List of known device MAC addresses
    """
    try:
        diagnostics = network_monitor.get_diagnostics()
        diagnostics["websocket_connections"] = manager.get_connection_count()
        return diagnostics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/network")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time network updates

    Sends network status updates every 5 seconds and
    immediately on network changes
    """
    await manager.connect(websocket)
    last_device_state = {}

    try:
        while True:
            try:
                # Get current network status
                devices = await network_monitor.scan_network()
                stats = await network_monitor.get_system_stats()
                stats.connected_devices = len(devices)
                activities = await network_monitor.get_activities(limit=10)
                chart_data = network_monitor.generate_chart_data()

                # Prepare status data
                status_data = {
                    "stats": {
                        "connected_devices": stats.connected_devices,
                        "network_speed": stats.network_speed,
                        "data_usage": stats.data_usage,
                        "uptime": stats.uptime,
                    },
                    "devices": [device.model_dump(mode="json") for device in devices],
                    "activities": [act.model_dump(mode="json") for act in activities],
                    "chart_data": [
                        point.model_dump(mode="json") for point in chart_data
                    ],
                }

                # Check for device changes
                current_device_state = {
                    dev.mac: {"status": dev.status, "quality": dev.connection_quality}
                    for dev in devices
                }

                # Detect new/removed/changed devices
                for mac, state in current_device_state.items():
                    if mac not in last_device_state:
                        # New device
                        device = next(d for d in devices if d.mac == mac)
                        device_data = device.model_dump(mode="json")
                        await manager.broadcast_device_event("connected", device_data)
                    elif last_device_state[mac]["quality"] != state["quality"]:
                        # Quality changed
                        device = next(d for d in devices if d.mac == mac)
                        device_data = device.model_dump(mode="json")
                        await manager.broadcast_device_event(
                            "quality_change", device_data
                        )

                # Check for disconnected devices
                for mac in last_device_state:
                    if mac not in current_device_state:
                        await manager.broadcast_device_event(
                            "disconnected", {"mac": mac}
                        )

                last_device_state = current_device_state

                # Broadcast network update
                await manager.broadcast_network_update(status_data)

                # Wait 5 seconds before next update
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in WebSocket loop: {e}")
                await asyncio.sleep(5)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
