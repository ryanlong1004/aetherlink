<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Back button -->
        <NuxtLink to="/"
            class="inline-flex items-center space-x-2 text-aether-cyan hover:text-aether-cyan-light mb-6 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            <span class="font-orbitron">Back to Dashboard</span>
        </NuxtLink>

        <!-- Loading state -->
        <div v-if="loading" class="flex items-center justify-center py-20">
            <div class="text-aether-cyan text-xl font-orbitron">Loading device data...</div>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="glass-panel rounded-lg p-8 border-2 border-red-500/40 text-center">
            <h2 class="text-2xl font-bold text-red-500 mb-2">Error</h2>
            <p class="text-gray-300">{{ error }}</p>
        </div>

        <!-- Device details -->
        <div v-else-if="device">
            <!-- Device header -->
            <div class="glass-panel rounded-lg p-6 border-2 border-aether-cyan/40 mb-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <div class="text-5xl">
                            {{ getDeviceIcon(device.type) }}
                        </div>
                        <div>
                            <h1 class="text-3xl font-bold font-merriweather text-aether-cyan cyan-glow">
                                {{ device.name }}
                            </h1>
                            <p class="text-gray-400 font-mono text-sm mt-1">
                                {{ device.ip }} • {{ device.mac }}
                            </p>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                            :class="device.status === 'online' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'">
                            {{ device.status }}
                        </span>
                    </div>
                </div>

                <!-- Device metrics -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                    <div class="glass-panel rounded p-3 border border-aether-cyan/20">
                        <div class="text-gray-400 text-xs font-orbitron mb-1">Latency</div>
                        <div class="text-white text-lg font-bold">
                            {{ device.latency !== null ? `${device.latency.toFixed(1)} ms` : 'N/A' }}
                        </div>
                    </div>
                    <div class="glass-panel rounded p-3 border border-aether-cyan/20">
                        <div class="text-gray-400 text-xs font-orbitron mb-1">Packet Loss</div>
                        <div class="text-white text-lg font-bold">
                            {{ device.packet_loss !== null ? `${device.packet_loss.toFixed(1)}%` : 'N/A' }}
                        </div>
                    </div>
                    <div class="glass-panel rounded p-3 border border-aether-cyan/20">
                        <div class="text-gray-400 text-xs font-orbitron mb-1">Quality</div>
                        <div class="text-white text-lg font-bold capitalize">
                            {{ device.connection_quality || 'Unknown' }}
                        </div>
                    </div>
                    <div class="glass-panel rounded p-3 border border-aether-cyan/20">
                        <div class="text-gray-400 text-xs font-orbitron mb-1">Connections</div>
                        <div class="text-white text-lg font-bold">
                            {{ device.total_connections || 1 }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- History chart -->
            <div class="glass-panel rounded-lg p-6 border-2 border-aether-cyan/20 mb-6">
                <h2 class="text-2xl font-bold font-merriweather text-aether-cyan mb-4">
                    Connection History
                </h2>
                <DeviceHistoryChart v-if="history.length > 0" :history="history" />
                <div v-else class="text-center text-gray-400 py-8">
                    No historical data available yet
                </div>
            </div>

            <!-- Activity log -->
            <div class="glass-panel rounded-lg p-6 border-2 border-aether-cyan/20">
                <h2 class="text-2xl font-bold font-merriweather text-aether-cyan mb-4">
                    Recent Activity
                </h2>
                <div v-if="activities.length > 0" class="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
                    <div v-for="activity in activities" :key="activity.id"
                        class="flex items-start space-x-3 p-3 glass-panel rounded-lg border border-aether-cyan/10 hover:border-aether-cyan/30 transition-all">
                        <div class="flex-shrink-0 w-2 h-2 mt-2 bg-aether-cyan rounded-full pulse-animation"></div>
                        <div class="flex-1">
                            <p class="text-white font-orbitron">
                                {{ activity.action }}
                            </p>
                            <p class="text-gray-400 text-sm font-mono">{{ formatTime(activity.timestamp) }}</p>
                        </div>
                    </div>
                </div>
                <div v-else class="text-center text-gray-400 py-8">
                    No recent activity
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8001'

const deviceId = route.params.id as string

const device = ref<any>(null)
const history = ref<any[]>([])
const activities = ref<any[]>([])
const loading = ref(true)
const error = ref('')

const fetchDeviceData = async () => {
    try {
        loading.value = true
        error.value = ''

        // Fetch device details
        const deviceData = await $fetch(`${apiBase}/api/devices/${deviceId}`)
        device.value = deviceData

        // Fetch device history
        try {
            const historyData = await $fetch(`${apiBase}/api/devices/${deviceId}/history?limit=50`)
            history.value = historyData.history || []
        } catch (e) {
            console.warn('No history available for device')
            history.value = []
        }

        // Fetch device activities
        try {
            const activitiesData = await $fetch(`${apiBase}/api/devices/${deviceId}/activities?limit=20`)
            activities.value = activitiesData || []
        } catch (e) {
            console.warn('No activities available for device')
            activities.value = []
        }
    } catch (e: any) {
        error.value = e.message || 'Failed to load device data'
    } finally {
        loading.value = false
    }
}

const getDeviceIcon = (type: string): string => {
    const icons: Record<string, string> = {
        phone: '📱',
        mobile: '📱',
        laptop: '💻',
        computer: '🖥️',
        desktop: '🖥️',
        tablet: '📱',
        tv: '📺',
        speaker: '🔊',
        iot: '🌐',
        router: '📡',
        default: '📟'
    }
    return icons[type] || icons.default
}

const formatTime = (timestamp: Date | string): string => {
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

onMounted(() => {
    fetchDeviceData()
})
</script>
