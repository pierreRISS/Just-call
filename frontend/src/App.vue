<script setup>
import { Device } from '@twilio/voice-sdk'
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import {
  apiRequest,
  clearCallLogs,
  createCallLog,
  createContact,
  deleteContact,
  updateContact,
} from './api/client'
import CallLogDrawer from './components/CallLogDrawer.vue'
import SessionSetupModal from './components/SessionSetupModal.vue'
import ToastStack from './components/ToastStack.vue'
import CallingView from './views/CallingView.vue'
import HistoryView from './views/HistoryView.vue'
import ProspectsView from './views/ProspectsView.vue'
import TwilioSettingsView from './views/TwilioSettingsView.vue'

const contacts = ref([])
const callLogs = ref([])
const completedContactIds = ref([])
const isClearingHistory = ref(false)
const isStartingDirectCall = ref(false)
const isDirectCallActive = ref(false)
const isRunning = ref(false)
const remainingSeconds = ref(0)
const countdownTotalSeconds = ref(0)
const activeCall = ref(null)
const activeCallSeconds = ref(0)
const selectedCallLog = ref(null)
const activeView = ref('prospects')
const selectedProspectId = ref(null)
const isAddProspectOpen = ref(false)
const isProspectDetailOpen = ref(false)
const showSessionSetup = ref(false)
const sessionStarted = ref(false)
const timeoutAlert = ref(false)
const error = ref('')
const success = ref('')
const toasts = ref([])
const microphoneStatus = ref('')
const voiceStatus = ref('')
const voiceConfig = ref(null)

const contactForm = reactive({
  name: '',
  phone_number: '',
  notes: '',
})

const prospectEditForm = reactive({
  id: null,
  name: '',
  phone_number: '',
  notes: '',
})

const directCallForm = reactive({
  phone_number: '',
})

const sessionForm = reactive({
  goal: '',
  callTarget: 10,
  cadenceMinutes: 3,
})

const sessionConfig = reactive({
  goal: '',
  callTarget: 0,
  cadenceMinutes: 3,
})

const callForm = reactive({
  outcome: 'answered',
  notes: '',
})

const dashboardViews = [
  { id: 'prospects', label: 'Prospects' },
  { id: 'calling', label: 'Calling' },
  { id: 'calls', label: 'Appels' },
  { id: 'settings', label: 'Settings' },
]

let countdownTimer = null
let callTimer = null
let audioContext = null
let voiceDevice = null
let voiceCall = null
let toastId = 0

const pendingContacts = computed(() =>
  contacts.value.filter((contact) => !completedContactIds.value.includes(contact.id)),
)

const totalCallsToday = computed(() => callLogs.value.length)
const conversionRate = computed(() => {
  if (!contacts.value.length) return 0
  return Math.round((callLogs.value.length / contacts.value.length) * 100)
})

const countdownLabel = computed(() => formatDuration(remainingSeconds.value))
const activeCallDuration = computed(() => formatDuration(activeCallSeconds.value))
const isVoiceReady = computed(() => Boolean(voiceConfig.value?.is_ready))
const missingVoiceConfig = computed(() => voiceConfig.value?.missing || [])
const completedContacts = computed(() =>
  contacts.value.filter((contact) => completedContactIds.value.includes(contact.id)),
)
const selectedProspect = computed(
  () => contacts.value.find((contact) => contact.id === selectedProspectId.value) || contacts.value[0] || null,
)
const currentProspect = computed(() => pendingContacts.value[0] || null)
const timerProgress = computed(() => {
  if (!countdownTotalSeconds.value) return 0
  return Math.max(0, Math.min(100, (remainingSeconds.value / countdownTotalSeconds.value) * 100))
})
const timerTone = computed(() => {
  if (!isRunning.value || activeCall.value || !remainingSeconds.value) return 'calm'
  if (remainingSeconds.value <= 5) return 'danger'
  if (remainingSeconds.value <= 30) return 'urgent'
  if (remainingSeconds.value <= 60) return 'strong-warning'
  if (remainingSeconds.value <= 120) return 'warning'
  return 'calm'
})
const timerPanelClass = computed(() => {
  if (timerTone.value === 'danger') return 'bg-red-50 text-red-950'
  if (timerTone.value === 'urgent') return 'bg-orange-50 text-orange-950'
  if (timerTone.value === 'strong-warning') return 'bg-amber-100 text-amber-950'
  if (timerTone.value === 'warning') return 'bg-yellow-50 text-yellow-950'
  return 'bg-white text-slate-950'
})
const timerBarClass = computed(() => {
  if (timerTone.value === 'danger') return 'bg-red-600'
  if (timerTone.value === 'urgent') return 'bg-orange-600'
  if (timerTone.value === 'strong-warning') return 'bg-amber-500'
  if (timerTone.value === 'warning') return 'bg-yellow-400'
  return 'bg-blue-600'
})
const shouldShakeInterface = computed(
  () => remainingSeconds.value > 0 && remainingSeconds.value <= 5 && isRunning.value && !activeCall.value,
)

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

