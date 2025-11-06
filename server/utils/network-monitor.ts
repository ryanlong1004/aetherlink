/**
 * Network monitoring utilities for AetherLink
 * Provides real network data collection from local network
 */

import arp from "node-arp";
import si from "systeminformation";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export interface NetworkDevice {
  id: string;
  name: string;
  ip: string;
  mac: string;
  status: "online" | "offline";
  type: string;
  vendor?: string;
  lastSeen?: Date;
}

export interface NetworkStats {
  connectedDevices: number;
  networkSpeed: number;
  dataUsage: number;
  uptime: string;
}

export interface NetworkActivity {
  id: string;
  device: string;
  action: string;
  timestamp: Date;
}

/**
 * Get network interface statistics
 */
export async function getNetworkStats(): Promise<
  si.Systeminformation.NetworkStatsData[]
> {
  return await si.networkStats();
}

/**
 * Get network interface information
 */
export async function getNetworkInterfaces(): Promise<
  si.Systeminformation.NetworkInterfacesData[]
> {
  return await si.networkInterfaces();
}

/**
 * Get system uptime
 */
export async function getSystemUptime(): Promise<number> {
  const time = await si.time();
  return time.uptime;
}

/**
 * Format uptime in days, hours, minutes
 */
export function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) {
    return `${days}d ${hours}h`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
}

/**
 * Scan local network for devices using ARP
 */
export async function scanNetwork(
  networkPrefix: string = "192.168.1"
): Promise<NetworkDevice[]> {
  const devices: NetworkDevice[] = [];

  try {
    // Get ARP table
    const arpTable = await getArpTable();

    for (const entry of arpTable) {
      if (entry.ip && entry.mac) {
        devices.push({
          id: entry.mac.replace(/:/g, ""),
          name:
            (await getDeviceHostname(entry.ip)) ||
            `Device-${entry.ip.split(".").pop()}`,
          ip: entry.ip,
          mac: entry.mac,
          status: "online",
          type: guessDeviceType(entry.mac),
          vendor: await getMacVendor(entry.mac),
          lastSeen: new Date(),
        });
      }
    }
  } catch (error) {
    console.error("Network scan error:", error);
  }

  return devices;
}

/**
 * Get ARP table from system
 */
async function getArpTable(): Promise<Array<{ ip: string; mac: string }>> {
  try {
    const { stdout } = await execAsync("arp -a");
    const entries: Array<{ ip: string; mac: string }> = [];

    // Parse ARP output
    const lines = stdout.split("\n");
    for (const line of lines) {
      // Match IP and MAC address patterns
      const ipMatch = line.match(/\((\d+\.\d+\.\d+\.\d+)\)/);
      const macMatch = line.match(
        /([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})/
      );

      if (ipMatch && macMatch) {
        entries.push({
          ip: ipMatch[1],
          mac: macMatch[1].toLowerCase(),
        });
      }
    }

    return entries;
  } catch (error) {
    console.error("Failed to get ARP table:", error);
    return [];
  }
}

/**
 * Attempt to get hostname for IP address
 */
async function getDeviceHostname(ip: string): Promise<string | null> {
  return new Promise((resolve) => {
    arp.getMAC(ip, (err, mac) => {
      if (err) {
        resolve(null);
      } else {
        // Try reverse DNS lookup
        exec(`nslookup ${ip}`, (error, stdout) => {
          if (error) {
            resolve(null);
          } else {
            const nameMatch = stdout.match(/name = (.+)/);
            resolve(nameMatch ? nameMatch[1].trim() : null);
          }
        });
      }
    });
  });
}

/**
 * Guess device type based on MAC address OUI
 */
function guessDeviceType(mac: string): string {
  const oui = mac.substring(0, 8).toLowerCase();

  // Common device type patterns (partial list)
  const patterns: Record<string, string> = {
    // Apple devices
    "00:03:93": "mobile",
    "00:0a:95": "mobile",
    "00:1b:63": "mobile",
    "ac:de:48": "mobile",
    "f0:18:98": "laptop",

    // Samsung
    "00:12:fb": "mobile",
    "00:1d:25": "tv",

    // Google/Nest
    "54:60:09": "iot",
    "6c:ad:f8": "iot",

    // Raspberry Pi
    "b8:27:eb": "iot",
    "dc:a6:32": "iot",
  };

  return patterns[oui] || "default";
}

/**
 * Get MAC vendor from OUI (simplified - in production use an API)
 */
async function getMacVendor(mac: string): Promise<string | undefined> {
  const oui = mac.substring(0, 8).toLowerCase();

  // Common vendors (partial list - in production, use IEEE OUI database or API)
  const vendors: Record<string, string> = {
    "00:03:93": "Apple",
    "00:0a:95": "Apple",
    "00:1b:63": "Apple",
    "ac:de:48": "Apple",
    "f0:18:98": "Apple",
    "00:12:fb": "Samsung",
    "00:1d:25": "Samsung",
    "54:60:09": "Google",
    "6c:ad:f8": "Google",
    "b8:27:eb": "Raspberry Pi Foundation",
    "dc:a6:32": "Raspberry Pi Trading",
  };

  return vendors[oui];
}

/**
 * Calculate network speed based on interface stats
 */
export async function calculateNetworkSpeed(): Promise<number> {
  const stats = await getNetworkStats();

  // Get primary interface (usually the one with most traffic)
  const primaryInterface = stats.reduce((prev, current) =>
    prev.rx_bytes + prev.tx_bytes > current.rx_bytes + current.tx_bytes
      ? prev
      : current
  );

  // Convert bytes/sec to Mbps
  const speedMbps =
    ((primaryInterface.rx_sec + primaryInterface.tx_sec) * 8) / 1000000;

  return Math.round(speedMbps);
}

/**
 * Calculate total data usage
 */
export async function calculateDataUsage(): Promise<number> {
  const stats = await getNetworkStats();

  const totalBytes = stats.reduce(
    (sum, iface) => sum + iface.rx_bytes + iface.tx_bytes,
    0
  );

  // Convert to GB
  return Math.round((totalBytes / 1073741824) * 10) / 10;
}
