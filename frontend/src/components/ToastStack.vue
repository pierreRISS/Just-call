<script setup>
defineProps({
  toasts: { type: Array, required: true },
})

defineEmits(['dismiss'])
</script>

<template>
  <div class="fixed right-4 top-4 z-50 grid w-[min(24rem,calc(100vw-2rem))] gap-2">
    <article
      v-for="toast in toasts"
      :key="toast.id"
      class="border bg-white px-4 py-3 shadow-lg"
      :class="toast.type === 'error' ? 'border-red-200 text-red-950' : 'border-blue-200 text-blue-950'"
    >
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.14em] opacity-70">
            {{ toast.type === 'error' ? 'Erreur' : 'Info' }}
          </p>
          <p class="mt-1 text-sm font-semibold leading-5">{{ toast.message }}</p>
        </div>
        <button type="button" class="text-sm font-semibold opacity-60 hover:opacity-100" @click="$emit('dismiss', toast.id)">
          Fermer
        </button>
      </div>
    </article>
  </div>
</template>
