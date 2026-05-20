import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  createCall,
  createProspect,
  createReplaySession,
  getCalls,
  getProspects,
  getReplaySessions,
  getSession,
  getSettings,
  login,
  logout,
  sendReplayMessage,
  setAuthToken,
  updateCall,
  updateProspect,
  updateSettings,
  type BackendAiReview,
  type BackendCall,
  type BackendProspect,
  type BackendReplaySession,
  type BackendSettings,
  type BackendUser,
} from '../api/client'
import type {
  AiReview,
  CallRecord,
  CallStage,
  Metric,
  PageId,
  Prospect,
  ReplayMessage,
  ReplaySession,
  Toast,
  WorkspaceSettings,
  WorkspaceUser,
} from '../types'

const pageTitles: Record<PageId, string> = {
  home: 'Home',
  prospects: 'Prospects',
  call: 'Call workspace',
  history: 'Calls',
  replay: 'Jouer IA',
  analytics: 'Analytics',
  profile: 'Profile',
  settings: 'Settings',
}

const pageIds: PageId[] = ['home', 'prospects', 'call', 'history', 'replay', 'analytics', 'profile', 'settings']

const emptySettings: WorkspaceSettings = {
  audioInput: '',
  noiseCleanup: '',
  microphonePermission: '',
  notifications: {},
  aiPreferences: {},
  integrations: {},
  statusOptions: [],
}

const signedOutUser: WorkspaceUser = {
  id: 0,
  email: '',
  displayName: 'Just Call User',
  role: 'Sales operator',
  initials: 'JC',
}

