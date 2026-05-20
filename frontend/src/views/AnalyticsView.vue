<script setup lang="ts">
import { computed, ref } from 'vue'
import LumaSurface from '../components/LumaSurface.vue'
import MetricCard from '../components/MetricCard.vue'
import { useWorkspaceStore } from '../stores/workspace'
import type { CallRecord } from '../types'

const workspace = useWorkspaceStore()
const analyticsMode = ref<'real' | 'training'>('real')
const reviewedCalls = computed(() => workspace.callRecords.filter((call) => !call.sourceCallId && call.status === 'completed'))
const replayCalls = computed(() => workspace.callRecords.filter((call) => call.sourceCallId && call.status === 'completed'))
const visibleCalls = computed(() =>
  analyticsMode.value === 'real' ? reviewedCalls.value : workspace.callRecords.filter((call) => call.status === 'completed'),
)
const averageScore = computed(() => {
  if (!visibleCalls.value.length) return 0
  return Math.round(visibleCalls.value.reduce((total, call) => total + call.score, 0) / visibleCalls.value.length)
})
const conversionMomentum = computed(() => {
  const scores = visibleCalls.value.slice(0, 10).reverse().map((call) => call.score)
  return scores.length ? scores : [0]
})
const talkListen = computed(() => {
  const calls = Math.max(1, visibleCalls.value.length)
  const replayCount = visibleCalls.value.filter((call) => call.sourceCallId).length
  const replayRatio = Math.round((replayCount / calls) * 100)
  return [
    { label: 'Real calls', value: 100 - replayRatio },
    { label: 'AI replays', value: replayRatio },
  ]
})
const visibleMetrics = computed(() => aggregateMetrics(visibleCalls.value))

function aggregateMetrics(calls: CallRecord[]) {
  return workspace.performanceMetrics.map((metric) => {
    const matchingMetrics = calls.flatMap((call) => call.metrics.filter((item) => item.id === metric.id))
    if (!matchingMetrics.length) return { ...metric, score: 0 }
    return {
      ...metric,
      score: Math.round(matchingMetrics.reduce((total, item) => total + item.score, 0) / matchingMetrics.length),
    }
  })
}
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

    <div class="flex w-fit rounded-full border border-white/70 bg-white/45 p-1 shadow-sm backdrop-blur-xl">
      <button
        type="button"
        class="rounded-full px-4 py-2 text-sm font-semibold transition"
        :class="analyticsMode === 'real' ? 'bg-stone-950 text-white' : 'text-stone-500 hover:text-stone-950'"
        @click="analyticsMode = 'real'"
      >
        Vrais appels
      </button>
      <button
        type="button"
        class="rounded-full px-4 py-2 text-sm font-semibold transition"
        :class="analyticsMode === 'training' ? 'bg-stone-950 text-white' : 'text-stone-500 hover:text-stone-950'"
        @click="analyticsMode = 'training'"
      >
        IA + entraînement
      </button>
    </div>

    <LumaSurface v-if="!visibleCalls.length" class="p-8 text-center" subtle>
      <p class="text-sm font-semibold text-stone-500">
        No data for this mode yet.
      </p>
    </LumaSurface>

    <div v-else class="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
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

    <div v-if="visibleCalls.length" class="grid gap-5 md:grid-cols-3">
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

    <div v-if="visibleCalls.length" class="grid gap-5 md:grid-cols-5">
      <MetricCard v-for="metric in visibleMetrics" :key="metric.id" :metric="metric" />
    </div>
  </section>
</template>
