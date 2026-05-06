<script setup>
defineProps({
  isVoiceReady: { type: Boolean, required: true },
  missingVoiceConfig: { type: Array, required: true },
  voiceConfig: { type: Object, default: null },
})

defineEmits(['check-voice'])
</script>

<template>
  <section class="min-h-[calc(100vh-8.5rem)] bg-white">
    <div class="flex items-start justify-between gap-3 border-b border-slate-200 px-5 py-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Settings</p>
        <h2 class="text-xl font-semibold">Twilio Voice</h2>
      </div>
      <button type="button" class="min-h-9 rounded-md border border-slate-300 px-3 text-sm font-semibold hover:bg-slate-50" @click="$emit('check-voice')">
        Verifier
      </button>
    </div>

    <div class="grid gap-5 p-5 lg:max-w-3xl">
      <div class="rounded-md border px-3 py-2 text-sm font-bold" :class="isVoiceReady ? 'border-emerald-200 bg-emerald-50 text-emerald-950' : 'border-amber-200 bg-amber-50 text-amber-950'">
        {{ isVoiceReady ? 'Voice pret pour appeler.' : 'Configuration Voice incomplete.' }}
      </div>

      <div class="grid gap-2 text-sm font-semibold text-slate-600">
        <p v-if="voiceConfig?.phone_number">
          Numero sortant: <span class="font-mono text-slate-950">{{ voiceConfig.phone_number }}</span>
        </p>
        <p v-if="missingVoiceConfig.length">
          Manque: <span class="font-mono text-slate-950">{{ missingVoiceConfig.join(', ') }}</span>
        </p>
      </div>
    </div>
  </section>
</template>
