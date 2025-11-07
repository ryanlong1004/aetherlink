<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Connection Status Indicator -->
    <ConnectionStatus :status="connectionStatus" />
    
    <!-- Hero Header with Logo -->
    <header class="mb-12 text-center">
      <div class="flex items-center justify-center mb-4">
        <img src="/logo.png" alt="AetherLink Logo" class="h-24 w-24 object-contain node-pulse" />
      </div>
      <h1 class="text-6xl font-bold font-merriweather text-aether-cyan cyan-glow mb-3">
        AetherLink
      </h1>
      <p class="text-xl text-aether-bronze-light bronze-glow font-orbitron tracking-wider">
        See the unseen. Control the connected.
      </p>
      <p class="text-sm text-gray-400 mt-2 font-light">
        Your home network, visualized
      </p>
    </header>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatsCard
        title="Connected Devices"
        :value="stats.connectedDevices"
        icon="🔗"
        color="cyan"
      />
      <StatsCard
        title="Network Speed"
        :value="`${stats.networkSpeed} Mbps`"
        icon="⚡"
        color="cyan"
      />
      <StatsCard
        title="Data Usage"
        :value="`${stats.dataUsage} GB`"
        icon="📊"
        color="bronze"
      />
      <StatsCard
        title="Uptime"
        :value="stats.uptime"
        icon="⏱️"
        color="bronze"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <NetworkChart :data="networkData" />
      <DeviceList :devices="devices" />
    </div>

    <!-- Activity Log -->
    <div class="glass-panel rounded-lg p-6 border-2 border-aether-cyan/20">
      <h2 class="text-2xl font-bold font-merriweather text-aether-cyan mb-4">
        Network Activity
      </h2>
      <ActivityLog :activities="activities" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Stats {
  connected_devices: number
  network_speed: number
  data_usage: number
  uptime: string
}

interface Device {
  id: string
  name: string
  ip: string
  mac: string
  status: 'online' | 'offline'
  type: string
  vendor?: string
  latency?: number
  packet_loss?: number
  connection_quality?: 'excellent' | 'good' | 'fair' | 'poor'
  first_seen?: string
  last_seen?: string
  total_connections?: number
}

interface Activity {
  id: string
  device: string
  action: string
  timestamp: string
}

const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'
const wsBase = apiBase.replace('http://', 'ws://').replace('https://', 'wss://')

const stats = ref({
  connectedDevices: 0,
  networkSpeed: 0,
  dataUsage: 0,
  uptime: '0h 0m'
})

const devices = ref<Device[]>([])
const activities = ref<Activity[]>([])
const networkData = ref<any[]>([])
const connectionStatus = ref<'connected' | 'disconnected' | 'connecting' | 'reconnecting'>('connecting')

let ws: WebSocket | null = null
let reconnectAttempts = 0
let reconnectTimeout: ReturnType<typeof setTimeout> | null = null
const maxReconnectDelay = 30000 // 30 seconds max
const baseReconnectDelay = 1000 // 1 second base

const updateNetworkData = (data: any) => {
  stats.value = {
    connectedDevices: data.stats.connected_devices,
    networkSpeed: data.stats.network_speed,
    dataUsage: data.stats.data_usage,
    uptime: data.stats.uptime
  }
  
  devices.value = data.devices
  activities.value = data.activities
  networkData.value = data.chart_data
}

const connectWebSocket = () => {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return
  }

  connectionStatus.value = reconnectAttempts > 0 ? 'reconnecting' : 'connecting'
  
  try {
    ws = new WebSocket(`${wsBase}/api/ws/network`)

    ws.onopen = () => {
      console.log('✓ WebSocket connected')
      connectionStatus.value = 'connected'
      reconnectAttempts = 0
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        
        if (message.type === 'network_update') {
          updateNetworkData(message.data)
        } else if (message.type === 'device_event') {
          console.log(`Device event: ${message.event}`, message.device)
          // Could trigger notifications here
        } else if (message.type === 'ping') {
          // Heartbeat received
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      connectionStatus.value = 'disconnected'
    }

    ws.onclose = () => {
      console.log('✗ WebSocket disconnected')
      connectionStatus.value = 'disconnected'
      ws = null
      
      // Attempt to reconnect with exponential backoff
      const delay = Math.min(baseReconnectDelay * Math.pow(2, reconnectAttempts), maxReconnectDelay)
      console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1})`)
      
      reconnectTimeout = setTimeout(() => {
        reconnectAttempts++
        connectWebSocket()
      }, delay)
    }
  } catch (error) {
    console.error('Failed to create WebSocket:', error)
    connectionStatus.value = 'disconnected'
    fallbackToPolling()
  }
}

const disconnectWebSocket = () => {
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout)
    reconnectTimeout = null
  }
  
  if (ws) {
    ws.close()
    ws = null
  }
}

const fetchNetworkData = async () => {
  try {
    const response = await $fetch(`${apiBase}/api/network/status`)
    updateNetworkData(response)
  } catch (error) {
    console.error('Failed to fetch network data from API:', error)
    console.log('Falling back to mock data for development')
    loadMockData()
  }
}

const fallbackToPolling = () => {
  console.log('Falling back to HTTP polling')
  fetchNetworkData()
  setInterval(fetchNetworkData, 30000)
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
    { id: '1', device: 'iPhone 13', action: 'Connected to network', timestamp: new Date(Date.now() - 300000).toISOString() },
    { id: '2', device: 'MacBook Pro', action: 'High bandwidth usage detected', timestamp: new Date(Date.now() - 600000).toISOString() },
    { id: '3', device: 'Smart TV', action: 'Streaming detected', timestamp: new Date(Date.now() - 900000).toISOString() },
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
  // Try WebSocket first, fall back to polling if it fails
  connectWebSocket()
})

onUnmounted(() => {
  disconnectWebSocket()
})
</script>
