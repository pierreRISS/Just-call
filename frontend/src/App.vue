<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const contacts = ref([])
const callLogs = ref([])
const meetings = ref([])
const completedContactIds = ref([])
const isLoading = ref(false)
const isClearingHistory = ref(false)
const isRunning = ref(false)
const remainingSeconds = ref(0)
const activeCall = ref(null)
const activeCallSeconds = ref(0)
const error = ref('')
const success = ref('')

const cadence = reactive({
  minMinutes: 10,
  maxMinutes: 15,
})

const contactForm = reactive({
  name: '',
  phone_number: '',
  notes: '',
})

const callForm = reactive({
  outcome: 'answered',
  notes: '',
  hasMeeting: false,
  meetingAt: '',
  meetingNotes: '',
})

let countdownTimer = null
let callTimer = null
let audioContext = null

const pendingContacts = computed(() =>
  contacts.value.filter((contact) => !completedContactIds.value.includes(contact.id)),
)

const totalCallsToday = computed(() => callLogs.value.length)
const totalMeetings = computed(() => meetings.value.length)
const conversionRate = computed(() => {
  if (!callLogs.value.length) return 0
  return Math.round((meetings.value.length / callLogs.value.length) * 100)
})

const countdownLabel = computed(() => formatDuration(remainingSeconds.value))
const activeCallDuration = computed(() => formatDuration(activeCallSeconds.value))

function clearCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

function clearCallTimer() {
  if (callTimer) {
    clearInterval(callTimer)
    callTimer = null
  }
}