function maxDelaySeconds() {
  const cadenceMinutes = Math.max(0.1, Number(sessionConfig.cadenceMinutes) || 0.1)
  return Math.ceil(cadenceMinutes * 60)
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
}

function dismissToast(id) {
  toasts.value = toasts.value.filter((toast) => toast.id !== id)
}

function pushToast(type, message) {
  const id = ++toastId
  toasts.value = [...toasts.value, { id, type, message }]
  window.setTimeout(() => dismissToast(id), type === 'error' ? 6500 : 4000)
}

watch(error, (message) => {
  if (message) pushToast('error', message)
})

watch(success, (message) => {
  if (message) pushToast('success', message)
})

async function fetchData() {
  error.value = ''

  try {
    const [contactsPayload, callLogsPayload] = await Promise.all([
      apiRequest('/contacts'),
      apiRequest('/call-logs'),
    ])
    contacts.value = contactsPayload
    callLogs.value = callLogsPayload
  } catch (requestError) {
    error.value = requestError.message
  }
}

async function fetchVoiceConfig() {
  try {
    voiceConfig.value = await apiRequest('/voice/config')
  } catch (requestError) {
    voiceConfig.value = null
    error.value = requestError.message
  }
}

async function addContact() {
  const phoneNumber = contactForm.phone_number.trim()
  if (!phoneNumber) return

  error.value = ''
  success.value = ''

  try {
    const createdContact = await createContact({
      name: contactForm.name.trim() || null,
      phone_number: phoneNumber,
      notes: contactForm.notes.trim() || null,
    })

    contacts.value = [...contacts.value, createdContact]
    contactForm.name = ''
    contactForm.phone_number = ''
    contactForm.notes = ''
    isAddProspectOpen.value = false
    success.value = 'Contact ajouté.'
  } catch (requestError) {
    error.value = requestError.message
  }
}

function openAddProspect() {
  isAddProspectOpen.value = true
  isProspectDetailOpen.value = false
}

function openProspectDetail(contactId) {
  const contact = contacts.value.find((item) => item.id === contactId)
  if (!contact) return

  selectedProspectId.value = contactId
  prospectEditForm.id = contact.id
  prospectEditForm.name = contact.name || ''
  prospectEditForm.phone_number = contact.phone_number
  prospectEditForm.notes = contact.notes || ''
  isProspectDetailOpen.value = true
  isAddProspectOpen.value = false
}

async function saveProspect() {
  if (!prospectEditForm.id) return

  error.value = ''
  success.value = ''

  try {
    const updatedContact = await updateContact(prospectEditForm.id, {
      name: prospectEditForm.name.trim() || null,
      phone_number: prospectEditForm.phone_number.trim(),
      notes: prospectEditForm.notes.trim() || null,
    })

    contacts.value = contacts.value.map((contact) =>
      contact.id === updatedContact.id ? updatedContact : contact,
    )
    success.value = 'Prospect mis à jour.'
  } catch (requestError) {
    error.value = requestError.message
  }
}

async function requestMicrophoneAccess() {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error("Ton navigateur ne permet pas l'accès au micro sur cette page.")
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach((track) => track.stop())
    microphoneStatus.value = 'Micro autorisé.'
  } catch {
    microphoneStatus.value = ''
    throw new Error("Autorise le micro pour lancer l'appel.")
  }
}

async function fetchVoiceToken() {
  return apiRequest('/voice/token')
}

async function refreshVoiceToken() {
  if (!voiceDevice) return

  const payload = await fetchVoiceToken()
  voiceDevice.updateToken(payload.token)
}

async function createVoiceDevice() {
  if (voiceDevice) return voiceDevice

  const payload = await fetchVoiceToken()
  voiceDevice = new Device(payload.token, {
    logLevel: 1,
  })

  voiceDevice.on('registered', () => {
    voiceStatus.value = 'Téléphone web prêt.'
  })
  voiceDevice.on('tokenWillExpire', refreshVoiceToken)
  voiceDevice.on('error', (deviceError) => {
    error.value = deviceError.message || 'Erreur Twilio Voice.'
    voiceStatus.value = ''
  })

  await voiceDevice.register()
  return voiceDevice
}

