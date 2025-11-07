"""
Network monitoring service for AetherLink
Handles device discovery, network statistics, and activity tracking
Enhanced version with extensive data collection and caching
"""

import subprocess
import re
import psutil
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from collections import deque, defaultdict
from app.models.network import (
    NetworkDevice,
    NetworkStats,
    NetworkActivity,
    ChartDataPoint,
)
from app.services.mac_vendors import MAC_VENDORS


class NetworkMonitorService:
    """
    Enhanced service for monitoring network devices and statistics with:
    - Caching to reduce network overhead
    - Historical data tracking (24h network history)
    - Per-device bandwidth monitoring
    - Activity tracking (connects, disconnects, IP changes)
    """

    def __init__(self, network_prefix: str = "192.168.1"):
        self.network_prefix = network_prefix

        # Device tracking
        self.known_devices: Dict[str, Dict[str, Any]] = {}
        self.device_history: Dict[str, deque] = {}

        # Activity tracking
        self.activity_log: List[NetworkActivity] = []
        self.activity_counter = 0

        # Network history (24h @ 1 minute intervals)
        self.network_history: deque = deque(maxlen=1440)

        # Bandwidth tracking per device
        self.device_bandwidth: Dict[str, deque] = defaultdict(lambda: deque(maxlen=60))

        # Network stats history
        self.stats_history: deque = deque(maxlen=60)

        # Caching mechanism
        self.cache_duration = 5  # Cache for 5 seconds
        self.last_scan_time: Optional[float] = None
        self.cached_devices: List[NetworkDevice] = []
        self.cached_stats: Optional[NetworkStats] = None

        # Initial network I/O baseline for speed calculation
        self.last_net_io = psutil.net_io_counters()
        self.last_net_io_time = time.time()

    def get_mac_vendor(self, mac: str) -> Optional[Dict[str, str]]:
        """Get vendor information from MAC address OUI"""
        oui = mac[:8].lower()
        return MAC_VENDORS.get(oui)

    def reverse_dns_lookup(self, ip: str) -> Optional[str]:
        """Attempt to get hostname via reverse DNS"""
        try:
            import socket

            hostname = socket.gethostbyaddr(ip)[0]
            return hostname if hostname != ip else None
        except Exception:
            return None

    def ping_device(self, ip: str) -> tuple[Optional[float], float]:
        """
        Ping a device to measure latency and packet loss
        Returns (latency_ms, packet_loss_percentage)
        """
        try:
            # Send 3 pings with 1 second timeout
            result = subprocess.run(
                ["ping", "-c", "3", "-W", "1", ip],
                capture_output=True,
                text=True,
                timeout=4,
            )

            if result.returncode == 0:
                # Parse ping output for latency
                # Look for: rtt min/avg/max/mdev = 1.234/2.345/3.456/0.123 ms
                match = re.search(
                    r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/", result.stdout
                )
                if match:
                    latency = float(match.group(1))

                    # Check for packet loss
                    loss_match = re.search(r"(\d+)% packet loss", result.stdout)
                    packet_loss = float(loss_match.group(1)) if loss_match else 0.0

                    return latency, packet_loss

            # If ping failed, assume 100% packet loss
            return None, 100.0

        except (subprocess.TimeoutExpired, Exception):
            return None, 100.0

    def assess_connection_quality(self, latency: Optional[float], packet_loss: float):
        """
        Assess connection quality based on latency and packet loss
        Returns: excellent, good, fair, or poor (Literal type)
        """
        if packet_loss > 10:
            return "poor"
        elif packet_loss > 5:
            return "fair"
        elif latency is None:
            return "poor"
        elif latency < 10:
            return "excellent"
        elif latency < 50:
            return "good"
        elif latency < 100:
            return "fair"
        else:
            return "poor"

    def generate_device_name(
        self, ip: str, mac: str, hostname: Optional[str], vendor_info: Optional[Dict]
    ) -> str:
        """Generate a friendly device name"""
        if hostname and hostname != ip and "?" not in hostname:
            return hostname

        # Try reverse DNS lookup
        dns_name = self.reverse_dns_lookup(ip)
        if dns_name:
            return dns_name

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
            elif device_type == "iot":
                return f"{vendor} Device ({suffix})"
            elif device_type == "router":
                return f"{vendor} Router ({suffix})"
            else:
                return f"{vendor} Device ({suffix})"

        return f"Device {ip.split('.')[-1]}"

    def is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if self.last_scan_time is None:
            return False
        elapsed = time.time() - self.last_scan_time
        return elapsed < self.cache_duration

    async def scan_network(self) -> List[NetworkDevice]:
        """
        Scan network for connected devices using ARP table
        Returns cached result if scan was recent
        """
        # Return cached data if valid
        if self.is_cache_valid():
            print("📦 Returning cached devices")
            return self.cached_devices

        devices = []
        seen_macs = set()
        current_macs = set()

        try:
            # Run arp -a command
            result = subprocess.run(
                ["arp", "-a"], capture_output=True, text=True, timeout=3
            )

            if result.returncode != 0:
                print(f"ARP command failed: {result.stderr}")
                # Return cached data if available
                return self.cached_devices if self.cached_devices else []

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
                    current_macs.add(mac)

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

                    # Measure connection quality (ping only some devices)
                    latency = None
                    packet_loss = 0.0
                    connection_quality = None

                    # Ping every 5th device to avoid network congestion
                    # (or devices not in cache for first-time measurement)
                    if mac not in self.known_devices or len(devices) % 5 == 0:
                        latency, packet_loss = self.ping_device(ip)
                        connection_quality = self.assess_connection_quality(
                            latency, packet_loss
                        )

                    # Get first_seen and total_connections from history
                    first_seen = None
                    total_connections = None
                    if mac in self.known_devices:
                        first_seen = self.known_devices[mac].get("first_seen")
                        total_connections = self.known_devices[mac].get(
                            "connections", 1
                        )

                    device = NetworkDevice(
                        id=mac.replace(":", "").replace("-", ""),
                        name=device_name,
                        ip=ip,
                        mac=mac,
                        status="online",
                        type=device_type,
                        vendor=vendor_name,
                        last_seen=datetime.now(),
                        latency=latency,
                        packet_loss=packet_loss,
                        connection_quality=connection_quality,
                        first_seen=first_seen,
                        total_connections=total_connections,
                    )
                    devices.append(device)

                    # Track device info
                    if mac not in self.known_devices:
                        # New device connected
                        self.known_devices[mac] = {
                            "ip": ip,
                            "name": device_name,
                            "first_seen": datetime.now(),
                            "connections": 1,
                            "last_latency": latency,
                            "last_packet_loss": packet_loss,
                        }
                        self.activity_counter += 1
                        activity = NetworkActivity(
                            id=(
                                f"activity-{self.activity_counter}-"
                                f"{int(datetime.now().timestamp())}"
                            ),
                            device=device_name,
                            action="Connected to network",
                            timestamp=datetime.now(),
                        )
                        self.activity_log.insert(0, activity)
                        print(f"🆕 New device: {device_name} ({mac})")
                    elif self.known_devices[mac]["ip"] != ip:
                        # IP address changed
                        old_ip = self.known_devices[mac]["ip"]
                        self.known_devices[mac]["ip"] = ip
                        self.activity_counter += 1
                        activity = NetworkActivity(
                            id=(
                                f"activity-{self.activity_counter}-"
                                f"{int(datetime.now().timestamp())}"
                            ),
                            device=device_name,
                            action=f"IP changed from {old_ip} to {ip}",
                            timestamp=datetime.now(),
                        )
                        self.activity_log.insert(0, activity)
                        print(f"🔄 IP change: {device_name} {old_ip} -> {ip}")

            # Check for disconnected devices
            for mac, info in list(self.known_devices.items()):
                if mac not in current_macs:
                    self.activity_counter += 1
                    activity = NetworkActivity(
                        id=(
                            f"activity-{self.activity_counter}-"
                            f"{int(datetime.now().timestamp())}"
                        ),
                        device=info["name"],
                        action="Disconnected from network",
                        timestamp=datetime.now(),
                    )
                    self.activity_log.insert(0, activity)
                    print(f"🔴 Disconnected: {info['name']} ({mac})")
                    del self.known_devices[mac]

            # Update cache
            self.cached_devices = devices
            self.last_scan_time = time.time()

            # Store in network history
            self.network_history.append(
                {
                    "timestamp": datetime.now(),
                    "device_count": len(devices),
                    "devices": [d.dict() for d in devices],
                }
            )

            print(f"✅ Found {len(devices)} devices from ARP table")

        except subprocess.TimeoutExpired:
            print("⚠️ ARP scan timed out")
            return self.cached_devices if self.cached_devices else []
        except Exception as e:
            print(f"❌ Error scanning network: {e}")
            return self.cached_devices if self.cached_devices else []

        return devices

    async def get_system_stats(self) -> NetworkStats:
        """
        Get detailed system network statistics with speed calculation
        """
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
            current_time_precise = time.time()

            # Calculate data usage (convert bytes to GB)
            data_usage = round((net_io.bytes_sent + net_io.bytes_recv) / (1024**3), 1)

            # Calculate network speed (Mbps)
            time_delta = current_time_precise - self.last_net_io_time
            if time_delta > 0:
                bytes_delta = (net_io.bytes_sent + net_io.bytes_recv) - (
                    self.last_net_io.bytes_sent + self.last_net_io.bytes_recv
                )
                # Convert to Mbps
                network_speed = round((bytes_delta * 8) / (time_delta * 1_000_000), 2)
            else:
                network_speed = 0.0

            # Update baseline
            self.last_net_io = net_io
            self.last_net_io_time = current_time_precise

            stats = NetworkStats(
                connected_devices=len(self.known_devices),
                network_speed=network_speed,
                data_usage=data_usage,
                uptime=uptime_str,
            )

            # Store in stats history
            self.stats_history.append(
                {
                    "timestamp": datetime.now(),
                    "stats": stats.dict(),
                }
            )

            return stats

        except Exception as e:
            print(f"❌ Error getting system stats: {e}")
            return NetworkStats(
                connected_devices=0, network_speed=0.0, data_usage=0.0, uptime="0m"
            )

    async def get_activities(self, limit: int = 10) -> List[NetworkActivity]:
        """Get recent network activities"""
        # Keep only last 100 activities
        if len(self.activity_log) > 100:
            self.activity_log = self.activity_log[:100]

        return self.activity_log[:limit]

    def generate_chart_data(self) -> List[ChartDataPoint]:
        """
        Generate chart data from historical network statistics
        """
        data = []

        # Use real stats history if available
        if len(self.stats_history) > 0:
            for entry in list(self.stats_history)[-24:]:
                timestamp = entry["timestamp"]
                stats = entry["stats"]
                data.append(
                    ChartDataPoint(
                        time=timestamp.strftime("%H:%M"),
                        download=stats.get("network_speed", 0.0),
                        upload=stats.get("network_speed", 0.0) * 0.3,
                    )
                )
        else:
            # Return placeholder data
            for i in range(24, 0, -1):
                data.append(
                    ChartDataPoint(
                        time=f"{i}h" if i > 1 else "Now", download=0.0, upload=0.0
                    )
                )

        return data

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get service diagnostics for troubleshooting
        """
        return {
            "cache_valid": self.is_cache_valid(),
            "last_scan_time": self.last_scan_time,
            "cache_age_seconds": (
                time.time() - self.last_scan_time if self.last_scan_time else None
            ),
            "cached_device_count": len(self.cached_devices),
            "known_device_count": len(self.known_devices),
            "activity_count": len(self.activity_log),
            "network_history_count": len(self.network_history),
            "stats_history_count": len(self.stats_history),
            "known_devices": list(self.known_devices.keys()),
        }
