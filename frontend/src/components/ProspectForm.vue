<script setup>
defineProps({
  contactForm: { type: Object, required: true },
})

defineEmits(['add-contact'])
</script>

<template>
  <form class="rounded-md border border-slate-200 bg-white p-4 shadow-sm" @submit.prevent="$emit('add-contact')">
    <h2 class="text-xl font-semibold">Nouveau prospect</h2>
    <div class="mt-4 grid gap-3">
      <input v-model="contactForm.name" maxlength="120" type="text" class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600" placeholder="Entreprise ou contact" />
      <input v-model="contactForm.phone_number" maxlength="40" type="tel" required class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600" placeholder="+33 6 12 34 56 78" />
      <textarea v-model="contactForm.notes" maxlength="2000" rows="3" class="resize-none rounded-md border border-slate-300 bg-white px-3 py-2 outline-none focus:border-blue-600" placeholder="Contexte rapide" />
      <button type="submit" class="min-h-11 rounded-md bg-blue-700 px-4 font-semibold text-white hover:bg-blue-800">Ajouter au pipeline</button>
    </div>
  </form>
</template>