function bindVoiceCall(call, phoneNumber) {
  voiceCall = call
  isDirectCallActive.value = true
  voiceStatus.value = `Connexion vers ${phoneNumber}...`

  call.on('accept', () => {
    voiceStatus.value = `En appel avec ${phoneNumber}.`
  })
  call.on('disconnect', () => {
    voiceStatus.value = 'Appel terminé.'
    voiceCall = null
    isDirectCallActive.value = false
    isStartingDirectCall.value = false
  })
  call.on('cancel', () => {
    voiceStatus.value = 'Appel annulé.'
    voiceCall = null
    isDirectCallActive.value = false
    isStartingDirectCall.value = false
  })
  call.on('reject', () => {
    voiceStatus.value = 'Appel refusé.'
    voiceCall = null
    isDirectCallActive.value = false
    isStartingDirectCall.value = false
  })
  call.on('error', (callError) => {
    error.value = callError.message || "L'appel a échoué."
    voiceStatus.value = ''
    voiceCall = null
    isDirectCallActive.value = false
    isStartingDirectCall.value = false
  })
}

async function startDirectCall() {
  const phoneNumber = directCallForm.phone_number.trim()
  if (!phoneNumber || isStartingDirectCall.value) return false

  if (!isVoiceReady.value) {
    error.value = missingVoiceConfig.value.length
      ? `Configuration Twilio incomplète: ${missingVoiceConfig.value.join(', ')}.`
      : 'Configuration Twilio indisponible.'
    return false
  }

  error.value = ''
  success.value = ''
  microphoneStatus.value = ''
  isStartingDirectCall.value = true

  try {
    await requestMicrophoneAccess()
    const device = await createVoiceDevice()
    const call = await device.connect({
      params: {
        To: phoneNumber,
      },
    })

    bindVoiceCall(call, phoneNumber)
    success.value = ''
    return true
  } catch (requestError) {
    error.value = requestError.message
    isStartingDirectCall.value = false
    return false
  }
}

function hangUpDirectCall() {
  if (!voiceCall) return

  voiceCall.disconnect()
  voiceCall = null
  isDirectCallActive.value = false
  voiceStatus.value = 'Appel terminé.'
  isStartingDirectCall.value = false
}

function resetVoiceDevice() {
  if (voiceCall) {
    voiceCall.disconnect()
    voiceCall = null
  }
  isDirectCallActive.value = false

  if (voiceDevice) {
    voiceDevice.destroy()
    voiceDevice = null
  }

  isStartingDirectCall.value = false
  voiceStatus.value = ''
}

