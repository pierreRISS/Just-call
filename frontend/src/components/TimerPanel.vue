<script setup>
defineProps({
  activeCall: { type: Object, default: null },
  countdownLabel: { type: String, required: true },
  isRunning: { type: Boolean, required: true },
  panelClass: { type: String, required: true },
  progress: { type: Number, required: true },
  timerTone: { type: String, required: true },
  barClass: { type: String, required: true },
})

defineEmits(['start', 'pause', 'reset'])
</script>

<template>
  <section class="rounded-md border p-4 shadow-sm transition-colors" :class="panelClass">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.16em] opacity-75">Next call timer</p>
        <p class="mt-2 font-mono text-5xl font-semibold tabular-nums">{{ countdownLabel }}</p>
      </div>
      <span class="rounded-md border border-current/15 bg-white/60 px-3 py-2 text-xs font-semibold uppercase tracking-[0.12em]">
        {{ timerTone === 'danger' ? 'Go now' : timerTone === 'warning' ? 'Pressure' : 'Cadence' }}
      </span>
    </div>

    <div class="mt-4 h-2 overflow-hidden rounded-full bg-white/25">
      <div class="h-full rounded-full transition-all duration-500" :class="barClass" :style="{ width: `${progress}%` }" />
    </div>

    <div class="mt-4 grid grid-cols-3 gap-2">
      <button
        type="button"
        class="min-h-10 rounded-md bg-slate-950 px-3 font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
        :disabled="isRunning || Boolean(activeCall)"
        @click="$emit('start')"
      >
        Start
      </button>
      <button
        type="button"
        class="min-h-10 rounded-md border border-current/20 bg-white/50 px-3 font-semibold hover:bg-white disabled:cursor-not-allowed disabled:text-slate-400"
        :disabled="!isRunning || Boolean(activeCall)"
        @click="$emit('pause')"
      >
        Pause
      </button>
      <button type="button" class="min-h-10 rounded-md border border-current/20 bg-white/50 px-3 font-semibold hover:bg-white" @click="$emit('reset')">
        Reset
      </button>
    </div>
  </section>
</template>
