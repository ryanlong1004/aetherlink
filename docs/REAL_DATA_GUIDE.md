# Real Network Data Integration Guide

This guide explains how to populate AetherLink with real data from your home network.

## 📋 Table of Contents

1. [Quick Start - Local Network Scanning](#quick-start)
2. [Router-Specific Integration](#router-integration)
3. [Advanced Options](#advanced-options)
4. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start - Local Network Scanning

The simplest way to get real network data without router access.

### Step 1: Enable Real Data Mode

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
USE_REAL_NETWORK_DATA=true
NETWORK_PREFIX=192.168.1  # Adjust to your network
```

### Step 2: Grant Network Permissions

The app needs permission to scan your network. Depending on your OS:

**Linux:**

```bash
# Option 1: Run with sudo (development only)
sudo npm run dev

# Option 2: Grant node capabilities (recommended)
sudo setcap cap_net_raw+eip $(which node)
npm run dev
```

**macOS:**

```bash
# Run with sudo
sudo npm run dev
```

**Windows:**

```bash
# Run terminal as Administrator
npm run dev
```

### Step 3: Verify

Visit `http://localhost:3000` - you should see your actual network devices!

---

## 🏠 Router-Specific Integration

For more detailed data, integrate directly with your router's API.

### UniFi Controller

If you have a UniFi Dream Machine or Controller:

```bash
npm install node-unifi
```

Add to `.env`:

```env
UNIFI_CONTROLLER_URL=https://192.168.1.1:8443
UNIFI_USERNAME=admin
UNIFI_PASSWORD=your_password
UNIFI_SITE=default
```

### ASUS Routers

For ASUS routers with Asuswrt:

```bash
npm install asuswrt
```

Add to `.env`:

```env
ASUS_ROUTER_IP=192.168.1.1
ASUS_USERNAME=admin
ASUS_PASSWORD=your_password
```

### TP-Link Routers

For TP-Link routers:

```bash
npm install tp-link-cloud-api
```

### OpenWrt/DD-WRT

For custom firmware routers:

```bash
npm install ssh2
```

Configure SSH access to your router and query via command-line tools.

---

## 🔧 Advanced Options

### Option 1: SNMP Monitoring

For enterprise-grade routers with SNMP support:

```bash
npm install net-snmp
```

Create `server/utils/snmp-monitor.ts`:

```typescript
import snmp from "net-snmp";

export async function getSnmpData(host: string, community: string = "public") {
  const session = snmp.createSession(host, community);

  // OIDs for common network stats
  const oids = [
    "1.3.6.1.2.1.1.3.0", // System uptime
    "1.3.6.1.2.1.2.1.0", // Interface count
    "1.3.6.1.2.1.4.20.1.1", // IP addresses
  ];

  return new Promise((resolve, reject) => {
    session.get(oids, (error, varbinds) => {
      if (error) {
        reject(error);
      } else {
        resolve(varbinds);
      }
      session.close();
    });
  });
}
```

### Option 2: Router Admin Page Scraping

Last resort for routers without APIs:

```bash
npm install puppeteer cheerio
```

Create a scraper that logs into your router's web interface and parses the HTML.

### Option 3: Custom Device Database

Store device information for better naming:

```typescript
// server/data/known-devices.json
{
  "aa:bb:cc:dd:ee:01": {
    "name": "John's iPhone",
    "type": "mobile",
    "owner": "John"
  },
  "aa:bb:cc:dd:ee:02": {
    "name": "Living Room TV",
    "type": "tv",
    "location": "Living Room"
  }
}
```

---

## 🐛 Troubleshooting

### "Permission denied" errors

**Problem:** Can't access network interfaces

**Solution:**

```bash
# Linux - grant capabilities
sudo setcap cap_net_raw+eip $(which node)

# Or run with sudo (dev only)
sudo npm run dev
```

### No devices detected

**Problem:** ARP table is empty

**Solutions:**

1. Ping your network first: `ping 192.168.1.1`
2. Check your network prefix in `.env`
3. Ensure devices are actually connected
4. Try `arp -a` manually to verify ARP table

### Slow scanning

**Problem:** Network scan takes too long

**Solutions:**

1. Reduce scan range in `NETWORK_PREFIX`
2. Implement device caching
3. Use router API instead of network scanning

### TypeScript errors with node-arp

**Problem:** Type declaration errors

**Solution:**

```bash
# Create type declaration
echo 'declare module "node-arp";' > server/types/node-arp.d.ts
```

---

## 📊 What Data Can You Get?

### Network Scanning (Local)

✅ Connected devices (IP, MAC)
✅ Device count
✅ Network interface stats
✅ System uptime
❌ Individual device bandwidth
❌ Historical trends (requires storage)

### Router API Integration

✅ Everything from scanning, plus:
✅ Device hostnames
✅ Connection history
✅ Individual device bandwidth
✅ Signal strength (WiFi)
✅ Network topology
✅ Client association times

### SNMP Monitoring

✅ Everything from Router API, plus:
✅ Port statistics
✅ Interface errors
✅ QoS metrics
✅ VLAN information

---

## 🔐 Security Considerations

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use read-only accounts** - Don't use admin credentials if possible
3. **HTTPS only** - Enable SSL for router API connections
4. **Local network only** - Don't expose AetherLink to the internet without VPN
5. **Firewall rules** - Restrict access to trusted devices

---

## 📚 Additional Resources

- [systeminformation docs](https://systeminformation.io/)
- [node-arp GitHub](https://github.com/shopify/node-arp)
- [UniFi API Guide](https://ubntwiki.com/products/software/unifi-controller/api)
- [SNMP Tutorial](http://www.net-snmp.org/tutorial/)

---

## 🎯 Next Steps

1. **Start with mock data** - Get familiar with the dashboard
2. **Enable local scanning** - See your actual devices
3. **Add router integration** - Get detailed metrics
4. **Implement persistence** - Store historical data in database
5. **Add WebSockets** - Real-time updates without polling

Happy monitoring! 🌐
