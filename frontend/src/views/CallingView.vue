<script setup>
defineProps({
  activeCall: { type: Object, default: null },
  activeCallDuration: { type: String, required: true },
  callForm: { type: Object, required: true },
  completedContacts: { type: Array, required: true },
  countdownLabel: { type: String, required: true },
  currentProspect: { type: Object, default: null },
  formatDateTime: { type: Function, required: true },
  isRunning: { type: Boolean, required: true },
  pendingContacts: { type: Array, required: true },
  sessionConfig: { type: Object, required: true },
  sessionStarted: { type: Boolean, required: true },
  timeoutAlert: { type: Boolean, required: true },
  timerBarClass: { type: String, required: true },
  timerPanelClass: { type: String, required: true },
  timerProgress: { type: Number, required: true },
  timerTone: { type: String, required: true },
})

function timerMessage(tone) {
  const messages = {
    calm: 'Calme. Prepare le contexte du prochain prospect.',
    warning: 'Deux minutes. Le prochain appel doit se preparer.',
    'strong-warning': 'Une minute. Passe en mode execution.',
    urgent: 'Trente secondes. Appelle maintenant.',
    danger: 'Dernieres secondes. Plus de debat.',
  }

  return messages[tone] || messages.calm
}

defineEmits(['dismiss-alert', 'finish-call', 'open-setup', 'pause', 'reset', 'start', 'start-prospect-call'])
</script>

<template>
  <section class="grid min-h-[calc(100vh-8.5rem)] grid-rows-[auto_1fr] gap-4">
    <div v-if="timeoutAlert" class="border-2 border-red-500 bg-red-50 px-5 py-4 text-red-950 shadow-sm">
      <p class="text-sm font-semibold uppercase tracking-[0.16em]">Cadence ratee</p>
      <h2 class="mt-1 text-3xl font-bold">Il fallait appeler maintenant.</h2>
      <p class="mt-2 text-sm font-medium">Le timer est arrive a zero. Relance une cadence ou appelle le prospect courant.</p>
      <button type="button" class="mt-4 min-h-10 rounded-md bg-red-700 px-4 font-semibold text-white hover:bg-red-800" @click="$emit('dismiss-alert')">
        J'ai compris
      </button>
    </div>

    <section class="p-5" :class="timerPanelClass">
      <div class="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-center">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.16em] opacity-70">Prochain appel dans</p>
          <p class="mt-2 font-mono text-7xl font-bold leading-none tabular-nums">{{ countdownLabel }}</p>
          <p class="mt-3 text-sm font-medium opacity-80">
            {{ sessionStarted ? `${sessionConfig.callTarget} appels vises - toutes les ${sessionConfig.cadenceMinutes} min` : 'Configure une session pour lancer la cadence.' }}
          </p>
          <p class="mt-2 text-sm font-semibold">
            {{ timerMessage(timerTone) }}
          </p>
        </div>
        <div class="grid gap-2 sm:grid-cols-3 lg:min-w-80 lg:grid-cols-1">
          <button type="button" class="min-h-11 rounded-md bg-slate-950 px-4 font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300" :disabled="isRunning || !sessionStarted" @click="$emit('start')">
            Demarrer
          </button>
          <button type="button" class="min-h-11 rounded-md border border-current/20 bg-white/60 px-4 font-semibold hover:bg-white disabled:cursor-not-allowed disabled:text-slate-400" :disabled="!isRunning" @click="$emit('pause')">
            Pause
          </button>
          <button type="button" class="min-h-11 rounded-md border border-current/20 bg-white/60 px-4 font-semibold hover:bg-white" @click="$emit('open-setup')">
            Configurer
          </button>
        </div>
      </div>
      <div class="mt-5 h-3 overflow-hidden rounded-full bg-white/60">
        <div class="h-full rounded-full transition-all duration-500" :class="timerBarClass" :style="{ width: `${timerProgress}%` }" />
      </div>
    </section>

    <section class="grid min-h-0 gap-0 bg-white xl:grid-cols-[minmax(0,1fr)_420px]">
      <article class="min-h-[28rem]">
        <div class="border-b border-slate-200 px-4 py-3">
          <p class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">
            {{ activeCall ? 'Appel en cours' : 'Prospect courant' }}
          </p>
          <h2 class="text-2xl font-bold">{{ (activeCall || currentProspect)?.name || 'Aucun prospect pret' }}</h2>
        </div>
        <div v-if="activeCall || currentProspect" class="grid gap-5 p-5">
          <p class="font-mono text-lg font-semibold text-slate-700">{{ (activeCall || currentProspect).phone_number }}</p>
          <p class="whitespace-pre-wrap break-words text-sm font-medium leading-6 text-slate-600">{{ (activeCall || currentProspect).notes || 'Pas encore de contexte renseigne.' }}</p>
          <button v-if="!activeCall" type="button" class="min-h-12 rounded-md bg-blue-700 px-4 font-semibold text-white hover:bg-blue-800" @click="$emit('start-prospect-call', currentProspect)">
            Appeler ce prospect
          </button>
          <div v-else class="grid gap-4 border-t border-slate-200 pt-5">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">Temps d'appel</p>
                <p class="mt-1 font-mono text-4xl font-bold tabular-nums text-slate-950">{{ activeCallDuration }}</p>
              </div>
              <span class="rounded bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-800">Live</span>
            </div>

            <label class="grid gap-1.5 text-sm font-semibold text-slate-700">
              Resultat
              <select v-model="callForm.outcome" class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600">
                <option value="answered">Termine</option>
                <option value="no_answer">Pas de reponse</option>
                <option value="voicemail">Repondeur</option>
                <option value="failed">Echec</option>
              </select>
            </label>

            <label class="grid gap-1.5 text-sm font-semibold text-slate-700">
              Notes pendant l'appel
              <textarea v-model="callForm.notes" maxlength="2000" rows="8" class="resize-none rounded-md border border-slate-300 bg-white px-3 py-2 outline-none focus:border-blue-600" placeholder="Objections, signaux, prochaine action..." />
            </label>

            <div class="grid gap-2 sm:grid-cols-2">
              <button type="button" class="min-h-11 rounded-md bg-blue-700 px-4 font-semibold text-white hover:bg-blue-800" @click="$emit('finish-call')">
                Terminer
              </button>
              <button type="button" class="min-h-11 rounded-md border border-slate-300 px-4 font-semibold hover:bg-slate-50" @click="$emit('finish-call', 'no_answer')">
                Pas de reponse
              </button>
            </div>
          </div>
        </div>
        <p v-else class="px-4 py-10 text-center font-semibold text-slate-500">Ajoute des prospects avant de lancer une session.</p>
      </article>

      <aside class="border-t border-slate-200 bg-slate-50 xl:border-l xl:border-t-0">
        <div class="border-b border-slate-200 px-4 py-3">
          <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Session</p>
          <h2 class="text-xl font-bold">{{ sessionConfig.goal || 'Aucun objectif' }}</h2>
        </div>
        <div class="grid gap-3 p-4 text-sm font-medium text-slate-600">
          <p>Restants: <span class="font-mono font-semibold text-slate-950">{{ pendingContacts.length }}</span></p>
          <p>Traites: <span class="font-mono font-semibold text-slate-950">{{ completedContacts.length }}</span></p>
          <p v-if="activeCall">Appel actif: <span class="font-mono font-semibold text-slate-950">{{ activeCallDuration }}</span></p>
          <p v-if="currentProspect">Dernier appel prospect: {{ formatDateTime(currentProspect.last_called_at) }}</p>
        </div>
      </aside>
    </section>
  </section>
</template>
