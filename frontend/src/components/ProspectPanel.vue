<script setup lang="ts">
import type { Prospect } from '../types'

defineProps<{
  prospect: Prospect
}>()
</script>

<template>
  <aside class="rounded-[2rem] border border-white/70 bg-white/48 p-5 shadow-[0_24px_80px_rgba(85,68,42,0.09)] backdrop-blur-2xl">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Prospect</p>
        <h2 class="mt-2 truncate text-2xl font-semibold tracking-[-0.04em] text-stone-950">{{ prospect.name }}</h2>
        <p class="mt-1 text-sm font-medium text-stone-500">{{ prospect.role }} at {{ prospect.company }}</p>
      </div>
      <span class="rounded-full bg-white/65 px-3 py-1 text-xs font-semibold text-stone-600 shadow-sm">
        {{ prospect.temperature }}
      </span>
    </div>

    <div class="mt-6 grid gap-3 text-sm">
      <p class="font-mono font-medium text-stone-700">{{ prospect.phone }}</p>
      <p class="font-medium text-stone-500">{{ prospect.email }}</p>
    </div>

    <p class="mt-6 text-sm font-medium leading-6 text-stone-650">{{ prospect.context }}</p>

    <div class="mt-6 flex flex-wrap gap-2">
      <span
        v-for="signal in prospect.prioritySignals"
        :key="signal"
        class="rounded-full border border-stone-200/80 bg-white/55 px-3 py-1.5 text-xs font-semibold text-stone-600"
      >
        {{ signal }}
      </span>
    </div>

    <div class="mt-6 rounded-2xl bg-stone-950/[0.035] px-4 py-3">
      <p class="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-stone-400">Last touch</p>
      <p class="mt-1 text-sm font-semibold text-stone-700">{{ prospect.lastTouch }}</p>
    </div>
  </aside>
</template>
