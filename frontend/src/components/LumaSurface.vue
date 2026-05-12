<script setup lang="ts">
defineProps<{
  subtle?: boolean
}>()
</script>

<template>
  <section
    class="rounded-[2rem] border backdrop-blur-2xl transition duration-500"
    :class="subtle ? 'border-white/55 bg-white/32 shadow-[0_18px_70px_rgba(85,68,42,0.06)]' : 'border-white/70 bg-white/50 shadow-[0_28px_100px_rgba(85,68,42,0.09)]'"
  >
    <slot />
  </section>
</template>
