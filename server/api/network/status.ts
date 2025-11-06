import {
  scanNetwork,
  getSystemUptime,
  formatUptime,
  calculateNetworkSpeed,
  calculateDataUsage,
  getNetworkStats,
  type NetworkDevice,
} from "~/server/utils/network-monitor";

// Store for tracking network history and activities
const networkHistory: Array<{
  timestamp: Date;
  download: number;
  upload: number;
}> = [];
const activityLog: Array<{
  id: string;
  device: string;
  action: string;
  timestamp: Date;
}> = [];
let knownDevices = new Set<string>();

// Configuration
const USE_REAL_DATA = process.env.USE_REAL_NETWORK_DATA === "true";
const NETWORK_PREFIX = process.env.NETWORK_PREFIX || "192.168.1";

export default defineEventHandler(async () => {
  if (USE_REAL_DATA) {
    return await getRealNetworkData();
  } else {
    return getMockNetworkData();
  }
});

async function getRealNetworkData() {
  try {
    // Scan network for devices
    const devices = await scanNetwork(NETWORK_PREFIX);

    // Track new devices
    for (const device of devices) {
      if (!knownDevices.has(device.mac)) {
        knownDevices.add(device.mac);
        activityLog.unshift({
          id: Date.now().toString(),
          device: device.name,
          action: "Connected to network",
          timestamp: new Date(),
        });
      }
    }

    // Get system statistics
    const uptime = await getSystemUptime();
    const speed = await calculateNetworkSpeed();
    const dataUsage = await calculateDataUsage();

    // Get current network stats for chart
    const stats = await getNetworkStats();
    const primaryInterface = stats[0]; // Use first interface

    // Add to history
    networkHistory.push({
      timestamp: new Date(),
      download: Math.round((primaryInterface.rx_sec * 8) / 1000000), // Convert to Mbps
      upload: Math.round((primaryInterface.tx_sec * 8) / 1000000),
    });

    // Keep only last 24 hours of data
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    while (
      networkHistory.length > 0 &&
      networkHistory[0].timestamp.getTime() < oneDayAgo
    ) {
      networkHistory.shift();
    }

    // Keep only last 50 activities
    if (activityLog.length > 50) {
      activityLog.length = 50;
    }

    return {
      stats: {
        connectedDevices: devices.length,
        networkSpeed: speed,
        dataUsage: dataUsage,
        uptime: formatUptime(uptime),
      },
      devices: devices,
      activities: activityLog.slice(0, 10), // Return last 10 activities
      chartData: generateChartDataFromHistory(),
    };
  } catch (error) {
    console.error("Error fetching real network data:", error);
    // Fallback to mock data on error
    return getMockNetworkData();
  }
}

function generateChartDataFromHistory() {
  if (networkHistory.length === 0) {
    return generateMockChartData();
  }

  const data = networkHistory.map((entry, index) => {
    const hoursAgo = Math.floor(
      (Date.now() - entry.timestamp.getTime()) / 3600000
    );
    return {
      time: hoursAgo === 0 ? "Now" : `${hoursAgo}h`,
      download: entry.download,
      upload: entry.upload,
    };
  });

  return data.length > 0 ? data : generateMockChartData();
}

function getMockNetworkData() {
  return {
    stats: {
      connectedDevices: Math.floor(Math.random() * 5) + 5,
      networkSpeed: Math.floor(Math.random() * 100) + 400,
      dataUsage: Math.floor(Math.random() * 50) + 100,
      uptime: `${Math.floor(Math.random() * 10)}d ${Math.floor(
        Math.random() * 24
      )}h`,
    },
    devices: [
      {
        id: "1",
        name: "iPhone 13",
        ip: "192.168.1.10",
        mac: "AA:BB:CC:DD:EE:01",
        status: "online",
        type: "mobile",
      },
      {
        id: "2",
        name: "MacBook Pro",
        ip: "192.168.1.11",
        mac: "AA:BB:CC:DD:EE:02",
        status: "online",
        type: "laptop",
      },
      {
        id: "3",
        name: "Smart TV",
        ip: "192.168.1.15",
        mac: "AA:BB:CC:DD:EE:03",
        status: "online",
        type: "tv",
      },
      {
        id: "4",
        name: "Raspberry Pi",
        ip: "192.168.1.20",
        mac: "AA:BB:CC:DD:EE:04",
        status: "online",
        type: "iot",
      },
      {
        id: "5",
        name: "Google Home",
        ip: "192.168.1.25",
        mac: "AA:BB:CC:DD:EE:05",
        status: Math.random() > 0.5 ? "online" : "offline",
        type: "iot",
      },
    ],
    activities: [
      {
        id: "1",
        device: "iPhone 13",
        action: "Connected to network",
        timestamp: new Date(Date.now() - 300000),
      },
      {
        id: "2",
        device: "MacBook Pro",
        action: "High bandwidth usage detected",
        timestamp: new Date(Date.now() - 600000),
      },
      {
        id: "3",
        device: "Smart TV",
        action: "Streaming detected",
        timestamp: new Date(Date.now() - 900000),
      },
    ],
    chartData: generateMockChartData(),
  };
}

function generateMockChartData() {
  const data = [];
  for (let i = 23; i >= 0; i--) {
    data.push({
      time: i === 0 ? "Now" : `${i}h`,
      download: Math.floor(Math.random() * 100) + 50,
      upload: Math.floor(Math.random() * 50) + 10,
    });
  }
  return data.reverse();
}
