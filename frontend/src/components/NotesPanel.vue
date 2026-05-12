<script setup lang="ts">
defineProps<{
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
  save: []
}>()
</script>

<template>
  <section class="rounded-[2rem] border border-white/70 bg-white/46 p-5 shadow-[0_24px_90px_rgba(85,68,42,0.08)] backdrop-blur-2xl">
    <div class="flex items-center justify-between gap-4">
      <div>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Live notes</p>
        <h2 class="mt-1 text-xl font-semibold tracking-[-0.03em] text-stone-950">Clean capture</h2>
      </div>
      <button
        type="button"
        class="rounded-full bg-stone-950 px-4 py-2 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5"
        @click="$emit('save')"
      >
        Save
      </button>
    </div>

    <textarea
      :value="modelValue"
      class="mt-5 min-h-[22rem] w-full resize-none rounded-[1.5rem] border border-stone-200/70 bg-white/58 px-5 py-4 text-[0.95rem] font-medium leading-7 text-stone-800 outline-none transition placeholder:text-stone-300 focus:border-stone-300 focus:bg-white/80 focus:shadow-[0_18px_70px_rgba(85,68,42,0.08)]"
      placeholder="Capture concise notes, objections, emotional signals, and next steps."
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
  </section>
</template>
