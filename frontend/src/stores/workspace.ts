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
import { aiReview as fallbackAiReview, callRecords as fallbackCalls, metrics, prospects as fallbackProspects } from '../mockData'
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

const fallbackSettings: WorkspaceSettings = {
  audioInput: 'Studio microphone',
  noiseCleanup: 'Soft',
  microphonePermission: 'granted',
  notifications: {
    post_call_review: true,
    follow_up_reminders: true,
    quiet_mode: true,
  },
  aiPreferences: {
    feedback_tone: 'Encouraging',
    replay_difficulty: 'Balanced',
    coaching_style: 'Concise',
  },
  integrations: {
    crm: 'prepared',
    calendar: 'connected',
    email: 'ready',
  },
  statusOptions: ['New', 'Contacted', 'Engaged', 'Advancing', 'Scheduled', 'Converted', 'Archived'],
}

const fallbackUser: WorkspaceUser = {
  id: 0,
  email: 'pierre@just-call.local',
  displayName: 'Pierre Caller',
  role: 'Senior account executive',
  initials: 'PC',
}

const performanceScorecard: Metric[] = [
  { id: 'control', label: 'Lead control', score: 86, delta: '+8%' },
  { id: 'listening', label: 'Listening quality', score: 91, delta: '+4%' },
  { id: 'confidence', label: 'Confidence', score: 78, delta: '+11%' },
  { id: 'objections', label: 'Objection handling', score: 83, delta: '+6%' },
  { id: 'closing', label: 'Closing clarity', score: 74, delta: '+3%' },
]

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
    role: payload.role || 'Sales contact',
    phone: payload.phone_number,
    email: payload.email || '',
    status: payload.status,
    priority: payload.priority,
    temperature: payload.temperature,
    context: payload.context || 'No context captured yet.',
    previousNotes: payload.previous_notes || 'No previous notes yet.',
    callObjective: payload.call_objective || 'Understand the current sales motion and qualify a useful next step.',
    possibleObjections: payload.possible_objections.length ? payload.possible_objections : ['No urgency', 'Budget timing'],
    prioritySignals: payload.priority_signals.length ? payload.priority_signals : ['New prospect'],
    lastTouch: payload.last_touch || 'No previous touch',
    lastCall: payload.last_call || (payload.last_called_at ? formatDate(payload.last_called_at) : 'No call yet'),
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
    : buildPerformanceMetrics(payload.global_score)

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

function averageMetricScore(metricList: Metric[]): number {
  if (!metricList.length) return 0
  return clampScore(metricList.reduce((total, metric) => total + metric.score, 0) / metricList.length)
}

function buildPerformanceMetrics(score: number, sourceScore?: number | null): Metric[] {
  if (sourceScore == null) return performanceScorecard.map((metric) => ({ ...metric }))

  const lift = Math.max(1, Math.round((score - sourceScore) / 3))
  return performanceScorecard.map((metric, index) => ({
    ...metric,
    score: clampScore(metric.score + lift + (index === 2 ? 2 : 0)),
    delta: `+${Number(metric.delta.replace(/[+%]/g, '')) + lift}%`,
  }))
}

