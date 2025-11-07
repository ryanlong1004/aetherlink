<template>
  <div class="w-full h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface HistorySnapshot {
  timestamp: string
  latency: number | null
  packet_loss: number | null
  connection_quality: string | null
  status: string
}

interface Props {
  history: HistorySnapshot[]
}

const props = defineProps<Props>()

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const createChart = () => {
  if (!chartCanvas.value || !props.history.length) return

  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  // Prepare data
  const labels = props.history.map(h => {
    const date = new Date(h.timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  const latencyData = props.history.map(h => h.latency)
  const packetLossData = props.history.map(h => h.packet_loss)

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Latency (ms)',
          data: latencyData,
          borderColor: '#00e5ff',
          backgroundColor: 'rgba(0, 229, 255, 0.1)',
          borderWidth: 2,
          tension: 0.4,
          yAxisID: 'y',
          pointRadius: 3,
          pointHoverRadius: 5,
        },
        {
          label: 'Packet Loss (%)',
          data: packetLossData,
          borderColor: '#cd7f32',
          backgroundColor: 'rgba(205, 127, 50, 0.1)',
          borderWidth: 2,
          tension: 0.4,
          yAxisID: 'y1',
          pointRadius: 3,
          pointHoverRadius: 5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: '#e5e7eb',
            font: {
              family: 'Orbitron',
              size: 12,
            },
            usePointStyle: true,
            padding: 15,
          },
        },
        tooltip: {
          backgroundColor: 'rgba(17, 24, 39, 0.95)',
          titleColor: '#00e5ff',
          bodyColor: '#e5e7eb',
          borderColor: '#00e5ff',
          borderWidth: 1,
          padding: 12,
          titleFont: {
            family: 'Orbitron',
            size: 13,
          },
          bodyFont: {
            family: 'Monospace',
            size: 12,
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 229, 255, 0.1)',
            drawBorder: false,
          },
          ticks: {
            color: '#9ca3af',
            font: {
              family: 'Monospace',
              size: 10,
            },
            maxRotation: 45,
            minRotation: 0,
          },
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Latency (ms)',
            color: '#00e5ff',
            font: {
              family: 'Orbitron',
              size: 11,
            },
          },
          grid: {
            color: 'rgba(0, 229, 255, 0.1)',
            drawBorder: false,
          },
          ticks: {
            color: '#00e5ff',
            font: {
              family: 'Monospace',
              size: 10,
            },
          },
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Packet Loss (%)',
            color: '#cd7f32',
            font: {
              family: 'Orbitron',
              size: 11,
            },
          },
          grid: {
            drawOnChartArea: false,
          },
          ticks: {
            color: '#cd7f32',
            font: {
              family: 'Monospace',
              size: 10,
            },
          },
        },
      },
    },
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.history, () => {
  createChart()
}, { deep: true })
</script>
