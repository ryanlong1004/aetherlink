"""
Network monitoring service for AetherLink
Handles device discovery, network statistics, and activity tracking
"""

import subprocess
import re
import psutil
from datetime import datetime
from typing import List, Dict, Optional
from app.models.network import (
    NetworkDevice,
    NetworkStats,
    NetworkActivity,
    ChartDataPoint,
)


# MAC OUI to Vendor mapping (abbreviated - expand as needed)
MAC_VENDORS = {
    # Apple
    "00:03:93": {"vendor": "Apple", "type": "phone"},
    "a4:83:e7": {"vendor": "Apple", "type": "phone"},
    "f0:99:b6": {"vendor": "Apple", "type": "phone"},
    "ac:87:a3": {"vendor": "Apple", "type": "phone"},
    # Amazon
    "00:71:47": {"vendor": "Amazon", "type": "speaker"},
    "38:f7:3d": {"vendor": "Amazon", "type": "speaker"},
    "68:37:e9": {"vendor": "Amazon", "type": "speaker"},
    "a0:02:dc": {"vendor": "Amazon", "type": "tv"},
    # Roku
    "b0:a7:37": {"vendor": "Roku", "type": "tv"},
    "d8:31:34": {"vendor": "Roku", "type": "tv"},
    # Sony
    "30:f9:ed": {"vendor": "Sony", "type": "tv"},
    "54:42:49": {"vendor": "Sony", "type": "tv"},
    # Samsung
    "00:12:fb": {"vendor": "Samsung", "type": "tv"},
    "e8:50:8b": {"vendor": "Samsung", "type": "tv"},
    # Google/Nest
    "1c:f2:9a": {"vendor": "Google", "type": "speaker"},
    "54:60:09": {"vendor": "Google", "type": "speaker"},
}


class NetworkMonitorService:
    """Service for monitoring network devices and statistics"""

    def __init__(self, network_prefix: str = "192.168.1"):
        self.network_prefix = network_prefix
        self.known_devices: set = set()
        self.activity_log: List[NetworkActivity] = []
        self.network_history: List[Dict] = []
        self.activity_counter = 0

    def get_mac_vendor(self, mac: str) -> Optional[Dict[str, str]]:
        """Get vendor information from MAC address OUI"""
        oui = mac[:8].lower()
        return MAC_VENDORS.get(oui)

    def generate_device_name(
        self, ip: str, mac: str, hostname: Optional[str], vendor_info: Optional[Dict]
    ) -> str:
        """Generate a friendly device name"""
        if hostname and hostname != ip and "?" not in hostname:
            return hostname

        if vendor_info:
            suffix = ip.split(".")[-1]
            vendor = vendor_info["vendor"]
            device_type = vendor_info.get("type", "device")

            if device_type == "phone":
                return f"{vendor} iPhone ({suffix})"
            elif device_type == "laptop":
                return f"{vendor} Mac ({suffix})"
            elif device_type == "tv":
                return f"{vendor} TV ({suffix})"
            elif device_type == "speaker":
                return f"{vendor} Speaker ({suffix})"
            else:
                return f"{vendor} Device ({suffix})"

        return f"Device {ip.split('.')[-1]}"

    async def scan_network(self) -> List[NetworkDevice]:
        """Scan network for connected devices using ARP table"""
        devices = []
        seen_macs = set()

        try:
            # Run arp -a command
            result = subprocess.run(
                ["arp", "-a"], capture_output=True, text=True, timeout=3
            )

            if result.returncode != 0:
                print(f"ARP command failed: {result.stderr}")
                return []

            lines = result.stdout.split("\n")
            print(f"📋 Found {len(lines)} ARP entries")

            for line in lines:
                # Match IP address: (192.168.1.x)
                ip_match = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)", line)
                # Match MAC address
                mac_match = re.search(
                    r"([0-9a-f]{1,2}[:-]){5}[0-9a-f]{1,2}", line, re.IGNORECASE
                )

                if ip_match and mac_match:
                    ip = ip_match.group(1)
                    mac = mac_match.group(0).lower()

                    # Skip if already seen or invalid
                    if (
                        mac in seen_macs
                        or mac == "00:00:00:00:00:00"
                        or "incomplete" in line.lower()
                    ):
                        continue

                    seen_macs.add(mac)

                    # Extract hostname if available
                    hostname_match = re.match(r"^(\S+)\s+\(", line)
                    hostname = hostname_match.group(1) if hostname_match else None

                    # Get vendor info
                    vendor_info = self.get_mac_vendor(mac)

                    # Generate device name
                    device_name = self.generate_device_name(
                        ip, mac, hostname, vendor_info
                    )
                    device_type = (
                        vendor_info.get("type", "default") if vendor_info else "default"
                    )
                    vendor_name = vendor_info.get("vendor") if vendor_info else None

                    device = NetworkDevice(
                        id=mac.replace(":", "").replace("-", ""),
                        name=device_name,
                        ip=ip,
                        mac=mac,
                        status="online",
                        type=device_type,
                        vendor=vendor_name,
                        last_seen=datetime.now(),
                    )
                    devices.append(device)

                    # Track new devices for activity log
                    if mac not in self.known_devices:
                        self.known_devices.add(mac)
                        self.activity_counter += 1
                        activity = NetworkActivity(
                            id=f"activity-{self.activity_counter}-{int(datetime.now().timestamp())}",
                            device=device_name,
                            action="Connected to network",
                            timestamp=datetime.now(),
                        )
                        self.activity_log.insert(0, activity)

            print(f"✅ Found {len(devices)} devices from ARP table")

        except subprocess.TimeoutExpired:
            print("⚠️ ARP scan timed out")
        except Exception as e:
            print(f"❌ Error scanning network: {e}")

        return devices

    async def get_system_stats(self) -> NetworkStats:
        """Get system network statistics"""
        try:
            # Get uptime
            uptime_seconds = int(psutil.boot_time())
            current_time = int(datetime.now().timestamp())
            uptime = current_time - uptime_seconds

            # Format uptime
            days = uptime // 86400
            hours = (uptime % 86400) // 3600
            minutes = (uptime % 3600) // 60

            if days > 0:
                uptime_str = f"{days}d {hours}h"
            elif hours > 0:
                uptime_str = f"{hours}h {minutes}m"
            else:
                uptime_str = f"{minutes}m"

            # Get network I/O stats
            net_io = psutil.net_io_counters()

            # Calculate data usage (convert bytes to GB)
            data_usage = round((net_io.bytes_sent + net_io.bytes_recv) / (1024**3), 1)

            # Network speed (simplified - would need historical data for accurate speed)
            network_speed = 0.0  # This would be calculated from historical data

            return NetworkStats(
                connected_devices=len(self.known_devices),
                network_speed=network_speed,
                data_usage=data_usage,
                uptime=uptime_str,
            )

        except Exception as e:
            print(f"❌ Error getting system stats: {e}")
            return NetworkStats(
                connected_devices=0, network_speed=0.0, data_usage=0.0, uptime="0m"
            )

    async def get_activities(self, limit: int = 10) -> List[NetworkActivity]:
        """Get recent network activities"""
        # Keep only last 50 activities
        if len(self.activity_log) > 50:
            self.activity_log = self.activity_log[:50]

        return self.activity_log[:limit]

    def generate_chart_data(self) -> List[ChartDataPoint]:
        """Generate chart data for network traffic"""
        # For now, return mock data
        # In production, this would use historical network stats
        data = []
        for i in range(24, 0, -1):
            data.append(
                ChartDataPoint(
                    time=f"{i}h" if i > 1 else "Now", download=0.0, upload=0.0
                )
            )
        return data
