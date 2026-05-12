<script setup lang="ts">
import type { Toast } from '../types'

defineProps<{
  toasts: Toast[]
}>()

defineEmits<{
  dismiss: [id: number]
}>()
</script>

<template>
  <div class="fixed right-5 top-5 z-50 grid w-[min(24rem,calc(100vw-2.5rem))] gap-2">
    <TransitionGroup name="toast">
      <article
        v-for="toast in toasts"
        :key="toast.id"
        class="rounded-2xl border border-white/70 bg-white/70 px-4 py-3 shadow-[0_22px_70px_rgba(80,61,35,0.14)] backdrop-blur-2xl"
        :class="toast.type === 'error' ? 'border-red-200/70' : ''"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-stone-400">
              {{ toast.type === 'error' ? 'Sync issue' : toast.type === 'success' ? 'Saved' : 'Workspace' }}
            </p>
            <p class="mt-1 text-sm font-medium leading-5 text-stone-800">{{ toast.message }}</p>
          </div>
          <button
            type="button"
            class="rounded-full px-2 py-1 text-xs font-semibold text-stone-400 transition hover:bg-stone-100 hover:text-stone-800"
            @click="$emit('dismiss', toast.id)"
          >
            Close
          </button>
        </div>
      </article>
    </TransitionGroup>
  </div>
</template>
