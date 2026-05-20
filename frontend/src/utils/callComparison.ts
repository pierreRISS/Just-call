import type { CallRecord, Metric } from '../types'

export type MetricComparison = {
  label: string
  original: number
  replay: number
  diff: number
}

const metricAliases: Record<string, string> = {
  discovery: 'listening',
  discovery_depth: 'listening',
  objection_handling: 'objections',
  next_step: 'closing',
  next_step_clarity: 'closing',
}

function metricKey(metric: Metric): string {
  const rawKey = metric.id || metric.label.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')
  return metricAliases[rawKey] ?? rawKey
}

export function buildMetricComparison(replayCall: CallRecord | null | undefined, sourceCall: CallRecord | null | undefined): MetricComparison[] {
  if (!replayCall || !sourceCall) return []

  const sourceByKey = new Map(sourceCall.metrics.map((metric) => [metricKey(metric), metric]))
  return replayCall.metrics
    .map((metric) => {
      const original = sourceByKey.get(metricKey(metric))
      if (!original) return null

      return {
        label: metric.label,
        original: original.score,
        replay: metric.score,
        diff: metric.score - original.score,
      }
    })
    .filter((comparison): comparison is MetricComparison => comparison !== null)
}
