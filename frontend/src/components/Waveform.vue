<script setup lang="ts">
const props = defineProps<{
  active?: boolean
  levels?: number[]
}>()

const bars = [32, 52, 28, 74, 46, 84, 38, 62, 30, 70, 48, 88, 42, 58, 34, 66, 40, 76]
</script>

<template>
  <div class="flex h-28 items-center justify-center gap-1.5" aria-hidden="true">
    <span
      v-for="(height, index) in bars"
      :key="index"
      class="waveform-bar w-1.5 rounded-full bg-stone-950/75"
      :class="{ 'is-active': active }"
      :style="{ height: `${props.levels?.[index] ?? height}%`, animationDelay: `${index * 90}ms` }"
    />
  </div>
</template>
