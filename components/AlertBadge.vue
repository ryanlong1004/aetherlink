<template>
  <button
    @click="$emit('toggle')"
    class="fixed top-4 right-32 z-50 glass-panel rounded-lg px-4 py-2 border-2 transition-all duration-300 hover:scale-105 cursor-pointer"
    :class="badgeClass"
  >
    <div class="flex items-center space-x-2">
      <!-- Alert icon -->
      <div class="relative">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-5 w-5" 
          :class="iconClass"
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" 
          />
        </svg>
        <!-- Pulse animation for active alerts -->
        <div 
          v-if="unacknowledgedCount > 0"
          class="absolute inset-0 animate-ping opacity-75"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            class="h-5 w-5" 
            :class="iconClass"
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" 
            />
          </svg>
        </div>
      </div>
      
      <!-- Badge count -->
      <span v-if="unacknowledgedCount > 0" class="text-sm font-bold">
        {{ unacknowledgedCount }}
      </span>
      <span v-else class="text-sm font-medium opacity-60">
        Alerts
      </span>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  unacknowledgedCount: number
  highestSeverity?: 'info' | 'warning' | 'error' | 'critical'
}

const props = withDefaults(defineProps<Props>(), {
  highestSeverity: 'info'
})

defineEmits(['toggle'])

const badgeClass = computed(() => {
  if (props.unacknowledgedCount === 0) {
    return 'border-gray-500/40'
  }
  
  switch (props.highestSeverity) {
    case 'critical':
      return 'border-red-500/60 bg-red-500/10'
    case 'error':
      return 'border-red-400/50 bg-red-400/5'
    case 'warning':
      return 'border-aether-bronze/50 bg-aether-bronze/5'
    case 'info':
      return 'border-aether-cyan/50 bg-aether-cyan/5'
    default:
      return 'border-gray-500/40'
  }
})

const iconClass = computed(() => {
  if (props.unacknowledgedCount === 0) {
    return 'text-gray-400'
  }
  
  switch (props.highestSeverity) {
    case 'critical':
      return 'text-red-500'
    case 'error':
      return 'text-red-400'
    case 'warning':
      return 'text-aether-bronze'
    case 'info':
      return 'text-aether-cyan'
    default:
      return 'text-gray-400'
  }
})
</script>
