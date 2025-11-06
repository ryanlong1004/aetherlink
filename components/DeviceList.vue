<template>
  <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 shadow-xl">
    <h3 class="text-xl font-semibold text-white mb-4">Connected Devices</h3>
    <div class="space-y-3 max-h-64 overflow-y-auto">
      <div
        v-for="device in devices"
        :key="device.id"
        class="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition"
      >
        <div class="flex items-center space-x-3">
          <span class="text-2xl">{{ getDeviceIcon(device.type) }}</span>
          <div>
            <p class="text-white font-medium">{{ device.name }}</p>
            <p class="text-gray-400 text-sm">{{ device.ip }}</p>
          </div>
        </div>
        <span
          :class="device.status === 'online' ? 'bg-green-500' : 'bg-gray-500'"
          class="px-3 py-1 rounded-full text-xs text-white font-medium"
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
