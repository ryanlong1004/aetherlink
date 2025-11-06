<template>
  <div class="glass-panel rounded-lg p-6 shadow-cyan-glow transition-all duration-300 hover:scale-105 border-2" :class="borderClass">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-gray-300 uppercase tracking-wider font-orbitron">{{ title }}</h3>
      <span class="text-3xl filter drop-shadow-lg">{{ icon }}</span>
    </div>
    <p :class="valueClass" class="text-4xl font-bold font-orbitron tracking-tight">{{ value }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  value: string | number
  icon: string
  color: 'cyan' | 'bronze'
}>()

const valueClass = computed(() => {
  const colors = {
    cyan: 'text-aether-cyan cyan-glow',
    bronze: 'text-aether-bronze-light bronze-glow'
  }
  return colors[props.color]
})

const borderClass = computed(() => {
  const borders = {
    cyan: 'border-aether-cyan/30 hover:border-aether-cyan/60',
    bronze: 'border-aether-bronze/30 hover:border-aether-bronze/60'
  }
  return borders[props.color]
})
</script>
