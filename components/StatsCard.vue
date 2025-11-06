<template>
  <div class="bg-white/10 backdrop-blur-lg rounded-lg p-6 shadow-xl">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
      <span class="text-2xl">{{ icon }}</span>
    </div>
    <p :class="valueClass" class="text-3xl font-bold">{{ value }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  value: string | number
  icon: string
  color: 'blue' | 'green' | 'purple' | 'orange'
}>()

const valueClass = computed(() => {
  const colors = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    purple: 'text-purple-400',
    orange: 'text-orange-400'
  }
  return colors[props.color]
})
</script>
