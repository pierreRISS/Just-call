<script setup lang="ts">
import type { Metric } from '../types'

defineProps<{
  metric: Metric
}>()
</script>

<template>
  <article class="rounded-[1.6rem] border border-white/65 bg-white/38 p-5 shadow-[0_18px_60px_rgba(85,68,42,0.06)] backdrop-blur-2xl">
    <div class="flex items-start justify-between gap-4">
      <p class="text-sm font-medium text-stone-600">{{ metric.label }}</p>
      <span class="rounded-full bg-white/65 px-2.5 py-1 text-xs font-semibold text-emerald-700">{{ metric.delta }}</span>
    </div>
    <p class="mt-8 text-4xl font-semibold tracking-[-0.06em] text-stone-950">{{ metric.score }}</p>
    <div class="mt-4 h-1.5 overflow-hidden rounded-full bg-stone-200/70">
      <div class="h-full rounded-full bg-stone-950" :style="{ width: `${metric.score}%` }" />
    </div>
  </article>
</template>
