<template>
  <div class="container mx-auto px-4 py-8">
    <header class="mb-8">
      <h1 class="text-4xl font-bold text-white mb-2">Aetherlink</h1>
      <p class="text-gray-300">Home Network Monitor</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatsCard
        title="Connected Devices"
        :value="stats.connectedDevices"
        icon="🔗"
        color="blue"
      />
      <StatsCard
        title="Network Speed"
        :value="`${stats.networkSpeed} Mbps`"
        icon="⚡"
        color="green"
      />
      <StatsCard
        title="Data Usage"
        :value="`${stats.dataUsage} GB`"
        icon="📊"
        color="purple"
      />
      <StatsCard
        title="Uptime"
        :value="stats.uptime"
        icon="⏱️"
        color="orange"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <NetworkChart :data="networkData" />
      <DeviceList :devices="devices" />
    </div>

    <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6">
      <h2 class="text-2xl font-bold text-white mb-4">Network Activity</h2>
      <ActivityLog :activities="activities" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Stats {
  connectedDevices: number
  networkSpeed: number
  dataUsage: number
  uptime: string
}

interface Device {
  id: string
  name: string
  ip: string
  mac: string
  status: 'online' | 'offline'
  type: string
}

interface Activity {
  id: string
  device: string
  action: string
  timestamp: Date
}

const stats = ref<Stats>({
  connectedDevices: 0,
  networkSpeed: 0,
  dataUsage: 0,
  uptime: '0h 0m'
})

const devices = ref<Device[]>([])
const activities = ref<Activity[]>([])
const networkData = ref<any[]>([])

const fetchNetworkData = async () => {
  try {
    const response = await $fetch('/api/network/status')
    stats.value = response.stats
    devices.value = response.devices
    activities.value = response.activities
    networkData.value = response.chartData
  } catch (error) {
    console.error('Failed to fetch network data:', error)
    // Use mock data for development
    loadMockData()
  }
}

const loadMockData = () => {
  stats.value = {
    connectedDevices: 8,
    networkSpeed: 450,
    dataUsage: 127.5,
    uptime: '5d 12h'
  }

  devices.value = [
    { id: '1', name: 'iPhone 13', ip: '192.168.1.10', mac: 'AA:BB:CC:DD:EE:01', status: 'online', type: 'mobile' },
    { id: '2', name: 'MacBook Pro', ip: '192.168.1.11', mac: 'AA:BB:CC:DD:EE:02', status: 'online', type: 'laptop' },
    { id: '3', name: 'Smart TV', ip: '192.168.1.15', mac: 'AA:BB:CC:DD:EE:03', status: 'online', type: 'tv' },
    { id: '4', name: 'Raspberry Pi', ip: '192.168.1.20', mac: 'AA:BB:CC:DD:EE:04', status: 'online', type: 'iot' },
    { id: '5', name: 'Google Home', ip: '192.168.1.25', mac: 'AA:BB:CC:DD:EE:05', status: 'offline', type: 'iot' },
  ]

  activities.value = [
    { id: '1', device: 'iPhone 13', action: 'Connected to network', timestamp: new Date(Date.now() - 300000) },
    { id: '2', device: 'MacBook Pro', action: 'High bandwidth usage detected', timestamp: new Date(Date.now() - 600000) },
    { id: '3', device: 'Smart TV', action: 'Streaming detected', timestamp: new Date(Date.now() - 900000) },
  ]

  networkData.value = generateMockChartData()
}

const generateMockChartData = () => {
  const data = []
  for (let i = 23; i >= 0; i--) {
    data.push({
      time: `${i}h ago`,
      download: Math.floor(Math.random() * 100) + 50,
      upload: Math.floor(Math.random() * 50) + 10
    })
  }
  return data.reverse()
}

onMounted(() => {
  fetchNetworkData()
  // Refresh data every 30 seconds
  setInterval(fetchNetworkData, 30000)
})
</script>
