"""
WebSocket manager for real-time network updates
Manages WebSocket connections and broadcasts updates to connected clients
"""

import asyncio
from typing import Set
from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages to all
    connected clients
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.broadcast_lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        total = len(self.active_connections)
        print(f"✓ WebSocket client connected. Total connections: {total}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket"""
        self.active_connections.discard(websocket)
        total = len(self.active_connections)
        print(f"✗ WebSocket client disconnected. Total: {total}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected clients
        Automatically removes disconnected clients
        """
        if not self.active_connections:
            return

        async with self.broadcast_lock:
            disconnected = set()

            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to client: {e}")
                    disconnected.add(connection)

            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection)

    async def broadcast_network_update(self, data: dict):
        """
        Broadcast network status update to all connected clients
        """
        message = {
            "type": "network_update",
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        await self.broadcast(message)

    async def broadcast_device_event(self, event_type: str, device: dict):
        """
        Broadcast device-specific events
        (connected, disconnected, quality_change)
        """
        message = {
            "type": "device_event",
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "device": device,
        }
        await self.broadcast(message)

    async def broadcast_alert(self, alert: dict):
        """
        Broadcast new alert to all connected clients for real-time notifications
        """
        message = {
            "type": "alert",
            "timestamp": datetime.now().isoformat(),
            "alert": alert,
        }
        await self.broadcast(message)

    async def send_heartbeat(self, websocket: WebSocket):
        """
        Send heartbeat/ping to check connection health
        """
        try:
            ping_msg = {"type": "ping", "timestamp": datetime.now().isoformat()}
            await websocket.send_json(ping_msg)
        except Exception:
            self.disconnect(websocket)

    def get_connection_count(self) -> int:
        """Return the number of active connections"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
