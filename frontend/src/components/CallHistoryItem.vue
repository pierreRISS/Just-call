<script setup lang="ts">
import { computed } from 'vue'
import type { CallRecord } from '../types'

const props = defineProps<{
  call: CallRecord
}>()

defineEmits<{
  replay: [call: CallRecord]
  select: [call: CallRecord]
}>()

const isReplay = computed(() => Boolean(props.call.sourceCallId))
</script>

<template>
  <article class="group grid gap-5 border-b border-stone-200/70 py-6 transition duration-500 hover:border-stone-300/80 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
    <button type="button" class="min-w-0 text-left" @click="$emit('select', call)">
      <div class="flex flex-wrap items-center gap-3">
        <h2 class="text-xl font-semibold tracking-[-0.035em] text-stone-950">{{ call.prospectName }}</h2>
        <span class="rounded-full bg-white/65 px-2.5 py-1 text-xs font-semibold text-stone-500">{{ call.company }}</span>
        <span v-if="isReplay" class="rounded-full bg-stone-950 px-2.5 py-1 text-xs font-semibold text-white">AI Replay</span>
      </div>
      <p class="mt-2 text-sm font-medium text-stone-400">{{ call.date }} · {{ call.duration }}</p>
      <p class="mt-4 max-w-3xl text-sm font-medium leading-6 text-stone-650">{{ call.summary }}</p>
    </button>

    <div class="flex items-center gap-4 md:justify-end">
      <div class="text-right">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-stone-400">
          {{ isReplay ? 'Replay score' : 'Score' }}
        </p>
        <p class="mt-1 text-3xl font-semibold tracking-[-0.04em] text-stone-950">{{ call.score }}</p>
      </div>
      <button
        type="button"
        class="rounded-full border border-white/70 bg-white/55 px-4 py-2 text-sm font-semibold text-stone-700 shadow-sm backdrop-blur-xl transition hover:-translate-y-0.5 hover:bg-white"
        @click="isReplay ? $emit('select', call) : $emit('replay', call)"
      >
        {{ isReplay ? 'Review replay' : 'Jouer IA' }}
      </button>
    </div>
  </article>
</template>
