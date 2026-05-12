<script setup lang="ts">
import type { AiReview } from '../types'
import ScoreMetricList from './ScoreMetricList.vue'

withDefaults(defineProps<{
  review: AiReview
  comparison?: Array<{ label: string; original: number; replay: number; diff: number }>
}>(), {
  comparison: () => [],
})

defineEmits<{
  replay: []
}>()
</script>

<template>
  <section class="rounded-[2rem] border border-white/70 bg-white/50 p-6 shadow-[0_28px_100px_rgba(85,68,42,0.09)] backdrop-blur-2xl sm:p-8">
    <div class="grid gap-8 lg:grid-cols-[16rem_1fr]">
      <div>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Global score</p>
        <p class="mt-4 text-7xl font-semibold tracking-[-0.08em] text-stone-950">{{ review.score }}</p>
      </div>

      <div class="grid gap-7">
        <div>
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">AI summary</p>
          <p class="mt-3 max-w-3xl text-lg font-medium leading-8 text-stone-700">{{ review.summary }}</p>
        </div>

        <ScoreMetricList :metrics="review.metrics" />

        <div v-if="comparison.length" class="rounded-[1.5rem] bg-stone-950/[0.035] p-4">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Original vs replay</p>
          <div class="mt-3 grid gap-2">
            <div v-for="metric in comparison" :key="metric.label" class="flex items-center justify-between gap-3 rounded-2xl bg-white/55 px-3 py-2">
              <p class="text-sm font-semibold text-stone-700">{{ metric.label }}</p>
              <p class="text-sm font-semibold" :class="metric.diff >= 0 ? 'text-emerald-700' : 'text-rose-700'">
                {{ metric.original }} → {{ metric.replay }} · {{ metric.diff >= 0 ? '+' : '' }}{{ metric.diff }}
              </p>
            </div>
          </div>
        </div>

        <div class="grid gap-3">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Strengths</p>
          <p v-for="strength in review.strengths" :key="strength" class="text-sm font-medium leading-6 text-stone-650">
            {{ strength }}
          </p>
        </div>

        <div class="rounded-[1.5rem] bg-stone-950/[0.035] p-4">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Next improvement focus</p>
          <p class="mt-2 text-sm font-semibold leading-6 text-stone-700">{{ review.improvementFocus }}</p>
        </div>

        <button
          type="button"
          class="w-fit rounded-full bg-stone-950 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5"
          @click="$emit('replay')"
        >
          Replay with AI simulation
        </button>
      </div>
    </div>
  </section>
</template>
