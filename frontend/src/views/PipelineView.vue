<script setup>
defineProps({
  activeCall: { type: Object, default: null },
  activeCallDuration: { type: String, required: true },
  completedContacts: { type: Array, required: true },
  formatDateTime: { type: Function, required: true },
  pendingContacts: { type: Array, required: true },
})

defineEmits(['remove-contact'])
</script>

<template>
  <section class="grid gap-4 lg:grid-cols-3">
    <div class="rounded-md border border-slate-200 bg-white shadow-sm">
      <div class="border-b border-slate-200 px-4 py-3">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Stage 1</p>
        <h2 class="text-xl font-semibold">A appeler</h2>
      </div>
      <div v-if="pendingContacts.length" class="grid gap-3 p-3">
        <article v-for="contact in pendingContacts" :key="contact.id" class="rounded-md border border-slate-200 bg-slate-50 p-3">
          <p class="break-words font-semibold">{{ contact.name || 'Sans nom' }}</p>
          <p class="mt-1 font-mono text-sm text-slate-700">{{ contact.phone_number }}</p>
          <p v-if="contact.notes" class="mt-2 line-clamp-2 break-words text-sm font-semibold text-slate-500">{{ contact.notes }}</p>
          <button type="button" class="mt-3 min-h-9 rounded-md border border-red-200 bg-white px-3 text-sm font-semibold text-red-700 hover:bg-red-50" @click="$emit('remove-contact', contact.id)">
            Retirer
          </button>
        </article>
      </div>
      <p v-else class="px-4 py-8 text-center font-semibold text-slate-500">Pipeline vide.</p>
    </div>

    <div class="rounded-md border border-blue-200 bg-blue-50 shadow-sm">
      <div class="border-b border-blue-200 px-4 py-3">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">Stage 2</p>
        <h2 class="text-xl font-semibold">En cours</h2>
      </div>
      <div class="p-3">
        <article v-if="activeCall" class="rounded-md border border-blue-300 bg-white p-4 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-700">Live call</p>
          <p class="mt-2 break-words text-xl font-semibold">{{ activeCall.name || 'Sans nom' }}</p>
          <p class="mt-1 font-mono text-sm text-slate-700">{{ activeCall.phone_number }}</p>
          <p class="mt-4 rounded-md bg-slate-950 px-3 py-2 text-center font-mono text-3xl font-semibold text-white">{{ activeCallDuration }}</p>
        </article>
        <p v-else class="rounded-md border border-dashed border-blue-300 bg-white/70 px-4 py-12 text-center font-semibold text-blue-900">
          Aucun appel actif.
        </p>
      </div>
    </div>

    <div class="rounded-md border border-slate-200 bg-white shadow-sm">
      <div class="border-b border-slate-200 px-4 py-3">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Stage 3</p>
        <h2 class="text-xl font-semibold">Appeles</h2>
      </div>
      <div v-if="completedContacts.length" class="grid gap-3 p-3">
        <article v-for="contact in completedContacts" :key="contact.id" class="rounded-md border border-slate-200 bg-slate-50 p-3">
          <p class="break-words font-semibold">{{ contact.name || 'Sans nom' }}</p>
          <p class="mt-1 font-mono text-sm text-slate-700">{{ contact.phone_number }}</p>
          <p class="mt-2 text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
            Dernier appel: {{ formatDateTime(contact.last_called_at) }}
          </p>
        </article>
      </div>
      <p v-else class="px-4 py-8 text-center font-semibold text-slate-500">Rien de traite dans cette session.</p>
    </div>
  </section>
</template>
