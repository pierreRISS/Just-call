<script setup>
defineProps({
  directCallForm: { type: Object, required: true },
  isDirectCallActive: { type: Boolean, required: true },
  isStartingDirectCall: { type: Boolean, required: true },
  isVoiceReady: { type: Boolean, required: true },
  microphoneStatus: { type: String, default: '' },
  missingVoiceConfig: { type: Array, required: true },
  voiceConfig: { type: Object, default: null },
  voiceStatus: { type: String, default: '' },
})

defineEmits(['check-voice', 'hang-up', 'start-call'])
</script>

<template>
  <form class="rounded-md border border-slate-800 bg-slate-950 p-4 text-white shadow-sm" @submit.prevent="$emit('start-call')">
    <div class="flex items-start justify-between gap-3">
      <div>
        <h2 class="text-xl font-semibold">Appel direct</h2>
        <p class="mt-1 text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
          {{ isVoiceReady ? 'Voice pret' : 'Setup a finir' }}
        </p>
      </div>
      <button type="button" class="min-h-9 rounded-md border border-slate-700 px-3 text-sm font-semibold text-slate-100 hover:bg-slate-800" @click="$emit('check-voice')">
        Verifier
      </button>
    </div>

    <div v-if="voiceConfig && !isVoiceReady" class="mt-4 rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm font-bold text-amber-950">
      Manque: {{ missingVoiceConfig.join(', ') }}
    </div>

    <div class="mt-4 grid gap-3">
      <input
        v-model="directCallForm.phone_number"
        maxlength="40"
        type="tel"
        required
        class="min-h-11 rounded-md border border-slate-700 bg-white px-3 text-slate-950 outline-none focus:border-blue-400"
        placeholder="+33 6 12 34 56 78"
      />
      <button
        type="submit"
        class="min-h-11 rounded-md bg-blue-600 px-4 font-semibold text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-600"
        :disabled="isStartingDirectCall || !isVoiceReady"
      >
        {{ isStartingDirectCall ? 'Lancement...' : 'Appeler' }}
      </button>
      <button v-if="isDirectCallActive" type="button" class="min-h-11 rounded-md border border-red-300 px-4 font-semibold text-red-100 hover:bg-red-950" @click="$emit('hang-up')">
        Raccrocher
      </button>
      <p v-if="microphoneStatus" class="text-sm font-semibold text-blue-100">{{ microphoneStatus }}</p>
      <p v-if="voiceStatus" class="text-sm font-semibold text-slate-200">{{ voiceStatus }}</p>
    </div>
  </form>
</template>
