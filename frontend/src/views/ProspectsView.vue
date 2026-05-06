<script setup>
defineProps({
  editForm: { type: Object, required: true },
  isAddOpen: { type: Boolean, required: true },
  isDetailOpen: { type: Boolean, required: true },
  contacts: { type: Array, required: true },
  contactForm: { type: Object, required: true },
  formatDateTime: { type: Function, required: true },
  selectedProspect: { type: Object, default: null },
})

defineEmits(['add-contact', 'close-add', 'close-detail', 'open-add', 'remove-contact', 'save-prospect', 'select-prospect'])
</script>

<template>
  <section class="relative min-h-[calc(100vh-8.5rem)] overflow-hidden bg-white">
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Base prospects</p>
        <h2 class="text-xl font-bold">{{ contacts.length }} prospects</h2>
      </div>
      <button type="button" class="min-h-10 rounded-md bg-blue-700 px-4 font-semibold text-white hover:bg-blue-800" @click="$emit('open-add')">
        Ajouter prospect
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full text-left text-sm">
        <thead class="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
          <tr>
            <th class="px-5 py-3">Prospect</th>
            <th class="px-5 py-3">Telephone</th>
            <th class="px-5 py-3">Statut</th>
            <th class="px-5 py-3">Dernier appel</th>
            <th class="px-5 py-3">Contexte</th>
            <th class="px-5 py-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody v-if="contacts.length" class="divide-y divide-slate-200">
          <tr v-for="contact in contacts" :key="contact.id" class="cursor-pointer hover:bg-slate-50" @click="$emit('select-prospect', contact.id)">
            <td class="px-5 py-4 font-semibold text-slate-950">{{ contact.name || 'Sans nom' }}</td>
            <td class="px-5 py-4 font-mono text-slate-700">{{ contact.phone_number }}</td>
            <td class="px-5 py-4">
              <span class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
                {{ contact.last_called_at ? 'Appele' : 'A appeler' }}
              </span>
            </td>
            <td class="px-5 py-4 font-medium text-slate-600">{{ formatDateTime(contact.last_called_at) }}</td>
            <td class="max-w-xl px-5 py-4 text-slate-600">
              <p class="line-clamp-1">{{ contact.notes || 'Aucun contexte' }}</p>
            </td>
            <td class="px-5 py-4 text-right">
              <button type="button" class="min-h-9 rounded-md border border-red-200 bg-white px-3 text-sm font-semibold text-red-700 hover:bg-red-50" @click.stop="$emit('remove-contact', contact.id)">
                Retirer
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-if="!contacts.length" class="px-4 py-16 text-center font-semibold text-slate-500">
        Ajoute tes premiers prospects avant de lancer Calling.
      </p>
    </div>

    <div v-if="isAddOpen || isDetailOpen" class="absolute inset-0 z-10 bg-slate-950/10" @click="$emit(isAddOpen ? 'close-add' : 'close-detail')" />

    <div v-if="isAddOpen" class="absolute inset-y-0 right-0 z-20 w-full max-w-lg border-l border-slate-200 bg-white shadow-2xl">
      <form class="grid h-full grid-rows-[auto_1fr_auto]" @submit.prevent="$emit('add-contact')">
        <div class="flex items-start justify-between gap-3 border-b border-slate-200 px-4 py-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">Nouveau</p>
            <h2 class="text-xl font-bold">Ajouter un prospect</h2>
          </div>
          <button type="button" class="min-h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold hover:bg-slate-50" @click="$emit('close-add')">
            Fermer
          </button>
        </div>
        <div class="grid content-start gap-3 overflow-y-auto p-4">
          <input v-model="contactForm.name" maxlength="120" type="text" class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600" placeholder="Nom, entreprise ou contact" />
          <input v-model="contactForm.phone_number" maxlength="40" type="tel" required class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600" placeholder="+33 6 12 34 56 78" />
          <textarea v-model="contactForm.notes" maxlength="2000" rows="10" class="resize-none rounded-md border border-slate-300 bg-white px-3 py-2 outline-none focus:border-blue-600" placeholder="Entreprise, role, secteur, site, LinkedIn, contexte, objection probable..." />
        </div>
        <div class="border-t border-slate-200 p-4">
          <button type="submit" class="min-h-11 w-full rounded-md bg-blue-700 px-4 font-semibold text-white hover:bg-blue-800">Ajouter</button>
        </div>
      </form>
    </div>

    <div v-if="isDetailOpen && selectedProspect" class="absolute inset-y-0 right-0 z-20 w-full max-w-lg border-l border-slate-200 bg-white shadow-2xl">
      <form class="grid h-full grid-rows-[auto_1fr_auto]" @submit.prevent="$emit('save-prospect')">
        <div class="flex items-start justify-between gap-3 border-b border-slate-200 px-4 py-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Base prospects</p>
            <h2 class="text-xl font-bold">Fiche prospect</h2>
          </div>
          <button type="button" class="min-h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold hover:bg-slate-50" @click="$emit('close-detail')">
            Fermer
          </button>
        </div>
        <div class="grid content-start gap-4 overflow-y-auto p-4">
          <label class="grid gap-1.5 text-sm font-semibold text-slate-700">
            Nom / entreprise
            <input v-model="editForm.name" maxlength="120" class="min-h-11 rounded-md border border-slate-300 px-3 outline-none focus:border-blue-600" />
          </label>
          <label class="grid gap-1.5 text-sm font-semibold text-slate-700">
            Telephone
            <input v-model="editForm.phone_number" maxlength="40" required class="min-h-11 rounded-md border border-slate-300 px-3 font-mono outline-none focus:border-blue-600" />
          </label>
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Dernier appel</p>
            <p class="mt-1 font-semibold">{{ formatDateTime(selectedProspect.last_called_at) }}</p>
          </div>
          <label class="grid gap-1.5 text-sm font-semibold text-slate-700">
            Notes / contexte
            <textarea v-model="editForm.notes" maxlength="2000" rows="12" class="resize-none rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600" />
          </label>
        </div>
        <div class="border-t border-slate-200 p-4">
          <button type="submit" class="min-h-11 w-full rounded-md bg-slate-950 px-4 font-semibold text-white hover:bg-slate-800">
            Enregistrer
          </button>
        </div>
      </form>
    </div>
  </section>
</template>
