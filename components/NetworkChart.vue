<template>
  <div class="glass-panel rounded-lg p-6 shadow-cyan-glow border-2 border-aether-cyan/20">
    <h3 class="text-xl font-semibold font-merriweather text-aether-cyan mb-4">
      Network Traffic
    </h3>
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
      borderColor: '#00e5ff',
      backgroundColor: 'rgba(0, 229, 255, 0.15)',
      fill: true,
      tension: 0.4,
      borderWidth: 2,
      pointBackgroundColor: '#00e5ff',
      pointBorderColor: '#00ffff',
      pointHoverRadius: 6,
      pointRadius: 3
    },
    {
      label: 'Upload (Mbps)',
      data: props.data.map(d => d.upload),
      borderColor: '#cd7f32',
      backgroundColor: 'rgba(205, 127, 50, 0.15)',
      fill: true,
      tension: 0.4,
      borderWidth: 2,
      pointBackgroundColor: '#cd7f32',
      pointBorderColor: '#d4a574',
      pointHoverRadius: 6,
      pointRadius: 3
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#e8e8f0',
        font: {
          family: 'Orbitron',
          size: 12
        },
        usePointStyle: true,
        padding: 15
      }
    },
    tooltip: {
      backgroundColor: 'rgba(26, 26, 62, 0.95)',
      titleColor: '#00e5ff',
      bodyColor: '#e8e8f0',
      borderColor: '#00e5ff',
      borderWidth: 1,
      padding: 12,
      displayColors: true,
      titleFont: {
        family: 'Orbitron',
        size: 13
      },
      bodyFont: {
        family: 'Orbitron',
        size: 12
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#9ca3af',
        font: {
          family: 'Orbitron',
          size: 10
        }
      },
      grid: {
        color: 'rgba(0, 229, 255, 0.1)'
      }
    },
    y: {
      ticks: {
        color: '#9ca3af',
        font: {
          family: 'Orbitron',
          size: 10
        }
      },
      grid: {
        color: 'rgba(0, 229, 255, 0.1)'
      }
    }
  }
}
</script>
