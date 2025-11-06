<template>
  <div class="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
    <div
      v-for="activity in activities"
      :key="activity.id"
      class="flex items-start space-x-3 p-3 glass-panel rounded-lg border border-aether-cyan/10 hover:border-aether-cyan/30 transition-all"
    >
      <div class="flex-shrink-0 w-2 h-2 mt-2 bg-aether-cyan rounded-full pulse-animation"></div>
      <div class="flex-1">
        <p class="text-white font-orbitron">
          <span class="font-medium text-aether-cyan">{{ activity.device }}</span> - {{ activity.action }}
        </p>
        <p class="text-gray-400 text-sm font-mono">{{ formatTime(activity.timestamp) }}</p>
      </div>
    </div>
    <div v-if="activities.length === 0" class="text-center text-gray-400 py-8 font-orbitron">
      No recent activity
    </div>
  </div>
</template>

<script setup lang="ts">
interface Activity {
  id: string
  device: string
  action: string
  timestamp: Date
}

defineProps<{
  activities: Activity[]
}>()

const formatTime = (timestamp: Date): string => {
  const now = new Date()
  const diff = now.getTime() - new Date(timestamp).getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}
</script>
