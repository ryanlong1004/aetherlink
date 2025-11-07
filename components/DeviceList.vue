<template>
  <div class="glass-panel rounded-lg p-6 shadow-bronze-glow border-2 border-aether-bronze/20">
    <h3 class="text-xl font-semibold font-merriweather text-aether-bronze-light mb-4">
      Connected Devices
    </h3>
    <div class="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
      <NuxtLink
        v-for="device in devices"
        :key="device.id"
        :to="`/devices/${device.id}`"
        class="block p-3 glass-panel rounded-lg hover:border-aether-cyan/40 transition-all duration-300 border border-aether-cyan/10 cursor-pointer hover:scale-[1.02]"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center space-x-3 flex-1">
            <span class="text-2xl filter drop-shadow-lg">{{ getDeviceIcon(device.type) }}</span>
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <p class="text-white font-medium font-orbitron">{{ device.name }}</p>
                <span
                  v-if="device.vendor"
                  class="text-xs text-aether-bronze-light font-mono"
                >
                  ({{ device.vendor }})
                </span>
              </div>
              <p class="text-gray-400 text-sm font-mono">{{ device.ip }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span
              v-if="device.connection_quality"
              :class="getQualityClass(device.connection_quality)"
              class="px-2 py-1 rounded text-xs font-orbitron font-medium border"
              :title="`Latency: ${device.latency?.toFixed(1)}ms, Loss: ${device.packet_loss?.toFixed(1)}%`"
            >
              {{ device.connection_quality }}
            </span>
            <span
              :class="device.status === 'online' ? 'bg-aether-cyan/30 text-aether-cyan border-aether-cyan pulse-animation' : 'bg-gray-700/30 text-gray-400 border-gray-500'"
              class="px-3 py-1 rounded-full text-xs font-orbitron font-medium border"
            >
              {{ device.status }}
            </span>
          </div>
        </div>
        <div v-if="device.latency !== null && device.latency !== undefined" class="flex items-center space-x-4 text-xs text-gray-400 mt-2 pl-11">
          <span class="flex items-center space-x-1">
            <span>⚡</span>
            <span>{{ device.latency.toFixed(1) }}ms</span>
          </span>
          <span v-if="device.packet_loss !== null && device.packet_loss !== undefined" class="flex items-center space-x-1">
            <span>📶</span>
            <span>{{ device.packet_loss.toFixed(1) }}% loss</span>
          </span>
          <span v-if="device.total_connections" class="flex items-center space-x-1">
            <span>🔄</span>
            <span>{{ device.total_connections }} connections</span>
          </span>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
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
  total_connections?: number
}

defineProps<{
  devices: Device[]
}>()

const getDeviceIcon = (type: string): string => {
  const icons: Record<string, string> = {
    phone: '📱',
    mobile: '📱',
    laptop: '💻',
    tv: '📺',
    speaker: '🔊',
    iot: '🔌',
    router: '📡',
    default: '🖥️'
  }
  return icons[type] || icons.default
}

const getQualityClass = (quality: string): string => {
  const classes: Record<string, string> = {
    excellent: 'bg-green-500/20 text-green-400 border-green-500',
    good: 'bg-blue-500/20 text-blue-400 border-blue-500',
    fair: 'bg-yellow-500/20 text-yellow-400 border-yellow-500',
    poor: 'bg-red-500/20 text-red-400 border-red-500'
  }
  return classes[quality] || classes.fair
}
</script>
