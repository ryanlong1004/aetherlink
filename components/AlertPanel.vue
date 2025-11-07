<template>
  <div
    v-if="isOpen"
    class="fixed top-20 right-4 z-40 w-96 glass-panel rounded-lg border-2 border-aether-cyan/40 overflow-hidden shadow-2xl"
  >
    <!-- Header -->
    <div class="p-4 border-b border-aether-cyan/20 flex justify-between items-center">
      <h3 class="text-lg font-orbitron font-bold text-white flex items-center space-x-2">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-5 w-5 text-aether-cyan" 
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
        <span>Network Alerts</span>
      </h3>
      <button
        @click="$emit('close')"
        class="text-gray-400 hover:text-white transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-aether-cyan/20">
      <button
        @click="activeTab = 'active'"
        class="flex-1 px-4 py-2 font-orbitron text-sm transition-all"
        :class="activeTab === 'active' 
          ? 'text-aether-cyan border-b-2 border-aether-cyan bg-aether-cyan/5' 
          : 'text-gray-400 hover:text-white'"
      >
        Active ({{ alerts.length }})
      </button>
      <button
        @click="activeTab = 'history'"
        class="flex-1 px-4 py-2 font-orbitron text-sm transition-all"
        :class="activeTab === 'history' 
          ? 'text-aether-cyan border-b-2 border-aether-cyan bg-aether-cyan/5' 
          : 'text-gray-400 hover:text-white'"
      >
        History
      </button>
    </div>

    <!-- Alert List -->
    <div class="max-h-96 overflow-y-auto custom-scrollbar">
      <!-- Active Alerts -->
      <div v-if="activeTab === 'active'" class="p-4 space-y-3">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          class="p-3 rounded-lg border transition-all hover:scale-[1.02]"
          :class="alertClass(alert.severity)"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-2 flex-1">
              <!-- Severity icon -->
              <div class="flex-shrink-0 mt-1">
                <component :is="severityIcon(alert.severity)" class="w-5 h-5" :class="severityColor(alert.severity)" />
              </div>
              
              <!-- Alert content -->
              <div class="flex-1 min-w-0">
                <h4 class="font-orbitron font-medium text-white text-sm">
                  {{ alert.title }}
                </h4>
                <p class="text-gray-300 text-xs mt-1">
                  {{ alert.message }}
                </p>
                <div class="flex items-center space-x-3 mt-2 text-xs text-gray-400 font-mono">
                  <span v-if="alert.device_name">{{ alert.device_name }}</span>
                  <span>{{ formatTime(alert.timestamp) }}</span>
                </div>
              </div>
            </div>

            <!-- Acknowledge button -->
            <button
              v-if="!alert.acknowledged_at"
              @click="acknowledgeAlert(alert.id)"
              class="ml-2 px-2 py-1 text-xs font-orbitron rounded border border-aether-cyan/30 text-aether-cyan hover:bg-aether-cyan/10 transition-all"
              title="Acknowledge"
            >
              ✓
            </button>
          </div>
        </div>

        <div v-if="alerts.length === 0" class="text-center text-gray-400 py-8 font-orbitron">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          No active alerts
        </div>
      </div>

      <!-- Alert History -->
      <div v-else class="p-4 space-y-3">
        <div
          v-for="alert in alertHistory"
          :key="alert.id"
          class="p-3 rounded-lg border border-gray-700/50 bg-gray-800/30 opacity-70"
        >
          <div class="flex items-start space-x-2">
            <component :is="severityIcon(alert.severity)" class="w-4 h-4 mt-1 text-gray-500" />
            <div class="flex-1 min-w-0">
              <h4 class="font-orbitron font-medium text-gray-300 text-sm">
                {{ alert.title }}
              </h4>
              <p class="text-gray-400 text-xs mt-1">
                {{ alert.message }}
              </p>
              <div class="flex items-center space-x-3 mt-2 text-xs text-gray-500 font-mono">
                <span v-if="alert.device_name">{{ alert.device_name }}</span>
                <span>{{ formatTime(alert.timestamp) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="alertHistory.length === 0" class="text-center text-gray-400 py-8 font-orbitron">
          No alert history
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, h } from 'vue'

interface Alert {
  id: string
  type: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  title: string
  message: string
  device_name?: string
  device_mac?: string
  timestamp: Date
  acknowledged_at?: Date
}

interface Props {
  isOpen: boolean
  alerts: Alert[]
  alertHistory: Alert[]
}

defineProps<Props>()

const emit = defineEmits(['close', 'acknowledge'])

const activeTab = ref<'active' | 'history'>('active')

const acknowledgeAlert = (alertId: string) => {
  emit('acknowledge', alertId)
}

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

const alertClass = (severity: string) => {
  switch (severity) {
    case 'critical':
      return 'border-red-500/60 bg-red-500/10'
    case 'error':
      return 'border-red-400/50 bg-red-400/5'
    case 'warning':
      return 'border-aether-bronze/50 bg-aether-bronze/5'
    case 'info':
      return 'border-aether-cyan/50 bg-aether-cyan/5'
    default:
      return 'border-gray-500/40 bg-gray-500/5'
  }
}

const severityColor = (severity: string) => {
  switch (severity) {
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
}

const severityIcon = (severity: string) => {
  const iconProps = {
    xmlns: 'http://www.w3.org/2000/svg',
    fill: 'none',
    viewBox: '0 0 24 24',
    stroke: 'currentColor',
    'stroke-width': '2'
  }

  switch (severity) {
    case 'critical':
    case 'error':
      return h('svg', iconProps, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
        })
      ])
    case 'warning':
      return h('svg', iconProps, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          d: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
        })
      ])
    case 'info':
    default:
      return h('svg', iconProps, [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          d: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
        })
      ])
  }
}
</script>