function formatDuration(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

function formatDateTime(value) {
  if (!value) return 'Jamais'

  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function toDateTimeLocalValue(date) {
  const timezoneOffset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - timezoneOffset).toISOString().slice(0, 16)
}

function defaultMeetingDateTime() {
  const date = new Date()
  date.setDate(date.getDate() + 1)
  date.setMinutes(0, 0, 0)
  date.setHours(date.getHours() + 1)
  return toDateTimeLocalValue(date)
}

function normalizeCadence() {
  const min = Math.max(0.1, Number(cadence.minMinutes) || 0.1)
  const max = Math.max(min, Number(cadence.maxMinutes) || min)
  cadence.minMinutes = Number(min.toFixed(2))
  cadence.maxMinutes = Number(max.toFixed(2))
}

function maxDelaySeconds() {
  normalizeCadence()
  return Math.ceil(cadence.maxMinutes * 60)
}

function outcomeLabel(outcome) {
  const labels = {
    answered: 'Terminé',
    no_answer: 'Pas de réponse',
    voicemail: 'Répondeur',
    failed: 'Échec',
  }

  return labels[outcome] || outcome
}

function resetCallForm() {
  callForm.outcome = 'answered'
  callForm.notes = ''
  callForm.hasMeeting = false
  callForm.meetingAt = defaultMeetingDateTime()
  callForm.meetingNotes = ''
}

async function request(path, options = {}) {
  const response = await fetch(`${apiUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  if (!response.ok) {
    let message = 'Une erreur est survenue.'
    try {
      const payload = await response.json()
      message = payload.detail || message
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }

  if (response.status === 204) return null
  return response.json()
}

async function fetchData() {
  isLoading.value = true
  error.value = ''

  try {
    const [contactsPayload, callLogsPayload, meetingsPayload] = await Promise.all([
      request('/contacts'),
      request('/call-logs'),
      request('/meetings'),
    ])
    contacts.value = contactsPayload
    callLogs.value = callLogsPayload
    meetings.value = meetingsPayload
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    isLoading.value = false
  }
}

async function addContact() {
  const phoneNumber = contactForm.phone_number.trim()
  if (!phoneNumber) return

  error.value = ''
  success.value = ''

  try {
    const createdContact = await request('/contacts', {
      method: 'POST',
      body: JSON.stringify({
        name: contactForm.name.trim() || null,
        phone_number: phoneNumber,
        notes: contactForm.notes.trim() || null,
      }),
    })

    contacts.value = [...contacts.value, createdContact]
    contactForm.name = ''
    contactForm.phone_number = ''
    contactForm.notes = ''
    success.value = 'Contact ajouté.'
  } catch (requestError) {
    error.value = requestError.message
  }
}

async function removeContact(contactId) {
  error.value = ''
  success.value = ''

  try {
    await request(`/contacts/${contactId}`, {
      method: 'DELETE',
    })
    contacts.value = contacts.value.filter((contact) => contact.id !== contactId)
    completedContactIds.value = completedContactIds.value.filter((id) => id !== contactId)
  } catch (requestError) {
    error.value = requestError.message
  }
}

async function clearHistory() {
  if (!callLogs.value.length || isClearingHistory.value) return

  error.value = ''
  success.value = ''
  isClearingHistory.value = true

  try {
    await request('/call-logs', {
      method: 'DELETE',
    })
    callLogs.value = []
    meetings.value = meetings.value.map((meeting) => ({
      ...meeting,
      call_log_id: null,
    }))
    success.value = 'Historique supprimé.'
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    isClearingHistory.value = false
  }
}

function getNextContact() {
  return pendingContacts.value[0] || null
}

function unlockAudio() {
  const AudioContext = window.AudioContext || window.webkitAudioContext
  if (!AudioContext) return

  if (!audioContext) {
    audioContext = new AudioContext()
  }

  if (audioContext.state === 'suspended') {
    audioContext.resume()
  }
}

function playCallSound() {
  if (!audioContext) return

  const now = audioContext.currentTime
  ;[0, 0.22, 0.44].forEach((offset) => {
    const oscillator = audioContext.createOscillator()
    const gain = audioContext.createGain()

    oscillator.type = 'sine'
    oscillator.frequency.setValueAtTime(880, now + offset)
    gain.gain.setValueAtTime(0.0001, now + offset)
    gain.gain.exponentialRampToValueAtTime(0.18, now + offset + 0.02)
    gain.gain.exponentialRampToValueAtTime(0.0001, now + offset + 0.14)

    oscillator.connect(gain)
    gain.connect(audioContext.destination)
    oscillator.start(now + offset)
    oscillator.stop(now + offset + 0.16)
  })
}

function scheduleNextCall() {
  clearCountdown()

  const nextContact = getNextContact()
  if (!nextContact) {
    isRunning.value = false
    remainingSeconds.value = 0
    success.value = 'Session terminée.'
    return
  }

  remainingSeconds.value = maxDelaySeconds()
  countdownTimer = setInterval(() => {
    remainingSeconds.value -= 1

    if (remainingSeconds.value <= 0) {
      startSimulatedCall()
    }
  }, 1000)
}

function startSession() {
  if (!contacts.value.length) {
    error.value = 'Ajoute au moins un numéro avant de démarrer.'
    return
  }

  if (!pendingContacts.value.length) {
    completedContactIds.value = []
  }

  error.value = ''
  success.value = ''
  isRunning.value = true
  unlockAudio()
  scheduleNextCall()
}

function pauseSession() {
  clearCountdown()
  isRunning.value = false
}

function resetSession() {
  clearCountdown()
  clearCallTimer()
  isRunning.value = false
  remainingSeconds.value = 0
  activeCall.value = null
  activeCallSeconds.value = 0
  completedContactIds.value = []
  resetCallForm()
}

function startSimulatedCall() {
  clearCountdown()

  const nextContact = getNextContact()
  if (!nextContact) {
    scheduleNextCall()
    return
  }

  activeCall.value = nextContact
  activeCallSeconds.value = 0
  resetCallForm()
  playCallSound()

  callTimer = setInterval(() => {
    activeCallSeconds.value += 1
  }, 1000)
}

async function finishCall(outcome = callForm.outcome) {
  if (!activeCall.value) return

  error.value = ''
  success.value = ''
  const contact = activeCall.value

  if (callForm.hasMeeting && !callForm.meetingAt) {
    error.value = 'Choisis une date et une heure pour la réunion.'
    return
  }

  try {
    const createdLog = await request('/call-logs', {
      method: 'POST',
      body: JSON.stringify({
        contact_id: contact.id,
        outcome,
        duration_seconds: activeCallSeconds.value,
        notes: callForm.notes.trim() || null,
      }),
    })

    if (callForm.hasMeeting) {
      const createdMeeting = await request('/meetings', {
        method: 'POST',
        body: JSON.stringify({
          contact_id: contact.id,
          call_log_id: createdLog.id,
          scheduled_at: new Date(callForm.meetingAt).toISOString(),
          notes: callForm.meetingNotes.trim() || null,
        }),
      })

      meetings.value = [...meetings.value, createdMeeting].sort(
        (left, right) => new Date(left.scheduled_at) - new Date(right.scheduled_at),
      )
    }

    callLogs.value = [createdLog, ...callLogs.value]
    contacts.value = contacts.value.map((item) =>
      item.id === contact.id ? { ...item, last_called_at: createdLog.created_at } : item,
    )
    completedContactIds.value = [...completedContactIds.value, contact.id]
    activeCall.value = null
    activeCallSeconds.value = 0
    clearCallTimer()

    if (isRunning.value) {
      scheduleNextCall()
    }
  } catch (requestError) {
    error.value = requestError.message
  }
}

onMounted(() => {
  resetCallForm()
  fetchData()
})

onBeforeUnmount(() => {
  clearCountdown()
  clearCallTimer()
  if (audioContext) {
    audioContext.close()
  }
})
</script>

<template>
  <main class="min-h-screen bg-slate-50 px-4 py-5 text-slate-950 sm:px-6 lg:px-8">
    <div class="mx-auto grid w-full max-w-7xl gap-5">
      <header class="grid gap-4 border-b border-slate-300 pb-5 lg:grid-cols-[1fr_auto] lg:items-end">
        <div class="max-w-2xl">
          <p class="text-xs font-black uppercase tracking-[0.22em] text-blue-700">Just Call</p>
          <h1 class="mt-2 text-4xl font-black leading-none text-slate-950 sm:text-6xl">
            DashBoard
          </h1>
          <p class="mt-3 max-w-xl text-sm font-semibold leading-6 text-slate-600">
            Une cadence simple pour transformer une liste froide en conversations utiles.
          </p>
        </div>

        <div class="grid grid-cols-2 gap-2 text-left sm:w-auto sm:min-w-[36rem] sm:grid-cols-4">
          <div class="rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm">
            <p class="text-[0.68rem] font-black uppercase tracking-[0.16em] text-slate-500">Pipeline</p>
            <p class="mt-1 text-3xl font-black">{{ pendingContacts.length }}</p>
          </div>
          <div class="rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm">
            <p class="text-[0.68rem] font-black uppercase tracking-[0.16em] text-slate-600">Appels</p>
            <p class="mt-1 text-3xl font-black">{{ totalCallsToday }}</p>
          </div>
          <div class="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 shadow-sm">
            <p class="text-[0.68rem] font-black uppercase tracking-[0.16em] text-slate-700">Conversion</p>
            <p class="mt-1 text-3xl font-black">{{ conversionRate }}%</p>
          </div>
          <div class="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-white shadow-sm">
            <p class="text-[0.68rem] font-black uppercase tracking-[0.16em] text-slate-300">Timer</p>
            <p class="mt-1 text-3xl font-black tabular-nums">{{ countdownLabel }}</p>
          </div>
        </div>
      </header>

      <p v-if="error" class="rounded-md border border-red-200 bg-red-50 px-4 py-3 font-black text-red-900">
        {{ error }}
      </p>
      <p
        v-else-if="success"
        class="rounded-md border border-slate-200 bg-white px-4 py-3 font-black text-blue-900"
      >
        {{ success }}
      </p>

      <section class="grid gap-5 lg:grid-cols-[380px_1fr]">
        <aside class="grid content-start gap-5">
          <form class="rounded-md border border-slate-200 bg-white p-4 shadow-sm" @submit.prevent="addContact">
            <h2 class="text-xl font-black">Nouveau prospect</h2>

            <div class="mt-4 grid gap-3">
              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Nom
                <input
                  v-model="contactForm.name"
                  maxlength="120"
                  type="text"
                  class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600 focus:bg-white"
                  placeholder="Entreprise ou contact"
                />
              </label>

              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Numéro
                <input
                  v-model="contactForm.phone_number"
                  maxlength="40"
                  type="tel"
                  required
                  class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600 focus:bg-white"
                  placeholder="+33 6 12 34 56 78"
                />
              </label>

              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Notes
                <textarea
                  v-model="contactForm.notes"
                  maxlength="2000"
                  rows="3"
                  class="resize-none rounded-md border border-slate-300 bg-white px-3 py-2 outline-none focus:border-blue-600 focus:bg-white"
                  placeholder="Contexte rapide"
                />
              </label>

              <button type="submit" class="min-h-11 rounded-md bg-blue-700 px-4 font-black text-white hover:bg-blue-800">
                Ajouter
              </button>
            </div>
          </form>

          <section class="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <div class="flex items-center justify-between gap-3">
              <h2 class="text-xl font-black">Cadence</h2>
            </div>

            <div class="mt-4 grid grid-cols-2 gap-3">
              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Min. (minutes)
                <input
                  v-model.number="cadence.minMinutes"
                  min="0.1"
                  max="600"
                  step="0.1"
                  type="number"
                  class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600"
                />
              </label>

              <label class="grid gap-1.5 text-sm font-bold text-slate-700">
                Max. (minutes)
                <input
                  v-model.number="cadence.maxMinutes"
                  min="0.1"
                  max="600"
                  step="0.1"
                  type="number"
                  class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600"
                />
              </label>
            </div>

            <div class="mt-4 grid grid-cols-3 gap-2">
              <button
                type="button"
                class="min-h-11 rounded-md bg-slate-950 px-3 font-black text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-300"
                :disabled="isRunning || Boolean(activeCall)"
                @click="startSession"
              >
                Démarrer
              </button>
              <button
                type="button"
                class="min-h-11 rounded-md border border-slate-300 bg-white px-3 font-black hover:bg-white disabled:cursor-not-allowed disabled:text-slate-400"
                :disabled="!isRunning || Boolean(activeCall)"
                @click="pauseSession"
              >
                Pause
              </button>
              <button
                type="button"
                class="min-h-11 rounded-md border border-slate-300 bg-white px-3 font-black hover:bg-white"
                @click="resetSession"
              >
                Reset
              </button>
            </div>
          </section>
        </aside>

        <section class="grid content-start gap-5">
          <section class="rounded-md border border-slate-200 bg-white shadow-sm">
            <div class="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 class="text-xl font-black">File d'appels</h2>
              <span v-if="isLoading" class="text-sm font-black text-slate-700">Chargement...</span>
            </div>

            <div v-if="contacts.length" class="divide-y divide-slate-200">
              <article
                v-for="contact in contacts"
                :key="contact.id"
                class="grid gap-3 px-4 py-3 hover:bg-slate-50 sm:grid-cols-[1fr_auto] sm:items-center"
              >
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <h3 class="break-words font-black">
                      {{ contact.name || 'Sans nom' }}
                    </h3>
                    <span
                      v-if="completedContactIds.includes(contact.id)"
                      class="rounded-sm bg-slate-100 px-2 py-1 text-xs font-black uppercase tracking-[0.12em] text-blue-900"
                    >
                      Session faite
                    </span>
                  </div>
                  <p class="mt-1 font-mono text-sm text-slate-700">{{ contact.phone_number }}</p>
                  <p v-if="contact.notes" class="mt-1 break-words text-sm text-slate-500">
                    {{ contact.notes }}
                  </p>
                  <p class="mt-2 text-xs font-black uppercase tracking-[0.14em] text-slate-400">
                    Dernier appel: {{ formatDateTime(contact.last_called_at) }}
                  </p>
                </div>

                <button
                  type="button"
                  class="min-h-10 rounded-md border border-red-200 bg-white px-3 font-black text-red-700 hover:bg-red-50"
                  @click="removeContact(contact.id)"
                >
                  Retirer
                </button>
              </article>
            </div>

            <p v-else-if="!isLoading" class="px-4 py-8 text-center font-black text-slate-500">
              Aucun prospect.
            </p>
          </section>

          <section class="rounded-md border border-slate-200 bg-white shadow-sm">
            <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 class="text-xl font-black">Réunions</h2>
            </div>

            <div v-if="meetings.length" class="divide-y divide-slate-200">
              <article
                v-for="meeting in meetings"
                :key="meeting.id"
                class="grid gap-2 px-4 py-3 sm:grid-cols-[1fr_auto] sm:items-center"
              >
                <div class="min-w-0">
                  <p class="break-words font-black">{{ meeting.contact_name || 'Sans nom' }}</p>
                  <p class="font-mono text-sm text-slate-700">{{ meeting.phone_number }}</p>
                  <p v-if="meeting.notes" class="mt-1 break-words text-sm text-slate-500">
                    {{ meeting.notes }}
                  </p>
                </div>
                <p class="text-left text-sm font-black text-slate-700 sm:text-right">
                  {{ formatDateTime(meeting.scheduled_at) }}
                </p>
              </article>
            </div>

            <p v-else class="px-4 py-8 text-center font-black text-slate-500">
              Aucune réunion planifiée.
            </p>
          </section>

          <section class="rounded-md border border-slate-200 bg-white shadow-sm">
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 bg-slate-950 px-4 py-3 text-white">
              <h2 class="text-xl font-black">Historique</h2>
              <button
                type="button"
                class="min-h-9 rounded-md border border-slate-400 px-3 text-sm font-black text-white hover:bg-white hover:text-slate-950 disabled:cursor-not-allowed disabled:border-slate-600 disabled:text-slate-500"
                :disabled="!callLogs.length || isClearingHistory"
                @click="clearHistory"
              >
                Supprimer l'historique
              </button>
            </div>

            <div v-if="callLogs.length" class="divide-y divide-slate-200">
              <article
                v-for="log in callLogs"
                :key="log.id"
                class="grid gap-2 px-4 py-3 hover:bg-slate-50 sm:grid-cols-[1fr_auto] sm:items-center"
              >
                <div class="min-w-0">
                  <p class="break-words font-black">{{ log.contact_name || 'Sans nom' }}</p>
                  <p class="font-mono text-sm text-slate-700">{{ log.phone_number }}</p>
                  <p v-if="log.notes" class="mt-1 break-words text-sm text-slate-500">{{ log.notes }}</p>
                </div>
                <div class="text-left sm:text-right">
                  <p class="font-black text-slate-950">{{ outcomeLabel(log.outcome) }}</p>
                  <p class="text-sm font-bold text-slate-500">
                    {{ formatDuration(log.duration_seconds) }} - {{ formatDateTime(log.created_at) }}
                  </p>
                </div>
              </article>
            </div>

            <p v-else class="px-4 py-8 text-center font-black text-slate-500">
              Aucun appel enregistré.
            </p>
          </section>
        </section>
      </section>
    </div>

    <div
      v-if="activeCall"
      class="fixed inset-0 z-20 grid place-items-center bg-slate-950/80 px-4 py-6"
      role="dialog"
      aria-modal="true"
    >
      <section class="w-full max-w-md rounded-md border border-slate-200 bg-white p-5 shadow-2xl">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-bold uppercase tracking-normal text-blue-700">Appel simulé</p>
            <h2 class="mt-1 break-words text-2xl font-black">{{ activeCall.name || 'Sans nom' }}</h2>
            <p class="mt-1 font-mono text-lg text-slate-700">{{ activeCall.phone_number }}</p>
          </div>
          <p class="rounded-md bg-slate-950 px-3 py-2 font-mono text-lg font-black text-white">
            {{ activeCallDuration }}
          </p>
        </div>

        <div class="mt-5 grid gap-3">
          <label class="grid gap-1.5 text-sm font-bold text-slate-700">
            Résultat
            <select
              v-model="callForm.outcome"
              class="min-h-11 rounded-md border border-slate-300 bg-white px-3 outline-none focus:border-blue-600 focus:bg-white"
            >
              <option value="answered">Terminé</option>
              <option value="no_answer">Pas de réponse</option>
              <option value="voicemail">Répondeur</option>
              <option value="failed">Échec</option>
            </select>
          </label>

          <label class="grid gap-1.5 text-sm font-bold text-slate-700">
            Note d'appel
            <textarea
              v-model="callForm.notes"
              maxlength="2000"
              rows="3"
              class="resize-none rounded-md border border-slate-300 bg-white px-3 py-2 outline-none focus:border-blue-600 focus:bg-white"
              placeholder="Résultat, objection, prochaine action"
            />
          </label>
        </div>

        <div class="mt-5 grid gap-2 sm:grid-cols-2">
          <button
            type="button"
            class="min-h-11 rounded-md bg-blue-700 px-4 font-black text-white hover:bg-blue-800"
            @click="finishCall()"
          >
            Terminer l'appel
          </button>
          <button
            type="button"
            class="min-h-11 rounded-md border border-slate-300 bg-white px-4 font-black hover:bg-slate-50"
            @click="finishCall('no_answer')"
          >
            Pas de réponse
          </button>
        </div>
      </section>
    </div>
  </main>
</template>
