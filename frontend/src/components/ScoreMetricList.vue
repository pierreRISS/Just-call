<script setup lang="ts">
import type { Metric } from '../types'

withDefaults(
  defineProps<{
    metrics: Metric[]
    compact?: boolean
  }>(),
  {
    compact: false,
  },
)
</script>

<template>
  <div v-if="compact" class="overflow-hidden rounded-2xl border border-white/70 bg-white/50 shadow-[0_18px_54px_rgba(85,68,42,0.06)] backdrop-blur-2xl">
    <div
      v-for="metric in metrics"
      :key="metric.id"
      class="grid grid-cols-[minmax(0,1fr)_auto_auto] items-center gap-3 border-b border-stone-200/65 px-4 py-3 last:border-b-0"
    >
      <p class="min-w-0 text-sm font-semibold text-stone-700">{{ metric.label }}</p>
      <span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">{{ metric.delta }}</span>
      <p class="min-w-12 text-right text-2xl font-semibold tracking-[-0.04em] text-stone-950">{{ metric.score }}</p>
    </div>
  </div>

  <div v-else class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
    <article
      v-for="metric in metrics"
      :key="metric.id"
      class="rounded-2xl border border-white/65 bg-white/44 p-4 shadow-[0_18px_54px_rgba(85,68,42,0.06)] backdrop-blur-2xl"
    >
      <div class="flex items-start justify-between gap-3">
        <p class="text-sm font-semibold text-stone-700">{{ metric.label }}</p>
        <span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">{{ metric.delta }}</span>
      </div>
      <div class="mt-5 flex items-end justify-between gap-4">
        <p class="text-3xl font-semibold tracking-[-0.04em] text-stone-950">{{ metric.score }}</p>
        <p class="pb-1 text-xs font-semibold uppercase tracking-[0.16em] text-stone-400">/100</p>
      </div>
      <div class="mt-3 h-1.5 overflow-hidden rounded-full bg-stone-200/70">
        <div class="h-full rounded-full bg-stone-950" :style="{ width: `${metric.score}%` }" />
      </div>
      <p v-if="metric.comment" class="mt-3 text-xs font-medium leading-5 text-stone-500">{{ metric.comment }}</p>
    </article>
  </div>
</template>
