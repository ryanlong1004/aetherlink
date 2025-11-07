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
from app.services.alert_manager import AlertManager
from app.services.websocket_manager import manager as websocket_manager


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
        self.network_interface = self._detect_network_interface()

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

        # Alert management
        self.alert_manager = AlertManager()

    def _detect_network_interface(self) -> Optional[str]:
        """
        Auto-detect the active network interface for arp-scan
        Returns the first active non-loopback interface
        """
        try:
            # Get all network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()

            # Priority order for interface names
            priority = ["eth0", "wlan0", "en0", "ens33", "enp0s3"]

            # First try priority interfaces if they exist and are up
            for iface_name in priority:
                if iface_name in interfaces and iface_name in stats:
                    if stats[iface_name].isup:
                        # Skip loopback
                        if iface_name.lower() != "lo":
                            print(f"🌐 Detected network interface: {iface_name}")
                            return iface_name

            # Fall back to first active non-loopback interface
            for iface_name, iface_stats in stats.items():
                if iface_stats.isup:
                    # Skip loopback, docker, and virtual interfaces
                    skip_names = ["docker", "veth", "br-", "lo"]
                    if not any(x in iface_name.lower() for x in skip_names):
                        print(f"🌐 Detected network interface: {iface_name}")
                        return iface_name

            print("⚠️ No active network interface found")
            return None

        except Exception as e:
            print(f"❌ Error detecting network interface: {e}")
            return None

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

    def _scan_with_arp_scan(self) -> Optional[List[Dict[str, Any]]]:
        """
        Use arp-scan for fast, active network scanning
        Returns list of dicts with {ip, mac, vendor, response_time}
        Returns None if arp-scan fails
        """
        if not self.network_interface:
            print("⚠️ No network interface detected for arp-scan")
            return None

        try:
            # Run arp-scan with retry and timeout
            # Note: Requires cap_net_raw capability or sudo
            cmd = [
                "arp-scan",
                "--interface",
                self.network_interface,
                "--localnet",
                "--retry",
                "2",
                "--timeout",
                "500",
                "--quiet",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                print(f"⚠️ arp-scan failed: {result.stderr}")
                return None

            devices = []
            duplicate_ips = []

            # Parse arp-scan output
            # Format: IP\tMAC\tVendor\tResponse_time
            # Example: 192.168.1.1\t00:11:22:33:44:55\tApple\t0.123ms
            lines = result.stdout.strip().split("\n")

            for line in lines:
                # Skip empty lines and headers
                if not line or line.startswith("#"):
                    continue

                # Check for duplicate IP warnings
                if "DUP" in line or "duplicate" in line.lower():
                    # Extract IP from duplicate warning
                    ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                    if ip_match:
                        duplicate_ips.append(ip_match.group(1))
                    continue

                # Parse device line
                parts = line.split("\t")
                if len(parts) < 2:
                    continue

                ip = parts[0].strip()
                mac = parts[1].strip().lower()
                vendor = parts[2].strip() if len(parts) > 2 else None

                # Parse response time (e.g., "0.123ms")
                response_time = None
                if len(parts) > 3:
                    time_str = parts[3].strip()
                    time_match = re.search(r"([\d.]+)", time_str)
                    if time_match:
                        response_time = float(time_match.group(1))

                devices.append(
                    {
                        "ip": ip,
                        "mac": mac,
                        "vendor": vendor,
                        "response_time": response_time,
                    }
                )

            # Log duplicate IPs
            for dup_ip in duplicate_ips:
                self.activity_counter += 1
                activity = NetworkActivity(
                    id=f"activity-{self.activity_counter}-"
                    f"{int(datetime.now().timestamp())}",
                    device=f"Multiple devices at {dup_ip}",
                    action="⚠️ Duplicate IP address detected",
                    timestamp=datetime.now(),
                )
                self.activity_log.insert(0, activity)
                print(f"⚠️ Duplicate IP detected: {dup_ip}")

            print(f"✅ arp-scan found {len(devices)} devices")
            return devices

        except subprocess.TimeoutExpired:
            print("⚠️ arp-scan timed out")
            return None
        except FileNotFoundError:
            print("⚠️ arp-scan not found in PATH")
            return None
        except Exception as e:
            print(f"⚠️ arp-scan error: {e}")
            return None

    def _scan_with_arp_table(self) -> List[Dict[str, Any]]:
        """
        Fallback: Use traditional arp -a scanning
        Returns list of dicts with {ip, mac, hostname}
        """
        devices = []

        try:
            result = subprocess.run(
                ["arp", "-a"], capture_output=True, text=True, timeout=3
            )

            if result.returncode != 0:
                return devices

            for line in result.stdout.split("\n"):
                ip_match = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)", line)
                mac_match = re.search(
                    r"([0-9a-f]{1,2}[:-]){5}[0-9a-f]{1,2}", line, re.IGNORECASE
                )

                if ip_match and mac_match:
                    ip = ip_match.group(1)
                    mac = mac_match.group(0).lower()

                    if mac == "00:00:00:00:00:00":
                        continue
                    if "incomplete" in line.lower():
                        continue

                    hostname_match = re.match(r"^(\S+)\s+\(", line)
                    hostname = hostname_match.group(1) if hostname_match else None

                    devices.append({"ip": ip, "mac": mac, "hostname": hostname})

            print(f"✅ arp -a found {len(devices)} devices")
            return devices

        except Exception as e:
            print(f"❌ Error with arp -a: {e}")
            return devices

    async def scan_network(self) -> List[NetworkDevice]:
        """
        Scan network for connected devices using arp-scan (with fallback)
        Returns cached result if scan was recent
        """
        # Return cached data if valid
        if self.is_cache_valid():
            print("📦 Returning cached devices")
            return self.cached_devices

        devices = []
        seen_macs = set()
        current_macs = set()

        # Try arp-scan first (faster, more reliable)
        scan_results = self._scan_with_arp_scan()

        # Fall back to arp -a if arp-scan fails
        if scan_results is None:
            print("📋 Falling back to arp -a scanning")
            scan_results = self._scan_with_arp_table()

        try:
            # Process scan results
            for result in scan_results:
                ip = result.get("ip")
                mac = result.get("mac")

                # Skip if already seen or invalid
                if not ip or not mac:
                    continue
                if mac in seen_macs or mac == "00:00:00:00:00:00":
                    continue

                seen_macs.add(mac)
                current_macs.add(mac)

                # Get hostname from result or None
                hostname = result.get("hostname")

                # Get vendor - try arp-scan vendor first, then our database
                arp_scan_vendor = result.get("vendor")
                our_vendor_info = self.get_mac_vendor(mac)

                # Vendor fallback chain
                if arp_scan_vendor and arp_scan_vendor != "Unknown":
                    vendor_name = arp_scan_vendor
                    # Try to match type from our database
                    device_type = (
                        our_vendor_info.get("type", "default")
                        if our_vendor_info
                        else "default"
                    )
                elif our_vendor_info:
                    vendor_name = our_vendor_info.get("vendor")
                    device_type = our_vendor_info.get("type", "default")
                else:
                    vendor_name = None
                    device_type = "default"

                # Generate device name
                vendor_info_for_name = (
                    {"vendor": vendor_name, "type": device_type}
                    if vendor_name
                    else None
                )

                device_name = self.generate_device_name(
                    ip, mac, hostname, vendor_info_for_name
                )

                # Use arp-scan response time if available,
                # otherwise no ping needed
                latency = result.get("response_time")
                packet_loss = 0.0
                connection_quality = None

                if latency is not None:
                    # Response time from arp-scan (convert to ms if needed)
                    connection_quality = self.assess_connection_quality(
                        latency, packet_loss
                    )
                else:
                    # Fallback: ping only if arp-scan didn't provide time
                    if mac not in self.known_devices:
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

                    # Evaluate device for alerts
                    alerts = self.alert_manager.evaluate_device(device)
                    for alert in alerts:
                        # Add to activity log for visibility
                        self.activity_counter += 1
                        activity = NetworkActivity(
                            id=(
                                f"activity-{self.activity_counter}-"
                                f"{int(datetime.now().timestamp())}"
                            ),
                            device=device_name,
                            action=f"Alert: {alert.title}",
                            timestamp=datetime.now(),
                        )
                        self.activity_log.insert(0, activity)

                        # Broadcast alert via WebSocket for real-time updates
                        import asyncio

                        asyncio.create_task(
                            websocket_manager.broadcast_alert(
                                alert.model_dump(mode="json")
                            )
                        )

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
            "active_alerts": self.alert_manager.get_unacknowledged_count(),
        }

    def get_alerts(self):
        """Get all active alerts"""
        return self.alert_manager.get_active_alerts()

    def get_alert_history(self, limit: int = 50):
        """Get alert history"""
        return self.alert_manager.get_alert_history(limit)

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        return self.alert_manager.acknowledge_alert(alert_id)

    def get_alert_rules(self):
        """Get all alert rules"""
        return self.alert_manager.get_rules()

    def update_alert_rule(self, rule):
        """Update an alert rule"""
        self.alert_manager.update_rule(rule)
