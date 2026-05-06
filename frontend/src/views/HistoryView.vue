<script setup>
defineProps({
  callLogs: { type: Array, required: true },
  formatDateTime: { type: Function, required: true },
  formatDuration: { type: Function, required: true },
  isClearingHistory: { type: Boolean, required: true },
  outcomeLabel: { type: Function, required: true },
})

defineEmits(['clear-history', 'open-log'])
</script>

<template>
  <section class="min-h-[calc(100vh-8.5rem)] bg-white">
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Call intelligence</p>
        <h2 class="text-xl font-semibold text-slate-950">Journal d'appels</h2>
      </div>
      <button type="button" class="min-h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:text-slate-400" :disabled="!callLogs.length || isClearingHistory" @click="$emit('clear-history')">
        Vider
      </button>
    </div>

    <div v-if="callLogs.length" class="overflow-x-auto">
      <table class="min-w-full text-left text-sm">
        <thead class="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
          <tr>
            <th class="px-5 py-3">Prospect</th>
            <th class="px-5 py-3">Numero</th>
            <th class="px-5 py-3">Resultat</th>
            <th class="px-5 py-3">Duree</th>
            <th class="px-5 py-3">Date</th>
            <th class="px-5 py-3">Notes</th>
            <th class="px-5 py-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="log in callLogs" :key="log.id" class="hover:bg-slate-50">
            <td class="px-5 py-4 font-semibold">{{ log.contact_name || 'Sans nom' }}</td>
            <td class="px-5 py-4 font-mono text-slate-700">{{ log.phone_number }}</td>
            <td class="px-5 py-4 font-semibold text-slate-950">{{ outcomeLabel(log.outcome) }}</td>
            <td class="px-5 py-4 font-mono text-slate-600">{{ formatDuration(log.duration_seconds) }}</td>
            <td class="px-5 py-4 text-slate-600">{{ formatDateTime(log.created_at) }}</td>
            <td class="max-w-xl px-5 py-4 text-slate-500">
              <p class="line-clamp-1">{{ log.notes || 'Aucune note' }}</p>
            </td>
            <td class="px-5 py-4 text-right">
              <button type="button" class="min-h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold text-slate-700 hover:bg-white" @click="$emit('open-log', log)">
                Voir details
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="px-4 py-8 text-center font-semibold text-slate-500">Aucun appel enregistre.</p>
  </section>
</template>