async function removeContact(contactId) {
  error.value = ''
  success.value = ''

  try {
    await deleteContact(contactId)
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
    await clearCallLogs()
    callLogs.value = []
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
  timeoutAlert.value = false

  const nextContact = getNextContact()
  if (!nextContact) {
    isRunning.value = false
    remainingSeconds.value = 0
    success.value = 'Session terminée.'
    return
  }

  countdownTotalSeconds.value = maxDelaySeconds()
  remainingSeconds.value = countdownTotalSeconds.value
  countdownTimer = setInterval(() => {
    remainingSeconds.value -= 1

    if (remainingSeconds.value <= 0) {
      clearCountdown()
      isRunning.value = false
      remainingSeconds.value = 0
      timeoutAlert.value = true
      error.value = 'Cadence ratée : appelle le prospect maintenant.'
      playCallSound()
    }
  }, 1000)
}

function startSession() {
  if (!contacts.value.length) {
    activeView.value = 'prospects'
    error.value = 'Ajoute au moins un prospect avant de démarrer Calling.'
    return
  }

  if (!sessionStarted.value) {
    showSessionSetup.value = true
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
  countdownTotalSeconds.value = 0
  activeCall.value = null
  activeCallSeconds.value = 0
  completedContactIds.value = []
  timeoutAlert.value = false
  sessionStarted.value = false
  resetCallForm()
}

function selectView(viewId) {
  activeView.value = viewId
  if (viewId === 'calling' && !sessionStarted.value) {
    showSessionSetup.value = true
  }
}

function startCallingSession() {
  if (!contacts.value.length) {
    showSessionSetup.value = false
    activeView.value = 'prospects'
    error.value = 'Ajoute au moins un prospect avant de lancer une session Calling.'
    return
  }

  sessionConfig.goal = sessionForm.goal.trim() || 'Session de prospection'
  sessionConfig.callTarget = Math.max(1, Number(sessionForm.callTarget) || 1)
  sessionConfig.cadenceMinutes = Math.max(0.1, Number(sessionForm.cadenceMinutes) || 0.1)
  sessionStarted.value = true
  showSessionSetup.value = false
  activeView.value = 'calling'
  startSession()
}

function dismissTimeoutAlert() {
  timeoutAlert.value = false
  error.value = ''
}

async function startCallForProspect(contact) {
  if (!contact) return
  directCallForm.phone_number = contact.phone_number
  const didStart = await startDirectCall()
  if (didStart) {
    startSimulatedCall()
  }
}

function openCallLog(log) {
  selectedCallLog.value = log
}

function closeCallLog() {
  selectedCallLog.value = null
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

  try {
    const createdLog = await createCallLog({
      contact_id: contact.id,
      outcome,
      duration_seconds: activeCallSeconds.value,
      notes: callForm.notes.trim() || null,
    })

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
  fetchVoiceConfig()
})

onBeforeUnmount(() => {
  clearCountdown()
  clearCallTimer()
  resetVoiceDevice()
  if (audioContext) {
    audioContext.close()
  }
})
</script>

<template>
  <main
    class="min-h-screen bg-slate-50 px-4 py-5 text-slate-950 sm:px-6 lg:px-8"
    :class="{ 'just-call-shake': shouldShakeInterface }"
  >
    <ToastStack :toasts="toasts" @dismiss="dismissToast" />

    <div class="grid min-h-[calc(100vh-2.5rem)] grid-rows-[auto_1fr] gap-4">
      <header class="sticky top-4 z-20 rounded-md border border-slate-200 bg-white/95 px-4 py-3 shadow-sm backdrop-blur">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-4">
            <div>
              <p class="text-lg font-bold leading-none text-slate-950">Just Call</p>
              <p class="mt-1 text-xs font-medium text-slate-500">
                {{ contacts.length }} prospects - {{ pendingContacts.length }} a appeler - {{ totalCallsToday }} appels
              </p>
            </div>
            <nav class="flex overflow-x-auto rounded-md bg-slate-100 p-1">
              <button
                v-for="view in dashboardViews"
                :key="view.id"
                type="button"
                class="min-h-9 whitespace-nowrap rounded px-3 text-sm font-semibold text-slate-600 transition hover:bg-white hover:text-slate-950"
                :class="activeView === view.id ? 'bg-white text-slate-950 shadow-sm' : ''"
                @click="selectView(view.id)"
              >
                {{ view.label }}
              </button>
            </nav>
          </div>
          <div class="text-right text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Progression {{ conversionRate }}%
          </div>
        </div>
      </header>

      <section class="min-h-0">
        <div class="grid min-h-full content-start gap-5">
          <ProspectsView
            v-if="activeView === 'prospects'"
            :contact-form="contactForm"
            :contacts="contacts"
            :edit-form="prospectEditForm"
            :format-date-time="formatDateTime"
            :is-add-open="isAddProspectOpen"
            :is-detail-open="isProspectDetailOpen"
            :selected-prospect="selectedProspect"
            @add-contact="addContact"
            @close-add="isAddProspectOpen = false"
            @close-detail="isProspectDetailOpen = false"
            @open-add="openAddProspect"
            @remove-contact="removeContact"
            @save-prospect="saveProspect"
            @select-prospect="openProspectDetail"
          />

          <CallingView
            v-else-if="activeView === 'calling'"
            :active-call="activeCall"
            :active-call-duration="activeCallDuration"
            :call-form="callForm"
            :completed-contacts="completedContacts"
            :countdown-label="countdownLabel"
            :current-prospect="currentProspect"
            :format-date-time="formatDateTime"
            :is-running="isRunning"
            :pending-contacts="pendingContacts"
            :session-config="sessionConfig"
            :session-started="sessionStarted"
            :timeout-alert="timeoutAlert"
            :timer-bar-class="timerBarClass"
            :timer-panel-class="timerPanelClass"
            :timer-progress="timerProgress"
            :timer-tone="timerTone"
            @dismiss-alert="dismissTimeoutAlert"
            @finish-call="finishCall"
            @open-setup="showSessionSetup = true"
            @pause="pauseSession"
            @reset="resetSession"
            @start="startSession"
            @start-prospect-call="startCallForProspect"
          />

          <HistoryView
            v-else-if="activeView === 'calls'"
            :call-logs="callLogs"
            :format-date-time="formatDateTime"
            :format-duration="formatDuration"
            :is-clearing-history="isClearingHistory"
            :outcome-label="outcomeLabel"
            @clear-history="clearHistory"
            @open-log="openCallLog"
          />

          <section v-else-if="activeView === 'settings'" class="grid gap-5 lg:grid-cols-2">
            <TwilioSettingsView
              :is-voice-ready="isVoiceReady"
              :missing-voice-config="missingVoiceConfig"
              :voice-config="voiceConfig"
              @check-voice="fetchVoiceConfig"
            />
          </section>
        </div>
      </section>
    </div>

    <CallLogDrawer
      v-if="selectedCallLog"
      :format-date-time="formatDateTime"
      :format-duration="formatDuration"
      :log="selectedCallLog"
      :outcome-label="outcomeLabel"
      @close="closeCallLog"
    />

    <SessionSetupModal
      v-if="showSessionSetup"
      :form="sessionForm"
      :prospect-count="contacts.length"
      @close="showSessionSetup = false"
      @start="startCallingSession"
    />
  </main>
</template>
