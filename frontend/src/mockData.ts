import type { AiReview, CallRecord, Metric, Prospect, ReplayMessage } from './types'

export const metrics: Metric[] = [
  { id: 'control', label: 'Lead control', score: 86, delta: '+8%' },
  { id: 'listening', label: 'Listening quality', score: 91, delta: '+4%' },
  { id: 'confidence', label: 'Confidence', score: 78, delta: '+11%' },
  { id: 'objections', label: 'Objection handling', score: 83, delta: '+6%' },
  { id: 'closing', label: 'Closing clarity', score: 74, delta: '+3%' },
]

export const prospects: Prospect[] = [
  {
    id: 1,
    name: 'Camille Laurent',
    company: 'Nestra',
    role: 'VP Revenue',
    phone: '+33 6 42 19 80 14',
    email: 'camille@nestra.co',
    status: 'Advancing',
    priority: 'High',
    temperature: 'Warm',
    context:
      'Nestra is hiring 18 account executives this quarter. Camille cares about ramp speed, clean process, and coaching without adding manager overhead.',
    prioritySignals: ['Hiring sales team', 'Recent Series A', 'Outbound motion'],
    previousNotes:
      'Camille reacted well to manager leverage. She asked for proof that reps would not need extra admin.',
    callObjective: 'Confirm pilot criteria and secure a workflow review with her sales managers.',
    possibleObjections: ['Adoption risk', 'Manager time', 'Existing call recording tools'],
    lastTouch: 'LinkedIn reply, 2 days ago',
    lastCall: 'Today',
  },
  {
    id: 2,
    name: 'Arthur Besson',
    company: 'AltoPay',
    role: 'Head of Sales',
    phone: '+33 7 61 45 12 70',
    email: 'arthur@altopay.io',
    status: 'Engaged',
    priority: 'Medium',
    temperature: 'Neutral',
    context:
      'AltoPay sells into mid-market finance teams. Arthur mentioned inconsistent discovery quality across new reps.',
    prioritySignals: ['Discovery gaps', 'Mid-market', 'Training budget'],
    previousNotes:
      'Arthur wants less variability between reps. He is comparing enablement tools this month.',
    callObjective: 'Understand current coaching cadence and identify one measurable pilot outcome.',
    possibleObjections: ['Budget timing', 'Tool overlap', 'Data privacy'],
    lastTouch: 'Email opened today',
    lastCall: 'Yesterday',
  },
  {
    id: 3,
    name: 'Maya Chen',
    company: 'HelioWorks',
    role: 'Founder',
    phone: '+33 6 88 02 33 91',
    email: 'maya@helioworks.com',
    status: 'Contacted',
    priority: 'Low',
    temperature: 'Cold',
    context:
      'Small founder-led sales team. Likely sensitive to tools that feel heavy. Lead with clarity and low setup.',
    prioritySignals: ['Founder-led sales', 'Lean team', 'No CRM admin'],
    previousNotes:
      'Maya is skeptical of operational drag. Keep the story extremely concrete and lightweight.',
    callObjective: 'Earn permission for a short second conversation around founder-led sales habits.',
    possibleObjections: ['Too many tools', 'Small team', 'No time to implement'],
    lastTouch: 'No previous contact',
    lastCall: 'No call yet',
  },
]

export const aiReview: AiReview = {
  score: 88,
  metrics,
  summary:
    'You handled the adoption objection calmly and kept the conversation grounded in Camille’s reality. The best moment was when you connected ramp speed to fewer manager review loops.',
  strengths: [
    'You slowed down before answering the strongest objection.',
    'Your next step sounded practical, not pushy.',
    'You used her hiring context naturally.',
  ],
  improvementFocus:
    'Pause a little longer after budget concerns. Let the prospect finish the emotional part before you move into proof.',
}

export const callRecords: CallRecord[] = [
  {
    id: 101,
    prospectId: 1,
    sourceCallId: null,
    prospectName: 'Camille Laurent',
    company: 'Nestra',
    date: 'Today, 10:42',
    duration: '12:48',
    score: 88,
    metrics,
    summary: 'Strong discovery. The clearest moment came when you tied ramp speed to lower manager review time.',
    transcriptPreview:
      'Camille pushed on adoption risk. You slowed down, clarified the team workflow, and moved the conversation toward pilot success criteria.',
    tags: ['Discovery', 'Pilot interest', 'Hiring signal'],
  },
  {
    id: 102,
    prospectId: 2,
    sourceCallId: null,
    prospectName: 'Arthur Besson',
    company: 'AltoPay',
    date: 'Yesterday, 16:05',
    duration: '08:19',
    score: 76,
    metrics: [
      { id: 'control', label: 'Lead control', score: 74, delta: '+2%' },
      { id: 'listening', label: 'Listening quality', score: 82, delta: '+3%' },
      { id: 'confidence', label: 'Confidence', score: 68, delta: '+5%' },
      { id: 'objections', label: 'Objection handling', score: 79, delta: '+4%' },
      { id: 'closing', label: 'Closing clarity', score: 67, delta: '+1%' },
    ],
    summary: 'Good pace, but the next step could have been framed earlier and with more confidence.',
    transcriptPreview:
      'Arthur described uneven discovery calls. You mirrored the issue well, then waited too long before proposing a concrete next step.',
    tags: ['Objection', 'Next step'],
  },
  {
    id: 103,
    prospectId: 3,
    sourceCallId: null,
    prospectName: 'Maya Chen',
    company: 'HelioWorks',
    date: 'Mon, 11:28',
    duration: '05:44',
    score: 71,
    metrics: [
      { id: 'control', label: 'Lead control', score: 69, delta: '+1%' },
      { id: 'listening', label: 'Listening quality', score: 76, delta: '+2%' },
      { id: 'confidence', label: 'Confidence', score: 70, delta: '+4%' },
      { id: 'objections', label: 'Objection handling', score: 66, delta: '+2%' },
      { id: 'closing', label: 'Closing clarity', score: 62, delta: '+1%' },
    ],
    summary: 'Concise opener. More patience after the first objection would have helped the conversation breathe.',
    transcriptPreview:
      'Maya worried about adding another tool. You answered quickly, then recovered by anchoring the value in one weekly habit.',
    tags: ['Cold call', 'Tool fatigue'],
  },
]

export const replayMessages: ReplayMessage[] = [
  {
    id: 1,
    speaker: 'ai',
    text: 'I understand the promise, but my team already has too many tools. Why would this one be different?',
  },
  {
    id: 2,
    speaker: 'seller',
    text: 'That is fair. The reason teams keep it is that it does not ask reps to change their workflow first. It quietly captures the call, notes the moments that matter, and gives managers a useful review without another admin ritual.',
  },
  {
    id: 3,
    speaker: 'ai',
    text: 'So what would the first week actually look like for my team?',
  },
]
