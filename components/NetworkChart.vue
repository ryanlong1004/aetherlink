<template>
  <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 shadow-xl">
    <h3 class="text-xl font-semibold text-white mb-4">Network Traffic</h3>
    <div class="h-64">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps<{
  data: Array<{ time: string; download: number; upload: number }>
}>()

const chartData = computed(() => ({
  labels: props.data.map(d => d.time),
  datasets: [
    {
      label: 'Download (Mbps)',
      data: props.data.map(d => d.download),
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.4
    },
    {
      label: 'Upload (Mbps)',
      data: props.data.map(d => d.upload),
      borderColor: 'rgb(34, 197, 94)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      fill: true,
      tension: 0.4
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#ffffff'
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#9ca3af'
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    y: {
      ticks: {
        color: '#9ca3af'
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  }
}
</script>
