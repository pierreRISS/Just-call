<script setup>
defineProps({
  pendingCount: { type: Number, required: true },
  totalCalls: { type: Number, required: true },
  totalProspects: { type: Number, required: true },
  conversionRate: { type: Number, required: true },
})
</script>

<template>
  <header class="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
    <div>
      <p class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700">Just Call</p>
      <h1 class="mt-2 text-3xl font-bold leading-tight text-slate-950 sm:text-4xl">
        Call workspace
      </h1>
      <p class="mt-2 max-w-2xl text-sm font-medium leading-6 text-slate-600">
        Un CRM de prospection concentre sur la cadence, le contexte et la prochaine action.
      </p>
    </div>

    <div class="grid grid-cols-2 gap-2 sm:min-w-[36rem] sm:grid-cols-4">
      <div class="rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-500">Prospects</p>
        <p class="mt-1 text-3xl font-bold">{{ totalProspects }}</p>
      </div>
      <div class="rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-500">A appeler</p>
        <p class="mt-1 text-3xl font-bold">{{ pendingCount }}</p>
      </div>
      <div class="rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-500">Appeles</p>
        <p class="mt-1 text-3xl font-bold">{{ totalCalls }}</p>
      </div>
      <div class="rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-slate-500">Progression</p>
        <p class="mt-1 text-3xl font-bold">{{ conversionRate }}%</p>
      </div>
    </div>
  </header>
</template>
