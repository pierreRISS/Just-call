<script setup lang="ts">
import { computed } from 'vue'
import LumaSurface from '../components/LumaSurface.vue'
import MetricCard from '../components/MetricCard.vue'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()
const reviewedCalls = computed(() => workspace.callRecords.filter((call) => !call.sourceCallId))
const replayCalls = computed(() => workspace.callRecords.filter((call) => call.sourceCallId))
const averageScore = computed(() => {
  if (!workspace.callRecords.length) return 0
  return Math.round(workspace.callRecords.reduce((total, call) => total + call.score, 0) / workspace.callRecords.length)
})
const conversionMomentum = computed(() => {
  const scores = workspace.callRecords.slice(0, 10).reverse().map((call) => call.score)
  return scores.length ? scores : [0]
})
const talkListen = computed(() => {
  const calls = Math.max(1, workspace.callRecords.length)
  const replayRatio = Math.round((replayCalls.value.length / calls) * 100)
  return [
    { label: 'Real calls', value: 100 - replayRatio },
    { label: 'AI replays', value: replayRatio },
  ]
})
</script>

<template>
  <section class="grid gap-8">
    <div class="max-w-3xl">
      <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Analytics</p>
      <h2 class="mt-3 text-4xl font-semibold tracking-[-0.06em] text-stone-950 sm:text-5xl">Signals that actually matter.</h2>
      <p class="mt-5 text-sm font-medium leading-6 text-stone-500">
        Minimal charts for momentum, listening balance, and quiet skill progression.
      </p>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
      <LumaSurface class="p-6 sm:p-8">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Conversion momentum</p>
        <div class="mt-12 flex h-64 items-end gap-3">
          <span
            v-for="(value, index) in conversionMomentum"
            :key="index"
            class="flex-1 rounded-t-full bg-stone-950/80 transition duration-700 hover:bg-stone-950"
            :style="{ height: `${value}%` }"
          />
        </div>
      </LumaSurface>

      <LumaSurface class="p-6 sm:p-8" subtle>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Talk vs listen</p>
        <div class="mt-10 grid gap-5">
          <div v-for="item in talkListen" :key="item.label">
            <div class="flex justify-between text-sm font-semibold text-stone-650">
              <span>{{ item.label }}</span>
              <span>{{ item.value }}%</span>
            </div>
            <div class="mt-3 h-2 overflow-hidden rounded-full bg-stone-200/70">
              <div class="h-full rounded-full bg-stone-950" :style="{ width: `${item.value}%` }" />
            </div>
          </div>
        </div>
      </LumaSurface>
    </div>

    <div class="grid gap-5 md:grid-cols-3">
      <LumaSurface class="p-6" subtle>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Average score</p>
        <p class="mt-4 text-5xl font-semibold tracking-[-0.06em] text-stone-950">{{ averageScore }}</p>
      </LumaSurface>
      <LumaSurface class="p-6" subtle>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Calls reviewed</p>
        <p class="mt-4 text-5xl font-semibold tracking-[-0.06em] text-stone-950">{{ reviewedCalls.length }}</p>
      </LumaSurface>
      <LumaSurface class="p-6" subtle>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">AI replays</p>
        <p class="mt-4 text-5xl font-semibold tracking-[-0.06em] text-stone-950">{{ replayCalls.length }}</p>
      </LumaSurface>
    </div>

    <div class="grid gap-5 md:grid-cols-5">
      <MetricCard v-for="metric in workspace.metrics" :key="metric.id" :metric="metric" />
    </div>
  </section>
</template>
