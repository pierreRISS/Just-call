const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
let authToken = window.localStorage.getItem('just-call-token')

export function setAuthToken(token: string | null) {
  authToken = token
  if (token) {
    window.localStorage.setItem('just-call-token', token)
  } else {
    window.localStorage.removeItem('just-call-token')
  }
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 8000)

  const response = await fetch(`${apiUrl}${path}`, {
    ...options,
    signal: options.signal ?? controller.signal,
    headers: {
      'Content-Type': 'application/json',
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...(options.headers || {}),
    },
  }).finally(() => window.clearTimeout(timeout))

  if (!response.ok) {
    let message = 'The workspace could not sync.'
    try {
      const payload = await response.json()
      if (typeof payload.detail === 'string') {
        message = payload.detail
      } else if (Array.isArray(payload.detail)) {
        message = payload.detail
          .map((issue: { msg?: string; loc?: Array<string | number> }) => {
            const field = issue.loc?.slice(1).join('.')
            return field ? `${field}: ${issue.msg || 'Invalid value'}` : issue.msg || 'Invalid value'
          })
          .join(' · ')
      }
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }

  if (response.status === 204) return null as T
  return response.json() as Promise<T>
}

export function login(payload: BackendLoginRequest) {
  return apiRequest<BackendAuthSession>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getSession() {
  return apiRequest<BackendUser>('/auth/session')
}

export function logout() {
  return apiRequest<null>('/auth/logout', {
    method: 'POST',
  })
}

export function getProspects() {
  return apiRequest<BackendProspect[]>('/prospects')
}

export function createProspect(payload: BackendProspectCreate) {
  return apiRequest<BackendProspect>('/prospects', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateProspect(prospectId: number, payload: BackendProspectUpdate) {
  return apiRequest<BackendProspect>(`/prospects/${prospectId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getCalls() {
  return apiRequest<BackendCall[]>('/calls')
}

export function createCall(payload: BackendCallCreate) {
  return apiRequest<BackendCall>('/calls', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateCall(callId: number, payload: BackendCallUpdate) {
  return apiRequest<BackendCall>(`/calls/${callId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getReplaySessions() {
  return apiRequest<BackendReplaySession[]>('/replay-sessions')
}

export function createReplaySession(payload: BackendReplaySessionCreate) {
  return apiRequest<BackendReplaySession>('/replay-sessions', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getSettings() {
  return apiRequest<BackendSettings>('/settings')
}

export function updateSettings(payload: BackendSettingsUpdate) {
  return apiRequest<BackendSettings>('/settings', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export type BackendProspect = {
  id: number
  name: string
  company: string
  role: string | null
  phone_number: string
  email: string | null
  status: string
  priority: 'High' | 'Medium' | 'Low'
  temperature: 'Warm' | 'Neutral' | 'Cold'
  context: string | null
  previous_notes: string | null
  call_objective: string | null
  possible_objections: string[]
  priority_signals: string[]
  last_touch: string | null
  last_call: string | null
  last_called_at: string | null
  created_at: string
  updated_at: string
}

export type BackendUser = {
  id: number
  email: string
  display_name: string
  role: string | null
  created_at: string
}

export type BackendLoginRequest = {
  email: string
  password: string
}

export type BackendAuthSession = {
  token: string
  user: BackendUser
}

export type BackendProspectUpdate = Partial<BackendProspectCreate>

export type BackendProspectCreate = {
  name: string
  company: string
  role?: string | null
  phone_number: string
  email?: string | null
  status?: BackendProspect['status']
  priority?: BackendProspect['priority']
  temperature?: BackendProspect['temperature']
  context?: string | null
  previous_notes?: string | null
  call_objective?: string | null
  possible_objections?: string[]
  priority_signals?: string[]
  last_touch?: string | null
  last_call?: string | null
}

export type BackendAiReview = {
  id: number
  user_id: number
  call_id: number
  global_score: number
  summary: string
  strengths: string[]
  improvement_focus: string
  created_at: string
}

export type BackendCall = {
  id: number
  user_id: number
  prospect_id: number | null
  prospect_name: string
  company: string | null
  phone_number: string
  status: 'planned' | 'in_progress' | 'completed' | 'failed'
  quick_action: string | null
  duration_seconds: number
  notes: string | null
  transcript: string | null
  ai_summary: string | null
  global_score: number | null
  tags: string[]
  twilio_sid: string | null
  recording_url: string | null
  started_at: string | null
  ended_at: string | null
  created_at: string
  ai_review: BackendAiReview | null
}

export type BackendCallCreate = {
  prospect_id?: number | null
  prospect_name?: string | null
  company?: string | null
  phone_number?: string | null
  status?: BackendCall['status']
  quick_action?: string | null
  duration_seconds?: number
  notes?: string | null
  transcript?: string | null
  ai_summary?: string | null
  global_score?: number | null
  tags?: string[]
  started_at?: string | null
  ended_at?: string | null
}

export type BackendCallUpdate = Partial<Omit<BackendCallCreate, 'prospect_id' | 'prospect_name' | 'company' | 'phone_number'>>

export type BackendReplayMessage = {
  speaker: 'ai' | 'seller'
  text: string
}

export type BackendReplaySession = {
  id: number
  user_id: number
  call_id: number | null
  prospect_id: number | null
  difficulty: string
  objection_type: string
  prospect_behavior: string
  simulation_mode: string
  status: string
  messages: BackendReplayMessage[]
  created_at: string
}

export type BackendReplaySessionCreate = {
  call_id?: number | null
  prospect_id?: number | null
  difficulty?: string
  objection_type?: string
  prospect_behavior?: string
  simulation_mode?: string
  status?: string
  messages?: BackendReplayMessage[]
}

export type BackendSettings = {
  audio_input: string
  noise_cleanup: string
  microphone_permission: string
  notifications: Record<string, boolean>
  ai_preferences: Record<string, string>
  integrations: Record<string, string>
  status_options: string[]
}

export type BackendSettingsUpdate = Partial<BackendSettings>
