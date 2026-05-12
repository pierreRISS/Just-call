<script setup lang="ts">
import type { Prospect } from '../types'

defineProps<{
  prospects: Prospect[]
  selectedProspectId?: number
}>()

defineEmits<{
  call: [prospect: Prospect]
  select: [prospect: Prospect]
}>()
</script>

<template>
  <section class="rounded-[2rem] border border-white/70 bg-white/45 shadow-[0_28px_100px_rgba(85,68,42,0.08)] backdrop-blur-2xl">
    <p v-if="!prospects.length" class="px-6 py-14 text-center text-sm font-semibold text-stone-400">
      No prospects yet.
    </p>

    <div class="hidden grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)_8rem_7rem] gap-4 border-b border-stone-200/70 px-6 py-5 text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400 min-[1180px]:grid">
      <span>Name</span>
      <span>Company</span>
      <span>Status</span>
      <span class="text-right">Action</span>
    </div>

    <div v-if="prospects.length" class="divide-y divide-stone-200/65">
      <article
        v-for="prospect in prospects"
        :key="prospect.id"
        class="grid gap-4 px-5 py-5 transition duration-300 hover:bg-white/42 sm:px-6 min-[1180px]:grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)_8rem_7rem] min-[1180px]:items-center"
        :class="prospect.id === selectedProspectId ? 'bg-white/62 shadow-[inset_3px_0_0_rgba(28,25,23,0.9)]' : ''"
      >
        <button type="button" class="group min-w-0 text-left" @click="$emit('select', prospect)">
          <p class="truncate font-semibold tracking-[-0.02em] text-stone-950">{{ prospect.name }}</p>
          <p class="mt-1 truncate text-xs font-medium text-stone-400">{{ prospect.email || prospect.phone }}</p>
          <p class="mt-2 text-xs font-semibold text-stone-400 opacity-0 transition group-hover:opacity-100">Open details</p>
        </button>

        <div class="min-w-0">
          <p class="text-[0.62rem] font-semibold uppercase tracking-[0.16em] text-stone-400 min-[1180px]:hidden">Company</p>
          <p class="truncate text-sm font-medium text-stone-650">{{ prospect.company }}</p>
          <p class="mt-1 truncate text-xs font-medium text-stone-400">
            {{ prospect.role }} · {{ prospect.priority }} priority · {{ prospect.lastCall }}
          </p>
        </div>

        <div>
          <span class="rounded-full bg-white/65 px-3 py-1.5 text-xs font-semibold text-stone-650 shadow-sm">{{ prospect.status }}</span>
        </div>

        <div class="flex justify-start min-[1180px]:justify-end">
          <button
            type="button"
            class="rounded-full bg-stone-950 px-4 py-2 text-sm font-semibold text-white opacity-90 shadow-[0_14px_34px_rgba(28,25,23,0.16)] transition hover:-translate-y-0.5 hover:opacity-100"
            @click="$emit('call', prospect)"
          >
            Quick Call
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
