export default defineEventHandler(() => {
  // This is a mock API endpoint. In production, this would connect to actual network monitoring tools
  // like router APIs, SNMP, or system network interfaces

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
    chartData: generateChartData(),
  };
});

function generateChartData() {
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
