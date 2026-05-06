<script setup>
defineProps({
  formatDateTime: { type: Function, required: true },
  formatDuration: { type: Function, required: true },
  log: { type: Object, required: true },
  outcomeLabel: { type: Function, required: true },
})

defineEmits(['close'])
</script>

<template>
  <div class="fixed inset-0 z-30 bg-slate-950/10" role="dialog" aria-modal="true" @click.self="$emit('close')">
    <section class="absolute inset-y-0 right-0 grid w-full max-w-lg grid-rows-[auto_1fr] border-l border-slate-200 bg-white shadow-2xl">
      <div class="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">Call record</p>
          <h2 class="mt-1 break-words text-2xl font-semibold">{{ log.contact_name || 'Sans nom' }}</h2>
          <p class="mt-1 font-mono text-sm font-bold text-slate-600">{{ log.phone_number }}</p>
        </div>
        <button type="button" class="min-h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold hover:bg-slate-50" @click="$emit('close')">
          Fermer
        </button>
      </div>

      <div class="grid content-start gap-4 overflow-y-auto p-5">
        <div class="grid grid-cols-2 gap-3">
          <div class="border border-slate-200 bg-slate-50 p-3">
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Resultat</p>
            <p class="mt-1 text-lg font-semibold">{{ outcomeLabel(log.outcome) }}</p>
          </div>
          <div class="border border-slate-200 bg-slate-50 p-3">
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Duree</p>
            <p class="mt-1 font-mono text-lg font-semibold">{{ formatDuration(log.duration_seconds) }}</p>
          </div>
        </div>

        <div class="border border-slate-200 p-3">
          <p class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Cree le</p>
          <p class="mt-1 font-bold">{{ formatDateTime(log.created_at) }}</p>
        </div>

        <div class="border border-slate-200 p-3">
          <p class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Notes</p>
          <p class="mt-2 whitespace-pre-wrap break-words text-sm font-semibold leading-6 text-slate-700">
            {{ log.notes || 'Aucune note pour cet appel.' }}
          </p>
        </div>
      </div>
    </section>
  </div>
</template>
