<script setup>
defineProps({
  form: { type: Object, required: true },
  prospectCount: { type: Number, required: true },
})

defineEmits(['close', 'start'])
</script>

<template>
  <div class="fixed inset-0 z-40 grid place-items-center bg-slate-950/70 px-4 py-6" role="dialog" aria-modal="true">
    <form class="w-full max-w-xl rounded-md border border-slate-200 bg-white shadow-2xl" @submit.prevent="$emit('start')">
      <div class="border-b border-slate-200 px-5 py-4">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">Calling session</p>
        <h2 class="mt-1 text-2xl font-bold text-slate-950">Definir la pression</h2>
        <p class="mt-2 text-sm font-medium leading-6 text-slate-600">
          Tu choisis ton objectif et la cadence. Ensuite le timer te pousse a appeler le prochain prospect.
        </p>
      </div>

      <div class="grid gap-4 p-5">
        <div class="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700">
          Prospects disponibles: <span class="font-mono text-slate-950">{{ prospectCount }}</span>
        </div>

        <label class="grid gap-1.5 text-sm font-semibold text-slate-700">
          Objectif de session
          <input v-model="form.goal" required maxlength="160" class="min-h-11 rounded-md border border-slate-300 px-3 outline-none focus:border-blue-600" placeholder="Ex: qualifier 8 prospects chauds" />
        </label>

        <div class="grid gap-3 sm:grid-cols-2">
          <label class="grid gap-1.5 text-sm font-semibold text-slate-700">
            Nombre d'appels vise
            <input v-model.number="form.callTarget" required min="1" max="200" type="number" class="min-h-11 rounded-md border border-slate-300 px-3 outline-none focus:border-blue-600" />
          </label>

          <label class="grid gap-1.5 text-sm font-semibold text-slate-700">
            Appeler toutes les X minutes
            <input v-model.number="form.cadenceMinutes" required min="0.1" max="120" step="0.1" type="number" class="min-h-11 rounded-md border border-slate-300 px-3 outline-none focus:border-blue-600" />
          </label>
        </div>
      </div>

      <div class="flex flex-col-reverse gap-2 border-t border-slate-200 px-5 py-4 sm:flex-row sm:justify-end">
        <button type="button" class="min-h-11 rounded-md border border-slate-300 px-4 font-semibold hover:bg-slate-50" @click="$emit('close')">
          Annuler
        </button>
        <button type="submit" class="min-h-11 rounded-md bg-slate-950 px-4 font-semibold text-white hover:bg-slate-800">
          Lancer la session
        </button>
      </div>
    </form>
  </div>
</template>
