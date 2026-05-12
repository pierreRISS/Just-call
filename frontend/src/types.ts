export type PageId = 'home' | 'prospects' | 'call' | 'history' | 'replay' | 'analytics' | 'profile' | 'settings'

export type CallStage = 'prep' | 'live' | 'review'

export type Metric = {
  id: string
  label: string
  score: number
  delta: string
  comment?: string | null
}

export type Prospect = {
  id: number
  name: string
  company: string
  role: string
  phone: string
  email: string
  status: string
  priority: 'High' | 'Medium' | 'Low'
  temperature: 'Warm' | 'Neutral' | 'Cold'
  context: string
  previousNotes: string
  callObjective: string
  possibleObjections: string[]
  prioritySignals: string[]
  lastTouch: string
  lastCall: string
}

export type WorkspaceUser = {
  id: number
  email: string
  displayName: string
  role: string
  initials: string
}

export type CallRecord = {
  id: number
  prospectId: number
  sourceCallId: number | null
  prospectName: string
  company: string
  date: string
  duration: string
  score: number
  metrics: Metric[]
  summary: string
  transcriptPreview: string
  tags: string[]
}

export type ReplayMessage = {
  id: number
  speaker: 'ai' | 'seller'
  text: string
}

export type ReplaySession = {
  id: number
  callId: number | null
  prospectId: number | null
  difficulty: string
  objectionType: string
  prospectBehavior: string
  simulationMode: string
  messages: ReplayMessage[]
}

export type AiReview = {
  score: number
  metrics: Metric[]
  summary: string
  strengths: string[]
  improvementFocus: string
}

export type Toast = {
  id: number
  type: 'success' | 'info' | 'error'
  message: string
}

export type WorkspaceSettings = {
  audioInput: string
  noiseCleanup: string
  microphonePermission: string
  notifications: Record<string, boolean>
  aiPreferences: Record<string, string>
  integrations: Record<string, string>
  statusOptions: string[]
}
