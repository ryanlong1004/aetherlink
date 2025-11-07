#!/usr/bin/env python3
import asyncio
import websockets
import json


async def test_websocket():
    uri = "ws://localhost:8000/api/ws/network"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected to WebSocket!")

            # Wait for first message
            message = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(message)

            print(f"\n✓ Received message:")
            print(f"  Type: {data.get('type')}")
            print(f"  Timestamp: {data.get('timestamp')}")

            if data.get("type") == "network_update":
                devices = data.get("data", {}).get("devices", [])
                print(f"  Devices: {len(devices)}")
                if devices:
                    print(
                        f"  Sample device: {devices[0].get('name')} ({devices[0].get('ip')})"
                    )

            print("\n✓ WebSocket is working correctly!")

    except asyncio.TimeoutError:
        print("✗ Timeout waiting for message")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