function buildAiReviewFromCall(call: CallRecord): AiReview {
  return {
    score: call.score,
    metrics: call.metrics,
    summary: call.summary,
    strengths: [
      'You kept the conversation structured around the prospect context.',
      'You gave the objection enough room before moving back to value.',
    ],
    improvementFocus: 'Make the next step clearer earlier, then confirm it with a short confident close.',
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
  const score = rawScore != null ? clampScore(rawScore) : averageMetricScore(performanceScorecard)
  const callMetrics = payload.ai_review?.metrics?.length
    ? payload.ai_review.metrics.map((metric) => ({
        id: metric.id,
        label: metric.label,
        score: clampScore(metric.score),
        delta: metric.delta || '+0%',
        comment: metric.comment,
      }))
    : buildPerformanceMetrics(score)

  return {
    id: payload.id,
    prospectId: payload.prospect_id ?? 0,
    sourceCallId,
    prospectName: payload.prospect_name,
    company: payload.company || 'Unknown company',
    date: formatDate(payload.started_at || payload.created_at),
    duration: formatDuration(payload.duration_seconds),
    score,
    metrics: callMetrics,
    summary: payload.ai_summary || payload.ai_review?.summary || 'No AI summary yet.',
    transcriptPreview: payload.transcript || payload.notes || 'No transcript captured yet.',
    tags: payload.tags,
  }
}

function attachReplayComparisons(calls: CallRecord[]): CallRecord[] {
  const byId = new Map(calls.map((call) => [call.id, call]))

  return calls.map((call) => {
    const sourceCall = call.sourceCallId ? byId.get(call.sourceCallId) : null
    if (!sourceCall) return call
    const metrics = buildPerformanceMetrics(call.score, sourceCall.score)
    return {
      ...call,
      metrics,
      score: averageMetricScore(metrics),
    }
  })
}

function isDemoReadyProspect(prospect: Prospect): boolean {
  return prospect.name.trim().includes(' ') && prospect.company.trim().length > 2
}

function isDemoReadyCall(call: CallRecord): boolean {
  return call.prospectName.trim().includes(' ') && call.company.trim().length > 2
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
  const statusOptions = payload.status_options?.length
    ? payload.status_options
    : ['New', 'Contacted', 'Engaged', 'Advancing', 'Scheduled', 'Converted', 'Archived']

  return {
    audioInput: payload.audio_input,
    noiseCleanup: payload.noise_cleanup,
    microphonePermission: payload.microphone_permission,
    notifications: payload.notifications,
    aiPreferences: payload.ai_preferences,
    integrations: payload.integrations,
    statusOptions,
  }
}

export const useWorkspaceStore = defineStore('workspace', () => {
  const activePage = ref<PageId>('home')
  const sidebarCollapsed = ref(false)
  const isLoading = ref(false)
  const isAuthReady = ref(false)
  const isAuthenticated = ref(false)
  const currentUser = ref<WorkspaceUser>(fallbackUser)
  const prospects = ref<Prospect[]>([...fallbackProspects])
  const callRecords = ref<CallRecord[]>([...fallbackCalls])
  const replaySessions = ref<ReplaySession[]>([])
  const settings = ref<WorkspaceSettings>(fallbackSettings)
  const selectedProspectId = ref(prospects.value[0]?.id ?? 0)
  const selectedCallId = ref(callRecords.value[0]?.id ?? 0)
  const selectedReplaySessionId = ref<number | null>(null)
  const callStage = ref<CallStage>('prep')
  const selectedQuickAction = ref('Interested')
  const activeBrowserCallId = ref<number | null>(null)
  const activeCallStartedAt = ref<string | null>(null)
  const callNotes = ref(
    'Opening: mention current hiring wave.\n\nDiscovery:\n- Ask how managers review outbound calls today\n- Clarify ramp bottleneck\n\nNext step: propose a 20 minute workflow review.',
  )
  const aiReview = ref<AiReview>(fallbackAiReview)
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
    if (replace) {
      window.history.replaceState({ page }, '', nextHash)
    } else {
      window.history.pushState({ page }, '', nextHash)
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
    window.addEventListener('hashchange', () => {
      applyPage(parsePageFromLocation())
    })
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

      const mappedProspects = prospectsPayload.map(mapProspect).filter(isDemoReadyProspect)
      const mappedCalls = attachReplayComparisons(callsPayload.map(mapCall).filter(isDemoReadyCall))

      prospects.value = mappedProspects.length
        ? mappedProspects.sort((first, second) => second.id - first.id)
        : [...fallbackProspects]
      callRecords.value = mappedCalls.length ? mappedCalls : [...fallbackCalls]
      replaySessions.value = replayPayload.map(mapReplaySession)
      settings.value = mapSettings(settingsPayload)

      selectedProspectId.value = prospects.value[0]?.id ?? 0
      selectedCallId.value = callRecords.value[0]?.id ?? 0
      selectedReplaySessionId.value = replaySessions.value[0]?.id ?? null
      aiReview.value = mapAiReview(callsPayload.find((call) => call.ai_review)?.ai_review ?? null) ?? fallbackAiReview
    } catch (error) {
      pushToast(error instanceof Error ? error.message : 'Backend unavailable. Using local sample data.', 'error')
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
    currentUser.value = fallbackUser
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
        company: payload.company.trim() || 'Unknown company',
        role: payload.role.trim() || null,
        phone_number: payload.phone.trim(),
        email: payload.email.trim() || null,
        status: settings.value.statusOptions[0] || 'New',
        priority: 'Medium',
        temperature: 'Neutral',
        context: payload.context.trim() || null,
        previous_notes: 'No previous notes yet.',
        call_objective: 'Understand the current sales motion and qualify a useful next step.',
        possible_objections: ['No urgency', 'Budget timing', 'Tool overlap'],
        priority_signals: ['New prospect'],
        last_touch: 'Added manually',
        last_call: 'No call yet',
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
        company: next.company || 'Unknown company',
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
    callNotes.value = `Opening: use ${prospect.company} context.\n\nObjective:\n- ${prospect.callObjective}\n\nWatch for:\n- ${prospect.possibleObjections.join('\n- ')}`
    pushToast(`${prospect.name} prepared.`, 'info')
  }

  function beginLiveCall() {
    callStage.value = 'live'
    activeCallStartedAt.value = new Date().toISOString()
    pushToast('Live call started.', 'info')
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
      aiReview.value = mapAiReview(saved.ai_review) ?? buildAiReviewFromCall(mapped)
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

  function buildTranscriptDataFromNotes(notes: string) {
    return notes
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((text) => ({ speaker: 'caller' as const, text }))
  }

  async function finishLiveCall(durationSeconds = 0) {
    const prospect = selectedProspect.value
    if (!prospect) return
    const currentCall = selectedCall.value
    const isReplayCall = Boolean(currentCall?.sourceCallId)

    if (isReplayCall && currentCall) {
      const completedReplay = {
        ...currentCall,
        duration: formatDuration(durationSeconds),
        summary: 'Replay completed. You practiced the same conversation with stronger control and clearer closing.',
        transcriptPreview: callNotes.value.trim() || 'Voice-only AI replay completed. Transcript will be attached when voice capture is connected.',
        tags: currentCall.tags.includes('Completed replay') ? currentCall.tags : ['Completed replay', ...currentCall.tags],
      }

      callRecords.value = attachReplayComparisons(callRecords.value.map((call) => (call.id === currentCall.id ? completedReplay : call)))
      aiReview.value = buildAiReviewFromCall(completedReplay)
      callStage.value = 'review'

      try {
        const saved = await updateCall(currentCall.id, {
          status: 'completed',
          duration_seconds: durationSeconds,
          transcript: completedReplay.transcriptPreview,
          transcript_data: buildTranscriptDataFromNotes(completedReplay.transcriptPreview),
          notes: callNotes.value.trim() || null,
          ai_summary: completedReplay.summary,
          global_score: completedReplay.score,
          tags: completedReplay.tags,
          ended_at: new Date().toISOString(),
        })
        const mapped = attachReplayComparisons([mapCall(saved), ...callRecords.value.filter((call) => call.id !== currentCall.id)])[0]
        callRecords.value = attachReplayComparisons(callRecords.value.map((call) => (call.id === currentCall.id ? mapped : call)))
        aiReview.value = buildAiReviewFromCall(mapped)
      } catch {
        pushToast('Replay saved locally with mocked AI scores.', 'info')
      }
      pushToast('Replay completed. AI scorecard is ready.')
      return
    }

    try {
      const callMetrics = buildPerformanceMetrics(averageMetricScore(performanceScorecard))
      const callScore = averageMetricScore(callMetrics)
      const created = await createCall({
        prospect_id: prospect.id,
        status: 'completed',
        quick_action: selectedQuickAction.value,
        duration_seconds: durationSeconds,
        notes: callNotes.value.trim() || null,
        transcript: callNotes.value.trim() || null,
        transcript_data: buildTranscriptDataFromNotes(callNotes.value),
        ai_summary: 'Call completed. AI scorecard is ready with five coaching criteria.',
        global_score: callScore,
        tags: [selectedQuickAction.value],
        started_at: activeCallStartedAt.value,
        ended_at: new Date().toISOString(),
      })
      const call = mapCall(created)
      callRecords.value = attachReplayComparisons([call, ...callRecords.value])
      selectedCallId.value = call.id
      aiReview.value = mapAiReview(created.ai_review) ?? buildAiReviewFromCall(call)
      callStage.value = 'review'
      pushToast('Call saved. AI review fields are ready.')
    } catch (error) {
      pushToast(error instanceof Error ? error.message : 'Call could not be saved.', 'error')
    }
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
      const replayMetrics = buildPerformanceMetrics(clampScore(sourceCall.score + 9), sourceCall.score)
      const replayScore = averageMetricScore(replayMetrics)
      const replayCreated = await createCall({
        prospect_id: sourceCall.prospectId || null,
        prospect_name: sourceCall.prospectName,
        company: sourceCall.company,
        status: 'in_progress',
        quick_action: 'AI Replay',
        duration_seconds: 0,
        notes: `AI replay simulation created from call #${sourceCall.id}.`,
        transcript: 'Voice-only AI replay. Transcript will be attached after the simulated call.',
        ai_summary: 'AI replay simulation started from the original call so the seller can practice without repeating the same mistakes.',
        global_score: replayScore,
        tags: ['AI replay', `source_call_id:${sourceCall.id}`, ...(sourceCall.tags.length ? [sourceCall.tags[0]] : [])],
        started_at: new Date().toISOString(),
      })
      const replayCallRecord = mapCall(replayCreated)
      callRecords.value = attachReplayComparisons([replayCallRecord, ...callRecords.value])
      selectedCallId.value = replayCallRecord.id

      const created = await createReplaySession({
        call_id: sourceCall.id,
        prospect_id: sourceCall.prospectId || null,
        difficulty: 'Balanced',
        objection_type: sourceCall.tags[0] || 'Tool fatigue',
        prospect_behavior: 'Skeptical but fair',
        simulation_mode: 'Text replay',
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
      const localReplay: CallRecord = {
        ...sourceCall,
        id: Date.now(),
        sourceCallId: sourceCall.id,
        date: 'Just now',
        duration: '00:00',
        score: averageMetricScore(buildPerformanceMetrics(clampScore(sourceCall.score + 9), sourceCall.score)),
        metrics: buildPerformanceMetrics(clampScore(sourceCall.score + 9), sourceCall.score),
        summary: 'Local mock replay started from the original call.',
        transcriptPreview: 'Text AI replay. Transcript will be attached after the simulated call.',
        tags: ['AI replay', `source_call_id:${sourceCall.id}`],
      }
      const localSession: ReplaySession = {
        id: Date.now() + 1,
        callId: sourceCall.id,
        prospectId: sourceCall.prospectId || null,
        difficulty: 'Balanced',
        objectionType: sourceCall.tags[0] || 'Tool fatigue',
        prospectBehavior: 'Skeptical but fair',
        simulationMode: 'Text replay',
        messages: [],
      }
      callRecords.value = attachReplayComparisons([localReplay, ...callRecords.value])
      replaySessions.value = [localSession, ...replaySessions.value]
      selectedCallId.value = localReplay.id
      selectedReplaySessionId.value = localSession.id
      callStage.value = 'live'
      setPage('replay')
      callNotes.value = ''
      pushToast('AI simulation started locally. You speak first.', 'info')
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
      summary: 'Replay completed. The new scorecard compares this practice run with the original call.',
      transcriptPreview: transcript,
      tags: currentCall.tags.includes('Completed replay') ? currentCall.tags : ['Completed replay', ...currentCall.tags],
    }

    callRecords.value = attachReplayComparisons(callRecords.value.map((call) => (call.id === currentCall.id ? completedReplay : call)))
    aiReview.value = buildAiReviewFromCall(completedReplay)
    callStage.value = 'review'

    try {
      const saved = await updateCall(currentCall.id, {
        status: 'completed',
        duration_seconds: durationSeconds,
        transcript,
        transcript_data: buildTranscriptDataFromNotes(transcript),
        notes: transcript,
        ai_summary: completedReplay.summary,
        global_score: completedReplay.score,
        tags: completedReplay.tags,
        ended_at: new Date().toISOString(),
      })
      const mapped = attachReplayComparisons([mapCall(saved), ...callRecords.value.filter((call) => call.id !== currentCall.id)])[0]
      callRecords.value = attachReplayComparisons(callRecords.value.map((call) => (call.id === currentCall.id ? mapped : call)))
      aiReview.value = buildAiReviewFromCall(mapped)
    } catch {
      pushToast('Replay review generated locally.', 'info')
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
    aiReview,
    callNotes,
    callRecords,
    callStage,
    currentUser,
    isAuthReady,
    isAuthenticated,
    isLoading,
    metrics,
    pageTitle,
    prospects,
    replayMessages,
    replaySessions,
    selectedCall,
    selectedProspect,
    selectedReplaySession,
    selectedQuickAction,
    settings,
    sidebarCollapsed,
    toasts,
    addProspect,
    addStatusOption,
    archiveProspect,
    beginLiveCall,
    beginBrowserCall,
    completeBrowserCall,
    dismissToast,
    beginReplaySimulation,
    finishLiveCall,
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
    setPage,
    signIn,
    signOut,
    startCall,
    toggleSidebar,
  }
})
