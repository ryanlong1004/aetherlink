<template>
  <div class="glass-panel rounded-lg p-6 shadow-bronze-glow border-2 border-aether-bronze/20">
    <h3 class="text-xl font-semibold font-merriweather text-aether-bronze-light mb-4">
      Connected Devices
    </h3>
    <div class="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
      <div
        v-for="device in devices"
        :key="device.id"
        class="flex items-center justify-between p-3 glass-panel rounded-lg hover:border-aether-cyan/40 transition-all duration-300 border border-aether-cyan/10"
      >
        <div class="flex items-center space-x-3">
          <span class="text-2xl filter drop-shadow-lg">{{ getDeviceIcon(device.type) }}</span>
          <div>
            <p class="text-white font-medium font-orbitron">{{ device.name }}</p>
            <p class="text-gray-400 text-sm font-mono">{{ device.ip }}</p>
          </div>
        </div>
        <span
          :class="device.status === 'online' ? 'bg-aether-cyan/30 text-aether-cyan border-aether-cyan pulse-animation' : 'bg-gray-700/30 text-gray-400 border-gray-500'"
          class="px-3 py-1 rounded-full text-xs font-orbitron font-medium border"
        >
          {{ device.status }}
        </span>
      </div>
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
}

defineProps<{
  devices: Device[]
}>()

const getDeviceIcon = (type: string): string => {
  const icons: Record<string, string> = {
    mobile: '📱',
    laptop: '💻',
    tv: '📺',
    iot: '🔌',
    router: '📡',
    default: '🖥️'
  }
  return icons[type] || icons.default
}
</script>
