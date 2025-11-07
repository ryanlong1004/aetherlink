<template>
  <div class="fixed top-4 right-4 z-50">
    <div
      class="glass-panel rounded-lg px-4 py-2 border-2 flex items-center space-x-2 transition-all duration-300"
      :class="statusClass"
    >
      <div class="relative">
        <div 
          class="w-3 h-3 rounded-full"
          :class="dotClass"
        ></div>
        <div 
          v-if="status === 'connected'"
          class="absolute inset-0 w-3 h-3 rounded-full animate-ping opacity-75"
          :class="dotClass"
        ></div>
      </div>
      <span class="text-sm font-medium">
        {{ statusText }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'connected' | 'disconnected' | 'connecting' | 'reconnecting'
}

const props = defineProps<Props>()

const statusText = computed(() => {
  switch (props.status) {
    case 'connected':
      return 'Live'
    case 'connecting':
      return 'Connecting...'
    case 'reconnecting':
      return 'Reconnecting...'
    case 'disconnected':
      return 'Disconnected'
    default:
      return 'Unknown'
  }
})

const statusClass = computed(() => {
  switch (props.status) {
    case 'connected':
      return 'border-aether-cyan/40'
    case 'connecting':
    case 'reconnecting':
      return 'border-aether-bronze/40'
    case 'disconnected':
      return 'border-red-500/40'
    default:
      return 'border-gray-500/40'
  }
})

const dotClass = computed(() => {
  switch (props.status) {
    case 'connected':
      return 'bg-aether-cyan'
    case 'connecting':
    case 'reconnecting':
      return 'bg-aether-bronze'
    case 'disconnected':
      return 'bg-red-500'
    default:
      return 'bg-gray-500'
  }
})
</script>
