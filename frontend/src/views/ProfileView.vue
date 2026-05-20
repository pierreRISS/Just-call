<script setup lang="ts">
import { computed } from 'vue'
import LumaSurface from '../components/LumaSurface.vue'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()

const completedCalls = computed(() => workspace.callRecords.filter((call) => call.status === 'completed'))

const strongestMetric = computed(() => {
  const metrics = workspace.performanceMetrics
  if (!metrics.length) return null
  return [...metrics].sort((left, right) => right.score - left.score)[0]
})

const performanceSummary = computed(() => {
  if (!completedCalls.value.length) return 'No reviewed calls yet. Complete a call to build a real performance profile.'
  if (!strongestMetric.value) return 'Reviewed calls are loaded, but no score metrics are available yet.'
  return `Your strongest current signal is ${strongestMetric.value.label.toLowerCase()} at ${strongestMetric.value.score}/100.`
})

const strengths = computed(() => {
  const unique = new Set<string>()
  completedCalls.value.forEach((call) => {
    call.strengths.forEach((strength) => {
      if (strength.trim()) unique.add(strength.trim())
    })
  })
  return Array.from(unique).slice(0, 3)
})

const focusAreas = computed(() => {
  const unique = new Set<string>()
  completedCalls.value.forEach((call) => {
    if (call.improvementFocus.trim()) unique.add(call.improvementFocus.trim())
  })
  return Array.from(unique).slice(0, 3)
})

const settingsSections = computed(() => [
  {
    title: 'Audio',
    items: [
      workspace.settings.audioInput ? `Input: ${workspace.settings.audioInput}` : '',
      workspace.settings.noiseCleanup ? `Noise cleanup: ${workspace.settings.noiseCleanup}` : '',
      workspace.settings.microphonePermission ? `Microphone: ${workspace.settings.microphonePermission}` : '',
    ].filter(Boolean),
  },
  {
    title: 'AI preferences',
    items: Object.entries(workspace.settings.aiPreferences).map(([key, value]) => `${key.replaceAll('_', ' ')}: ${value}`),
  },
  {
    title: 'Integrations',
    items: Object.entries(workspace.settings.integrations).map(([key, value]) => `${key}: ${value}`),
  },
])
</script>

<template>
  <section class="grid gap-8">
    <div class="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
      <LumaSurface class="p-8">
        <div class="grid justify-items-start gap-6">
          <div class="grid h-20 w-20 place-items-center rounded-[1.6rem] bg-stone-950 text-2xl font-semibold text-white">{{ workspace.currentUser.initials }}</div>
          <div>
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Profile</p>
            <h2 class="mt-3 text-4xl font-semibold tracking-[-0.06em] text-stone-950">{{ workspace.currentUser.displayName }}</h2>
            <p class="mt-3 text-sm font-medium text-stone-500">{{ workspace.currentUser.role }} · {{ workspace.currentUser.email }}</p>
          </div>
        </div>
      </LumaSurface>

      <div class="grid gap-6">
        <LumaSurface class="p-7" subtle>
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Performance overview</p>
          <p class="mt-4 max-w-2xl text-lg font-medium leading-8 text-stone-700">
            {{ performanceSummary }}
          </p>
        </LumaSurface>

        <div class="grid gap-6 md:grid-cols-2">
          <LumaSurface class="p-6" subtle>
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Strengths</p>
            <div class="mt-5 grid gap-3 text-sm font-semibold text-stone-650">
              <p v-for="strength in strengths" :key="strength">{{ strength }}</p>
              <p v-if="!strengths.length">No strengths detected yet.</p>
            </div>
          </LumaSurface>
          <LumaSurface class="p-6" subtle>
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Focus areas</p>
            <div class="mt-5 grid gap-3 text-sm font-semibold text-stone-650">
              <p v-for="focus in focusAreas" :key="focus">{{ focus }}</p>
              <p v-if="!focusAreas.length">No focus areas detected yet.</p>
            </div>
          </LumaSurface>
          <LumaSurface class="p-6" subtle>
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Recent activity</p>
            <div class="mt-5 grid gap-3 text-sm font-semibold text-stone-650">
              <p>{{ workspace.callRecords.length }} calls reviewed</p>
              <p>{{ workspace.callRecords.filter((call) => call.sourceCallId).length }} AI replays completed</p>
              <p>{{ workspace.prospects.length }} active prospects</p>
            </div>
          </LumaSurface>
        </div>
      </div>
    </div>

    <div class="grid gap-5 md:grid-cols-3">
      <LumaSurface v-for="section in settingsSections" :key="section.title" class="p-6" subtle>
        <h3 class="text-xl font-semibold tracking-[-0.04em] text-stone-950">{{ section.title }}</h3>
        <div class="mt-6 grid gap-3">
          <p v-for="item in section.items" :key="item" class="text-sm font-medium capitalize text-stone-650">{{ item }}</p>
        </div>
      </LumaSurface>
    </div>
  </section>
</template>
