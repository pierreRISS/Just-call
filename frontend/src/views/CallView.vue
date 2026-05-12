<script setup lang="ts">
import { computed, ref } from 'vue'
import AiReviewCard from '../components/AiReviewCard.vue'
import LumaSurface from '../components/LumaSurface.vue'
import NotesPanel from '../components/NotesPanel.vue'
import ProspectPanel from '../components/ProspectPanel.vue'
import Waveform from '../components/Waveform.vue'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()
const isProspectOpen = ref(true)
const isMuted = ref(false)
const seconds = ref(764)

const quickActions = ['Interested', 'Follow-up', 'Meeting booked', 'Send email', 'Budget issue', 'Not interested']
const isReplayCall = computed(() => Boolean(workspace.selectedCall?.sourceCallId))
const liveLabel = computed(() => (isReplayCall.value ? 'AI replay simulation' : 'Live call'))
const liveTitle = computed(() => (isReplayCall.value ? workspace.selectedCall.prospectName : workspace.selectedProspect.name))
const liveSubtitle = computed(() => {
  if (isReplayCall.value) return `Replay of call #${workspace.selectedCall.sourceCallId} · voice practice`
  return `${workspace.selectedProspect.role} · ${workspace.selectedProspect.company}`
})
const reviewLabel = computed(() => (isReplayCall.value ? 'Replay review' : 'Post-call review'))
const reviewTitle = computed(() => (isReplayCall.value ? 'Replay complete. Compare the improvement.' : 'A clean review, without the noise.'))
const reviewCopy = computed(() =>
  isReplayCall.value
    ? 'The AI scorecard shows whether this practice run corrected the original mistakes.'
    : 'The AI keeps the feedback human, practical, and encouraging.',
)
const replayComparison = computed(() => {
  if (!isReplayCall.value) return []
  const sourceCall = workspace.callRecords.find((call) => call.id === workspace.selectedCall.sourceCallId)
  if (!sourceCall) return []

  return workspace.selectedCall.metrics.map((metric) => {
    const original = sourceCall.metrics.find((item) => item.id === metric.id)
    return {
      label: metric.label,
      original: original?.score ?? 0,
      replay: metric.score,
      diff: metric.score - (original?.score ?? 0),
    }
  })
})

const timerLabel = computed(() => {
  const minutes = Math.floor(seconds.value / 60)
  const rest = seconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`
})

function saveNotes() {
  workspace.pushToast('Notes saved to the call timeline.')
}

function replayReview() {
  workspace.replayCall(workspace.selectedCall)
}
</script>

<template>
  <section class="grid gap-6">
    <Transition name="page" mode="out-in">
      <section v-if="workspace.callStage === 'prep'" key="prep" class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <LumaSurface class="p-6 sm:p-10">
          <div class="max-w-3xl">
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.24em] text-stone-400">Call preparation</p>
            <h2 class="mt-4 text-5xl font-semibold tracking-[-0.07em] text-stone-950">
              Prepare the conversation with {{ workspace.selectedProspect.name }}.
            </h2>
            <p class="mt-5 text-sm font-medium leading-6 text-stone-500">
              Review the context, keep the objective simple, then enter the call with quiet control.
            </p>
          </div>

          <div class="mt-12 grid gap-8 lg:grid-cols-2">
            <div>
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Previous notes</p>
              <p class="mt-3 text-base font-medium leading-7 text-stone-700">{{ workspace.selectedProspect.previousNotes }}</p>
            </div>
            <div>
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Call objective</p>
              <p class="mt-3 text-base font-medium leading-7 text-stone-700">{{ workspace.selectedProspect.callObjective }}</p>
            </div>
          </div>

          <div class="mt-10">
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Possible objections</p>
            <div class="mt-4 flex flex-wrap gap-2">
              <span
                v-for="objection in workspace.selectedProspect.possibleObjections"
                :key="objection"
                class="rounded-full border border-stone-200/80 bg-white/55 px-3 py-1.5 text-xs font-semibold text-stone-600"
              >
                {{ objection }}
              </span>
            </div>
          </div>

          <button
            type="button"
            class="mt-12 rounded-full bg-stone-950 px-7 py-3 text-sm font-semibold text-white shadow-[0_22px_60px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5"
            @click="workspace.beginLiveCall"
          >
            Start Call
          </button>
        </LumaSurface>

        <ProspectPanel :prospect="workspace.selectedProspect" />
      </section>

      <section v-else-if="workspace.callStage === 'live'" key="live" class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <div class="grid gap-6">
          <LumaSurface class="relative overflow-hidden px-6 py-8 sm:px-10">
            <div class="grid min-h-[24rem] content-center justify-items-center gap-8 text-center">
              <div>
                <p class="text-[0.68rem] font-semibold uppercase tracking-[0.24em] text-stone-400">{{ liveLabel }}</p>
                <h2 class="mt-3 text-4xl font-semibold tracking-[-0.06em] text-stone-950 sm:text-6xl">
                  {{ liveTitle }}
                </h2>
                <p class="mt-4 text-sm font-medium text-stone-500">
                  {{ liveSubtitle }}
                </p>
              </div>

              <Waveform active />

              <div class="flex flex-wrap items-center justify-center gap-3">
                <span class="rounded-full bg-white/60 px-4 py-2 font-mono text-sm font-semibold text-stone-700 shadow-sm">{{ timerLabel }}</span>
                <select
                  v-model="workspace.selectedQuickAction"
                  class="rounded-full border border-white/70 bg-white/60 px-4 py-2 text-sm font-semibold text-stone-650 shadow-sm outline-none backdrop-blur-xl"
                >
                  <option v-for="action in quickActions" :key="action" :value="action">{{ action }}</option>
                </select>
                <button
                  type="button"
                  class="rounded-full border border-white/70 bg-white/50 px-4 py-2 text-sm font-semibold text-stone-650 shadow-sm backdrop-blur-xl transition hover:bg-white hover:text-stone-950"
                  @click="isMuted = !isMuted"
                >
                  {{ isMuted ? 'Unmute' : 'Mute' }}
                </button>
                <button
                  type="button"
                  class="rounded-full border border-white/70 bg-white/50 px-4 py-2 text-sm font-semibold text-stone-650 shadow-sm backdrop-blur-xl transition hover:bg-white hover:text-stone-950"
                  @click="isProspectOpen = !isProspectOpen"
                >
                  {{ isProspectOpen ? 'Hide prospect' : 'Show prospect' }}
                </button>
                <button
                  type="button"
                  class="rounded-full bg-stone-950 px-5 py-2 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5"
                  @click="workspace.finishLiveCall(seconds)"
                >
                  End call
                </button>
              </div>
            </div>
          </LumaSurface>

          <NotesPanel v-model="workspace.callNotes" @save="saveNotes" />
        </div>

        <Transition name="panel">
          <ProspectPanel v-if="isProspectOpen" :prospect="workspace.selectedProspect" />
        </Transition>
      </section>

      <section v-else key="review" class="grid gap-8">
        <div class="max-w-3xl">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.24em] text-stone-400">{{ reviewLabel }}</p>
          <h2 class="mt-4 text-5xl font-semibold tracking-[-0.07em] text-stone-950">{{ reviewTitle }}</h2>
          <p class="mt-5 text-sm font-medium leading-6 text-stone-500">
            {{ reviewCopy }}
          </p>
        </div>

        <AiReviewCard :review="workspace.aiReview" :comparison="replayComparison" @replay="replayReview" />
      </section>
    </Transition>
  </section>
</template>
