"""Alert management service for network monitoring."""

import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque

from app.models.network import (
    Alert,
    AlertRule,
    AlertType,
    AlertSeverity,
    NetworkDevice,
)


class AlertManager:
    """Manages network alerts, rules, and notifications."""

    def __init__(self, max_history: int = 100):
        """Initialize alert manager with storage."""
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=max_history)
        self.rules: Dict[str, AlertRule] = self._create_default_rules()
        self.device_states: Dict[str, dict] = {}

    def _create_default_rules(self) -> Dict[str, AlertRule]:
        """Create default alert rules."""
        return {
            "high_latency": AlertRule(
                id="high_latency",
                type=AlertType.HIGH_LATENCY,
                enabled=True,
                latency_threshold=200.0,
            ),
            "packet_loss": AlertRule(
                id="packet_loss",
                type=AlertType.PACKET_LOSS,
                enabled=True,
                packet_loss_threshold=10.0,
            ),
            "device_offline": AlertRule(
                id="device_offline",
                type=AlertType.DEVICE_OFFLINE,
                enabled=True,
                offline_threshold=300,
            ),
            "new_device": AlertRule(
                id="new_device",
                type=AlertType.NEW_DEVICE,
                enabled=True,
            ),
            "duplicate_ip": AlertRule(
                id="duplicate_ip",
                type=AlertType.DUPLICATE_IP,
                enabled=True,
            ),
        }

    def evaluate_device(self, device: NetworkDevice) -> List[Alert]:
        """Evaluate a device against alert rules."""
        alerts = []
        device_id = device.id

        # Track device state
        if device_id not in self.device_states:
            # New device detected
            if self.rules["new_device"].enabled:
                alert = self._create_alert(
                    alert_type=AlertType.NEW_DEVICE,
                    severity=AlertSeverity.INFO,
                    title="New Device Connected",
                    message=f"New device '{device.name}' "
                    f"({device.ip}) joined the network",
                    device_id=device_id,
                    device_name=device.name,
                )
                alerts.append(alert)

            self.device_states[device_id] = {
                "last_seen": time.time(),
                "status": device.status,
            }
        else:
            # Update last seen
            self.device_states[device_id]["last_seen"] = time.time()

            # Check status change
            prev_status = self.device_states[device_id]["status"]
            if prev_status != device.status and device.status == "offline":
                if self.rules["device_offline"].enabled:
                    alert = self._create_alert(
                        alert_type=AlertType.DEVICE_OFFLINE,
                        severity=AlertSeverity.WARNING,
                        title="Device Went Offline",
                        message=f"Device '{device.name}' "
                        f"({device.ip}) is no longer responding",
                        device_id=device_id,
                        device_name=device.name,
                    )
                    alerts.append(alert)

            self.device_states[device_id]["status"] = device.status

        # Check connection quality for online devices
        if device.status == "online":
            # High latency check
            if (
                device.latency
                and self.rules["high_latency"].enabled
                and device.latency > self.rules["high_latency"].latency_threshold
            ):
                alert_id = f"latency-{device_id}"
                if alert_id not in self.active_alerts:
                    alert = self._create_alert(
                        alert_type=AlertType.HIGH_LATENCY,
                        severity=AlertSeverity.WARNING,
                        title="High Latency Detected",
                        message=f"Device '{device.name}' has high latency "
                        f"({device.latency:.1f}ms)",
                        device_id=device_id,
                        device_name=device.name,
                        alert_id=alert_id,
                    )
                    alerts.append(alert)

            # Packet loss check
            if (
                device.packet_loss
                and self.rules["packet_loss"].enabled
                and device.packet_loss > self.rules["packet_loss"].packet_loss_threshold
            ):
                alert_id = f"packetloss-{device_id}"
                if alert_id not in self.active_alerts:
                    alert = self._create_alert(
                        alert_type=AlertType.PACKET_LOSS,
                        severity=AlertSeverity.ERROR,
                        title="Packet Loss Detected",
                        message=f"Device '{device.name}' experiencing "
                        f"packet loss ({device.packet_loss:.1f}%)",
                        device_id=device_id,
                        device_name=device.name,
                        alert_id=alert_id,
                    )
                    alerts.append(alert)

        return alerts

    def create_duplicate_ip_alert(self, ip: str, mac_addresses: List[str]) -> Alert:
        """Create alert for duplicate IP detection."""
        alert = self._create_alert(
            alert_type=AlertType.DUPLICATE_IP,
            severity=AlertSeverity.CRITICAL,
            title="Duplicate IP Detected",
            message=f"IP {ip} is being used by multiple devices: "
            f"{', '.join(mac_addresses)}",
            alert_id=f"dupip-{ip}",
        )
        self._add_alert(alert)
        return alert

    def _create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        alert_id: Optional[str] = None,
    ) -> Alert:
        """Create a new alert."""
        if alert_id is None:
            alert_id = f"alert-{int(time.time() * 1000)}"

        alert = Alert(
            id=alert_id,
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            device_id=device_id,
            device_name=device_name,
            timestamp=datetime.now(),
            acknowledged=False,
        )

        self._add_alert(alert)
        return alert

    def _add_alert(self, alert: Alert):
        """Add alert to active alerts and history."""
        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unacknowledged) alerts."""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: int = 50) -> List[Alert]:
        """Get recent alert history."""
        return list(self.alert_history)[-limit:]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now()
            del self.active_alerts[alert_id]
            return True
        return False

    def update_rule(self, rule: AlertRule):
        """Update an alert rule."""
        self.rules[rule.id] = rule

    def get_rules(self) -> List[AlertRule]:
        """Get all alert rules."""
        return list(self.rules.values())

    def get_unacknowledged_count(self) -> int:
        """Get count of unacknowledged alerts."""
        return len(self.active_alerts)
