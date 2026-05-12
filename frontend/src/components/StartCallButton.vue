<script setup lang="ts">
defineEmits<{
  start: []
}>()
</script>

<template>
  <button
    type="button"
    class="start-call-button group relative grid h-44 w-44 place-items-center rounded-full border border-white/80 bg-white/62 text-stone-950 shadow-[0_34px_110px_rgba(72,55,29,0.18)] backdrop-blur-2xl transition duration-700 ease-[cubic-bezier(.22,1,.36,1)] hover:scale-[1.025] hover:bg-white/78 focus:outline-none focus:ring-8 focus:ring-white/60 sm:h-56 sm:w-56"
    @click="$emit('start')"
  >
    <span class="absolute inset-3 rounded-full border border-stone-200/70" />
    <span class="absolute inset-[-1rem] rounded-full border border-white/50 opacity-0 transition duration-700 group-hover:inset-[-1.35rem] group-hover:opacity-100" />
    <span class="grid text-center">
      <span class="text-[0.7rem] font-semibold uppercase tracking-[0.24em] text-stone-400">Begin</span>
      <span class="mt-2 text-3xl font-semibold tracking-[-0.05em] sm:text-4xl">Next Call</span>
    </span>
  </button>
</template>