function formatDate(value: string | null): string {
  if (!value) return 'No date'

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

function mapProspect(payload: BackendProspect): Prospect {
  return {
    id: payload.id,
    name: payload.name,
    company: payload.company,
    role: payload.role || '',
    phone: payload.phone_number,
    email: payload.email || '',
    status: payload.status,
    priority: payload.priority,
    temperature: payload.temperature,
    context: payload.context || '',
    previousNotes: payload.previous_notes || '',
    callObjective: payload.call_objective || '',
    possibleObjections: payload.possible_objections,
    prioritySignals: payload.priority_signals,
    lastTouch: payload.last_touch || '',
    lastCall: payload.last_call || (payload.last_called_at ? formatDate(payload.last_called_at) : ''),
  }
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('') || 'JC'
}

function mapUser(payload: BackendUser): WorkspaceUser {
  return {
    id: payload.id,
    email: payload.email,
    displayName: payload.display_name,
    role: payload.role || 'Sales operator',
    initials: getInitials(payload.display_name),
  }
}

function mapAiReview(payload: BackendAiReview | null): AiReview | null {
  if (!payload) return null
  const reviewMetrics = payload.metrics?.length
    ? payload.metrics.map((metric) => ({
        id: metric.id,
        label: metric.label,
        score: clampScore(metric.score),
        delta: metric.delta || '+0%',
        comment: metric.comment,
      }))
    : []

  return {
    score: clampScore(payload.global_score),
    metrics: reviewMetrics,
    summary: payload.summary,
    strengths: payload.strengths,
    improvementFocus: payload.improvement_focus,
  }
}

function clampScore(score: number): number {
  return Math.max(0, Math.min(100, Math.round(score)))
}

function buildAiReviewFromCall(call: CallRecord): AiReview {
  return {
    score: call.score,
    metrics: call.metrics,
    summary: call.summary,
    strengths: call.strengths,
    improvementFocus: call.improvementFocus,
  }
}

function parseSourceCallId(tags: string[]): number | null {
  const sourceTag = tags.find((tag) => tag.startsWith('source_call_id:'))
  if (!sourceTag) return null

  const sourceCallId = Number(sourceTag.replace('source_call_id:', ''))
  return Number.isFinite(sourceCallId) ? sourceCallId : null
}

function mapCall(payload: BackendCall): CallRecord {
  const sourceCallId = parseSourceCallId(payload.tags)
  const rawScore = payload.global_score ?? payload.ai_review?.global_score ?? null
  const score = rawScore != null ? clampScore(rawScore) : 0
  const review = mapAiReview(payload.ai_review)
  const callMetrics = payload.ai_review?.metrics?.length
    ? payload.ai_review.metrics.map((metric) => ({
        id: metric.id,
        label: metric.label,
        score: clampScore(metric.score),
        delta: metric.delta || '+0%',
        comment: metric.comment,
      }))
    : []
  const hasFallbackReview = payload.tags.some((tag) => tag.startsWith('Fallback review:'))

  return {
    id: payload.id,
    prospectId: payload.prospect_id ?? 0,
    sourceCallId,
    status: payload.status,
    reviewSource: hasFallbackReview ? 'fallback' : payload.ai_review ? 'ai' : 'pending',
    prospectName: payload.prospect_name,
    company: payload.company || '',
    date: formatDate(payload.started_at || payload.created_at),
    duration: formatDuration(payload.duration_seconds),
    score,
    metrics: callMetrics,
    summary: payload.ai_summary || payload.ai_review?.summary || '',
    strengths: review?.strengths ?? [],
    improvementFocus: review?.improvementFocus ?? '',
    transcriptPreview: payload.transcript || payload.notes || '',
    tags: payload.tags,
  }
}

function attachReplayComparisons(calls: CallRecord[]): CallRecord[] {
  return calls
}

function mapReplaySession(payload: BackendReplaySession): ReplaySession {
  return {
    id: payload.id,
    callId: payload.call_id,
    prospectId: payload.prospect_id,
    difficulty: payload.difficulty,
    objectionType: payload.objection_type,
    prospectBehavior: payload.prospect_behavior,
    simulationMode: payload.simulation_mode,
    messages: payload.messages.map((message, index) => ({ id: index + 1, ...message })),
  }
}

function mapSettings(payload: BackendSettings): WorkspaceSettings {
  return {
    audioInput: payload.audio_input,
    noiseCleanup: payload.noise_cleanup,
    microphonePermission: payload.microphone_permission,
    notifications: payload.notifications,
    aiPreferences: payload.ai_preferences,
    integrations: payload.integrations,
    statusOptions: payload.status_options,
  }
}

export const useWorkspaceStore = defineStore('workspace', () => {
  const activePage = ref<PageId>('home')
  const sidebarCollapsed = ref(false)
  const isLoading = ref(false)
  const isAuthReady = ref(false)
  const isAuthenticated = ref(false)
  const currentUser = ref<WorkspaceUser>(signedOutUser)
  const prospects = ref<Prospect[]>([])
  const callRecords = ref<CallRecord[]>([])
  const replaySessions = ref<ReplaySession[]>([])
  const settings = ref<WorkspaceSettings>(emptySettings)
  const selectedProspectId = ref(prospects.value[0]?.id ?? 0)
  const selectedCallId = ref(callRecords.value[0]?.id ?? 0)
  const selectedReplaySessionId = ref<number | null>(null)
  const callStage = ref<CallStage>('prep')
  const selectedQuickAction = ref('Interested')
  const activeBrowserCallId = ref<number | null>(null)
  const activeCallStartedAt = ref<string | null>(null)
  const callNotes = ref('')
  const toasts = ref<Toast[]>([])
  let toastId = 0
  let isNavigationReady = false

  const pageTitle = computed(() => pageTitles[activePage.value])
  const selectedProspect = computed(
    () => prospects.value.find((prospect) => prospect.id === selectedProspectId.value) ?? prospects.value[0],
  )
  const selectedCall = computed(
    () => callRecords.value.find((call) => call.id === selectedCallId.value) ?? callRecords.value[0],
  )
  const selectedAiReview = computed<AiReview | null>(() => (selectedCall.value ? buildAiReviewFromCall(selectedCall.value) : null))
  const realCallRecords = computed(() => callRecords.value.filter((call) => !call.sourceCallId && call.status === 'completed'))
  const performanceMetrics = computed<Metric[]>(() => {
    const metricMap = new Map<string, { label: string; total: number; count: number }>()
    realCallRecords.value.forEach((call) => {
      call.metrics.forEach((metric) => {
        const current = metricMap.get(metric.id) ?? { label: metric.label, total: 0, count: 0 }
        current.total += metric.score
        current.count += 1
        metricMap.set(metric.id, current)
      })
    })
    return Array.from(metricMap.entries()).map(([id, aggregate]) => {
      return {
        id,
        label: aggregate.label,
        score: clampScore(aggregate.total / aggregate.count),
        delta: '+0%',
      }
    })
  })
  const selectedReplaySession = computed(
    () => replaySessions.value.find((session) => session.id === selectedReplaySessionId.value) ?? null,
  )
  const replayMessages = computed<ReplayMessage[]>(() => selectedReplaySession.value?.messages ?? [])

  function parsePageFromLocation(): PageId {
    const hashPage = window.location.hash.replace(/^#\/?/, '').split('?')[0]
    return pageIds.includes(hashPage as PageId) ? (hashPage as PageId) : 'home'
  }

  function writePageToHistory(page: PageId, replace = false) {
    const nextHash = `#/${page}`
    if (window.location.hash === nextHash) return
    const nextUrl = `${window.location.pathname}${window.location.search}${nextHash}`
    if (replace) {
      window.history.replaceState({ page }, '', nextUrl)
    } else {
      window.history.pushState({ page }, '', nextUrl)
    }
  }

  function applyPage(page: PageId) {
    if (page === 'replay' && activePage.value !== 'replay') {
      const currentCall = selectedCall.value
      const sourceCall = currentCall?.sourceCallId
        ? callRecords.value.find((call) => call.id === currentCall.sourceCallId)
        : currentCall
      const firstOriginalCall = callRecords.value.find((call) => !call.sourceCallId)

      if (sourceCall || firstOriginalCall) selectedCallId.value = (sourceCall ?? firstOriginalCall)?.id ?? selectedCallId.value
      selectedReplaySessionId.value = null
      callStage.value = 'prep'
      callNotes.value = ''
    }
    activePage.value = page
  }

  function setPage(page: PageId, options: { replace?: boolean; syncHistory?: boolean } = {}) {
    applyPage(page)
    if (options.syncHistory !== false) writePageToHistory(page, options.replace)
  }

  function initializeNavigation() {
    if (isNavigationReady) return
    isNavigationReady = true
    setPage(parsePageFromLocation(), { replace: true })
    const syncPageFromBrowser = () => {
      applyPage(parsePageFromLocation())
    }
    window.addEventListener('hashchange', syncPageFromBrowser)
    window.addEventListener('popstate', syncPageFromBrowser)
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function selectProspect(prospect: Prospect) {
    selectedProspectId.value = prospect.id
  }

  async function loadWorkspace() {
    isLoading.value = true
    try {
      const [prospectsPayload, callsPayload, replayPayload, settingsPayload] = await Promise.all([
        getProspects(),
        getCalls(),
        getReplaySessions(),
        getSettings(),
      ])

      const mappedProspects = prospectsPayload.map(mapProspect)
      const mappedCalls = attachReplayComparisons(callsPayload.map(mapCall))

      prospects.value = mappedProspects.sort((first, second) => second.id - first.id)
      callRecords.value = mappedCalls
      replaySessions.value = replayPayload.map(mapReplaySession)
      settings.value = mapSettings(settingsPayload)

      selectedProspectId.value = prospects.value[0]?.id ?? 0
      selectedCallId.value = callRecords.value[0]?.id ?? 0
      selectedReplaySessionId.value = replaySessions.value[0]?.id ?? null
    } catch (error) {
      prospects.value = []
      callRecords.value = []
      replaySessions.value = []
      selectedProspectId.value = 0
      selectedCallId.value = 0
      selectedReplaySessionId.value = null
      pushToast(error instanceof Error ? error.message : 'Backend unavailable.', 'error')
    } finally {
      isLoading.value = false
    }
  }

  async function restoreSession() {
    if (!window.localStorage.getItem('just-call-token')) {
      isAuthenticated.value = false
      isAuthReady.value = true
      return
    }

    try {
      currentUser.value = mapUser(await getSession())
      isAuthenticated.value = true
      await loadWorkspace()
    } catch {
      setAuthToken(null)
      isAuthenticated.value = false
    } finally {
      isAuthReady.value = true
    }
  }

  async function signIn(email: string, password: string): Promise<boolean> {
    try {
      const session = await login({ email, password })
      setAuthToken(session.token)
      currentUser.value = mapUser(session.user)
      isAuthenticated.value = true
      await loadWorkspace()
      pushToast(`Welcome back, ${currentUser.value.displayName}.`, 'success')
      return true
    } catch (error) {
      pushToast(error instanceof Error ? error.message : 'Could not sign in.', 'error')
      return false
    } finally {
      isAuthReady.value = true
    }
  }

  async function signOut() {
    try {
      await logout()
    } catch {
      // Local logout still clears the client session.
    }
    setAuthToken(null)
    isAuthenticated.value = false
    currentUser.value = signedOutUser
    prospects.value = []
    callRecords.value = []
    replaySessions.value = []
  }

  async function addProspect(payload: {
    name: string
    company: string
    role: string
    phone: string
    email: string
    context: string
  }): Promise<boolean> {
    try {
      const created = await createProspect({
        name: payload.name.trim(),
        company: payload.company.trim(),
        role: payload.role.trim() || null,
        phone_number: payload.phone.trim(),
        email: payload.email.trim() || null,
        context: payload.context.trim() || null,
      })
      const prospect = mapProspect(created)
      prospects.value = [prospect, ...prospects.value]
      selectedProspectId.value = prospect.id
      pushToast(`${prospect.name} added to prospects.`)
      return true
    } catch (error) {
      pushToast(error instanceof Error ? error.message : 'Prospect could not be created.', 'error')
      return false
    }
  }

  async function saveProspect(prospectId: number, updates: Partial<Prospect>): Promise<boolean> {
    const existing = prospects.value.find((prospect) => prospect.id === prospectId)
    if (!existing) return false

    const previous = { ...existing }
    const next = { ...existing, ...updates }
    prospects.value = prospects.value.map((prospect) => (prospect.id === prospectId ? next : prospect))

    try {
      const saved = await updateProspect(prospectId, {
        name: next.name,
        company: next.company,
        role: next.role || null,
        phone_number: next.phone,
        email: next.email || null,
        status: next.status,
        priority: next.priority,
        temperature: next.temperature,
        context: next.context,
        previous_notes: next.previousNotes,
        call_objective: next.callObjective,
        possible_objections: next.possibleObjections,
        priority_signals: next.prioritySignals,
        last_touch: next.lastTouch,
        last_call: next.lastCall,
      })
      const mapped = mapProspect(saved)
      prospects.value = prospects.value.map((prospect) => (prospect.id === prospectId ? mapped : prospect))
      selectedProspectId.value = mapped.id
      pushToast('Prospect updated.')
      return true
    } catch (error) {
      prospects.value = prospects.value.map((prospect) => (prospect.id === prospectId ? previous : prospect))
      pushToast(error instanceof Error ? error.message : 'Prospect could not be updated.', 'error')
      return false
    }
  }

  function archiveProspect(prospect: Prospect) {
    return saveProspect(prospect.id, { status: 'Archived' })
  }

  async function addStatusOption(label: string): Promise<boolean> {
    const status = label.trim()
    if (!status || settings.value.statusOptions.includes(status)) return false

    const previous = [...settings.value.statusOptions]
    const next = [...previous, status]
    settings.value = { ...settings.value, statusOptions: next }

    try {
      const saved = await updateSettings({ status_options: next })
      settings.value = mapSettings(saved)
      pushToast(`${status} added to statuses.`)
      return true
    } catch (error) {
      settings.value = { ...settings.value, statusOptions: previous }
      pushToast(error instanceof Error ? error.message : 'Status could not be saved.', 'error')
      return false
    }
  }

  function selectCall(call: CallRecord) {
    selectedCallId.value = call.id
    if (call.prospectId) selectedProspectId.value = call.prospectId
  }

  function pushToast(message: string, type: Toast['type'] = 'success') {
    const toast = { id: ++toastId, message, type }
    toasts.value = [...toasts.value, toast]
    window.setTimeout(() => dismissToast(toast.id), type === 'error' ? 6000 : 4200)
  }

  function dismissToast(id: number) {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  function startCall() {
    callStage.value = 'prep'
    setPage('call')
    pushToast('Call workspace prepared.')
  }

  function prepareProspectCall(prospect: Prospect) {
    selectProspect(prospect)
    callStage.value = 'prep'
    setPage('call')
    const noteSections = [
      prospect.context ? `Context:\n${prospect.context}` : '',
      prospect.callObjective ? `Objective:\n- ${prospect.callObjective}` : '',
      prospect.possibleObjections.length ? `Watch for:\n- ${prospect.possibleObjections.join('\n- ')}` : '',
    ].filter(Boolean)
    callNotes.value = noteSections.join('\n\n')
    pushToast(`${prospect.name} prepared.`, 'info')
  }

  async function beginBrowserCall(recordConsent: boolean): Promise<CallRecord | null> {
    const prospect = selectedProspect.value
    if (!prospect) return null

    activeCallStartedAt.value = new Date().toISOString()
    try {
      const created = await createCall({
        prospect_id: prospect.id,
        status: 'in_progress',
        quick_action: selectedQuickAction.value,
        duration_seconds: 0,
        notes: callNotes.value.trim() || null,
        transcript: null,
        transcript_data: [],
        tags: recordConsent ? ['Recording consent confirmed'] : ['No recording'],
        started_at: activeCallStartedAt.value,
      })
      const call = mapCall(created)
      callRecords.value = attachReplayComparisons([call, ...callRecords.value])
      selectedCallId.value = call.id
      activeBrowserCallId.value = call.id
      callStage.value = 'live'
      pushToast(recordConsent ? 'Call started with recording enabled.' : 'Call started without recording.', 'info')
      return call
    } catch (error) {
      pushToast(error instanceof Error ? error.message : 'Call could not be prepared.', 'error')
      return null
    }
  }

  async function failBrowserCall(callId: number) {
    try {
      const saved = await updateCall(callId, {
        status: 'failed',
        ended_at: new Date().toISOString(),
      })
      const mapped = mapCall(saved)
      callRecords.value = callRecords.value.map((call) => (call.id === mapped.id ? mapped : call))
      selectedCallId.value = mapped.id
      activeBrowserCallId.value = null
      callStage.value = 'review'
    } catch {
      // Twilio status webhooks may still reconcile this call.
    }
  }

  async function completeBrowserCall() {
    const callId = activeBrowserCallId.value
    activeBrowserCallId.value = null
    callStage.value = 'review'
    if (!callId) return

    window.setTimeout(async () => {
      try {
        await loadWorkspace()
        selectedCallId.value = callId
      } catch {
        // The webhook path remains the source of truth.
      }
    }, 3500)
  }

  async function saveActiveCallNotes(): Promise<boolean> {
    const callId = activeBrowserCallId.value ?? selectedCall.value?.id
    if (!callId) return false

    try {
      const saved = await updateCall(callId, {
        notes: callNotes.value.trim() || null,
      })
      const mapped = mapCall(saved)
      callRecords.value = callRecords.value.map((call) => (call.id === mapped.id ? mapped : call))
      pushToast('Notes saved to the call timeline.')
      return true
    } catch (error) {
      pushToast(error instanceof Error ? error.message : 'Notes could not be saved.', 'error')
      return false
    }
  }

  function buildTranscriptDataFromNotes(notes: string) {
    return notes
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((text) => ({ speaker: 'caller' as const, text }))
  }

  function prepareReplayCall(call: CallRecord) {
    selectCall(call)
    selectedReplaySessionId.value = null
    callStage.value = 'prep'
    setPage('replay')
    callNotes.value = ''
    pushToast(`${call.prospectName} selected for AI practice.`, 'info')
  }

  function replayCall(call: CallRecord) {
    prepareReplayCall(call.sourceCallId ? callRecords.value.find((item) => item.id === call.sourceCallId) ?? call : call)
  }

  async function beginReplaySimulation(call: CallRecord) {
    const sourceCall = call.sourceCallId ? callRecords.value.find((item) => item.id === call.sourceCallId) ?? call : call
    selectCall(sourceCall)

    try {
      const replayCreated = await createCall({
        prospect_id: sourceCall.prospectId || null,
        prospect_name: sourceCall.prospectName,
        company: sourceCall.company,
        status: 'in_progress',
        quick_action: 'AI Replay',
        duration_seconds: 0,
        notes: `AI replay simulation created from call #${sourceCall.id}.`,
        tags: ['AI replay', `source_call_id:${sourceCall.id}`, ...(sourceCall.tags.length ? [sourceCall.tags[0]] : [])],
        started_at: new Date().toISOString(),
      })
      const replayCallRecord = mapCall(replayCreated)
      callRecords.value = attachReplayComparisons([replayCallRecord, ...callRecords.value])
      selectedCallId.value = replayCallRecord.id

      const created = await createReplaySession({
        call_id: sourceCall.id,
        prospect_id: sourceCall.prospectId || null,
        messages: [],
      })
      const session = mapReplaySession(created)
      replaySessions.value = [session, ...replaySessions.value.filter((item) => item.id !== session.id)]
      selectedReplaySessionId.value = session.id
      callStage.value = 'live'
      setPage('replay')
      callNotes.value = ''
      pushToast('AI simulation started. You speak first.', 'info')
    } catch {
      pushToast('AI simulation could not be started.', 'error')
    }
  }

  async function finishReplaySimulation(durationSeconds = 0) {
    const currentCall = selectedCall.value
    if (!currentCall?.sourceCallId) return

    const session = selectedReplaySession.value
    const transcript = session?.messages.length
      ? session.messages.map((message) => `${message.speaker === 'seller' ? 'Seller' : 'AI'}: ${message.text}`).join('\n')
      : 'Simulation ended before any message was sent.'
    const completedReplay: CallRecord = {
      ...currentCall,
      duration: formatDuration(durationSeconds),
      transcriptPreview: transcript,
      tags: currentCall.tags.includes('Completed replay') ? currentCall.tags : ['Completed replay', ...currentCall.tags],
    }

    const previousCalls = [...callRecords.value]
    callRecords.value = attachReplayComparisons(callRecords.value.map((call) => (call.id === currentCall.id ? completedReplay : call)))
    callStage.value = 'review'

    try {
      const saved = await updateCall(currentCall.id, {
        status: 'completed',
        duration_seconds: durationSeconds,
        transcript,
        transcript_data: buildTranscriptDataFromNotes(transcript),
        notes: transcript,
        tags: completedReplay.tags,
        ended_at: new Date().toISOString(),
      })
      const mapped = attachReplayComparisons([mapCall(saved), ...callRecords.value.filter((call) => call.id !== currentCall.id)])[0]
      callRecords.value = attachReplayComparisons(callRecords.value.map((call) => (call.id === currentCall.id ? mapped : call)))
    } catch {
      callRecords.value = previousCalls
      pushToast('Replay could not be saved.', 'error')
      return
    }
    pushToast('Replay complete. Scorecard is ready.')
  }

  async function sendReplayText(text: string): Promise<boolean> {
    const session = selectedReplaySession.value
    const message = text.trim()
    if (!session || !message) return false

    const previousSession = { ...session, messages: [...session.messages] }
    const optimisticSession: ReplaySession = {
      ...session,
      messages: [...session.messages, { id: Date.now(), speaker: 'seller', text: message }],
    }
    replaySessions.value = replaySessions.value.map((item) => (item.id === session.id ? optimisticSession : item))

    try {
      const updated = mapReplaySession(await sendReplayMessage(session.id, message))
      replaySessions.value = replaySessions.value.map((item) => (item.id === updated.id ? updated : item))
      selectedReplaySessionId.value = updated.id
      return true
    } catch (error) {
      replaySessions.value = replaySessions.value.map((item) => (item.id === session.id ? previousSession : item))
      pushToast(error instanceof Error ? error.message : 'AI client could not answer.', 'error')
      return false
    }
  }

  return {
    activePage,
    activeBrowserCallId,
    callNotes,
    callRecords,
    callStage,
    currentUser,
    isAuthReady,
    isAuthenticated,
    isLoading,
    pageTitle,
    performanceMetrics,
    prospects,
    realCallRecords,
    replayMessages,
    replaySessions,
    selectedCall,
    selectedAiReview,
    selectedProspect,
    selectedReplaySession,
    selectedQuickAction,
    settings,
    sidebarCollapsed,
    toasts,
    addProspect,
    addStatusOption,
    archiveProspect,
    beginBrowserCall,
    completeBrowserCall,
    dismissToast,
    beginReplaySimulation,
    finishReplaySimulation,
    failBrowserCall,
    initializeNavigation,
    loadWorkspace,
    prepareReplayCall,
    prepareProspectCall,
    pushToast,
    replayCall,
    restoreSession,
    sendReplayText,
    selectCall,
    selectProspect,
    saveProspect,
    saveActiveCallNotes,
    setPage,
    signIn,
    signOut,
    startCall,
    toggleSidebar,
  }
})
