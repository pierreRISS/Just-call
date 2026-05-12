<script setup lang="ts">
import { computed } from 'vue'
import type { CallRecord, ReplaySession } from '../types'
import ScoreMetricList from './ScoreMetricList.vue'

const props = defineProps<{
  call: CallRecord | null
  calls: CallRecord[]
  replaySessions: ReplaySession[]
}>()

defineEmits<{
  close: []
  replay: [call: CallRecord]
}>()

const sourceCall = computed(() => {
  if (!props.call?.sourceCallId) return null
  return props.calls.find((call) => call.id === props.call?.sourceCallId) ?? null
})

const relatedReplayCalls = computed(() => {
  if (!props.call) return []
  return props.calls.filter((call) => call.sourceCallId === props.call?.id)
})

const relatedReplaySessions = computed(() => {
  if (!props.call) return []
  return props.replaySessions.filter((session) => session.callId === props.call?.id)
})

const comparison = computed(() => {
  if (!props.call || !sourceCall.value) return null
  return props.call.metrics.map((metric) => {
    const original = sourceCall.value?.metrics.find((item) => item.id === metric.id)
    return {
      label: metric.label,
      original: original?.score ?? 0,
      replay: metric.score,
      diff: metric.score - (original?.score ?? 0),
    }
  })
})
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="call" class="fixed inset-0 z-[80]">
        <button type="button" class="absolute inset-0 bg-stone-950/18 backdrop-blur-[2px]" aria-label="Close call details" @click="$emit('close')" />

        <aside class="absolute right-0 top-0 h-full w-full max-w-xl overflow-y-auto border-l border-white/65 bg-[#f8f4ec]/95 p-5 shadow-[-30px_0_90px_rgba(55,45,30,0.18)] backdrop-blur-2xl sm:p-7">
          <div class="flex items-start justify-between gap-5">
            <div class="min-w-0">
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">
                {{ call.sourceCallId ? 'AI replay call' : 'Call review' }}
              </p>
              <h2 class="mt-3 text-3xl font-semibold tracking-[-0.055em] text-stone-950">{{ call.prospectName }}</h2>
              <p class="mt-2 text-sm font-semibold text-stone-500">{{ call.company }} · {{ call.date }} · {{ call.duration }}</p>
            </div>
            <button
              type="button"
              class="grid h-10 w-10 shrink-0 place-items-center rounded-full border border-white/70 bg-white/60 text-lg font-semibold text-stone-500 shadow-sm transition hover:bg-white hover:text-stone-950"
              aria-label="Close call details"
              @click="$emit('close')"
            >
              ×
            </button>
          </div>

          <div class="mt-7 rounded-3xl border border-white/70 bg-white/48 p-5 shadow-[0_20px_70px_rgba(85,68,42,0.08)] backdrop-blur-2xl">
            <div class="flex items-end justify-between gap-4">
              <div>
                <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Global score</p>
                <p class="mt-3 text-6xl font-semibold tracking-[-0.075em] text-stone-950">{{ call.score }}</p>
              </div>
              <button
                v-if="!call.sourceCallId"
                type="button"
                class="rounded-full bg-stone-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.2)] transition hover:-translate-y-0.5"
                @click="$emit('replay', call)"
              >
                Start simulation
              </button>
            </div>
            <p class="mt-5 text-sm font-medium leading-6 text-stone-650">{{ call.summary }}</p>

            <div class="mt-6 border-t border-stone-200/70 pt-5">
              <div class="mb-3 flex items-center justify-between gap-3">
                <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">AI scorecard</p>
                <span class="rounded-full bg-white/70 px-3 py-1 text-xs font-semibold text-stone-500">5 scores</span>
              </div>
              <ScoreMetricList :metrics="call.metrics" compact />
            </div>
          </div>

          <section v-if="sourceCall && comparison" class="mt-5 rounded-3xl border border-white/70 bg-white/44 p-5 shadow-[0_18px_60px_rgba(85,68,42,0.07)] backdrop-blur-2xl">
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Replay improvement</p>
            <div class="mt-4 grid gap-3">
              <div v-for="metric in comparison" :key="metric.label" class="flex items-center justify-between gap-3 rounded-2xl bg-white/55 px-4 py-3">
                <p class="text-sm font-semibold text-stone-700">{{ metric.label }}</p>
                <p class="text-sm font-semibold" :class="metric.diff >= 0 ? 'text-emerald-700' : 'text-rose-700'">
                  {{ metric.original }} → {{ metric.replay }} · {{ metric.diff >= 0 ? '+' : '' }}{{ metric.diff }}
                </p>
              </div>
            </div>
          </section>

          <section class="mt-5 grid gap-4">
            <div class="rounded-3xl border border-white/70 bg-white/44 p-5 shadow-[0_18px_60px_rgba(85,68,42,0.07)] backdrop-blur-2xl">
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Strengths</p>
              <div class="mt-4 grid gap-3">
                <p class="rounded-2xl bg-white/55 px-4 py-3 text-sm font-medium leading-6 text-stone-650">You kept control of the conversation without rushing the prospect.</p>
                <p class="rounded-2xl bg-white/55 px-4 py-3 text-sm font-medium leading-6 text-stone-650">You reflected the business context before moving into the pitch.</p>
              </div>
            </div>

            <div class="rounded-3xl border border-white/70 bg-white/44 p-5 shadow-[0_18px_60px_rgba(85,68,42,0.07)] backdrop-blur-2xl">
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Improvement focus</p>
              <p class="mt-4 rounded-2xl bg-white/55 px-4 py-3 text-sm font-medium leading-6 text-stone-650">
                Slow down after the first objection and make the next step feel more concrete before closing.
              </p>
            </div>
          </section>

          <section class="mt-5 rounded-3xl border border-white/70 bg-white/44 p-5 shadow-[0_18px_60px_rgba(85,68,42,0.07)] backdrop-blur-2xl">
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Notes and transcript</p>
            <p class="mt-4 whitespace-pre-line text-sm font-medium leading-6 text-stone-650">{{ call.transcriptPreview }}</p>
          </section>

          <section v-if="!call.sourceCallId" class="mt-5 rounded-3xl border border-white/70 bg-white/44 p-5 shadow-[0_18px_60px_rgba(85,68,42,0.07)] backdrop-blur-2xl">
            <div class="flex items-center justify-between gap-3">
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Replay history</p>
              <span class="rounded-full bg-white/60 px-3 py-1 text-xs font-semibold text-stone-500">
                {{ relatedReplayCalls.length + relatedReplaySessions.length }}
              </span>
            </div>
            <div class="mt-4 grid gap-3">
              <p v-if="!relatedReplayCalls.length && !relatedReplaySessions.length" class="text-sm font-medium leading-6 text-stone-500">
                No simulation has been started from this call yet.
              </p>
              <div v-for="replay in relatedReplayCalls" :key="replay.id" class="rounded-2xl bg-white/55 px-4 py-3">
                <p class="text-sm font-semibold text-stone-800">{{ replay.date }} · Score {{ replay.score }}</p>
                <p class="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-700">
                  +{{ Math.max(0, replay.score - call.score) }} vs original
                </p>
              </div>
              <div v-for="session in relatedReplaySessions" :key="session.id" class="rounded-2xl bg-white/55 px-4 py-3">
                <p class="text-sm font-semibold text-stone-800">{{ session.simulationMode }}</p>
                <p class="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-stone-400">{{ session.difficulty }} · {{ session.prospectBehavior }}</p>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>
