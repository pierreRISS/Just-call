<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'
import AiReviewCard from '../components/AiReviewCard.vue'
import LumaSurface from '../components/LumaSurface.vue'
import ReplayBadge from '../components/ReplayBadge.vue'
import ScoreMetricList from '../components/ScoreMetricList.vue'
import Waveform from '../components/Waveform.vue'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()
const selectedMode = computed(() => workspace.selectedReplaySession?.simulationMode ?? 'Text replay')
const sourceCalls = computed(() => workspace.callRecords.filter((call) => !call.sourceCallId))
const selectedSourceCall = computed(() => {
  const currentCall = workspace.selectedCall
  const sourceId = currentCall?.sourceCallId ?? currentCall?.id
  return sourceCalls.value.find((call) => call.id === sourceId) ?? sourceCalls.value[0] ?? null
})
const selectedSourceCallId = computed({
  get: () => selectedSourceCall.value?.id ?? 0,
  set: (id: number) => {
    const call = sourceCalls.value.find((item) => item.id === Number(id))
    if (call) workspace.prepareReplayCall(call)
  },
})
const replayComparison = computed(() => {
  if (!workspace.selectedCall?.sourceCallId || !selectedSourceCall.value) return []

  return workspace.selectedCall.metrics.map((metric) => {
    const original = selectedSourceCall.value?.metrics.find((item) => item.id === metric.id)
    return {
      label: metric.label,
      original: original?.score ?? 0,
      replay: metric.score,
      diff: metric.score - (original?.score ?? 0),
    }
  })
})
const draftMessage = ref('')
const isSending = ref(false)
const isStarting = ref(false)
const seconds = ref(0)
const messagesEnd = ref<HTMLElement | null>(null)
let timerId = 0

const timerLabel = computed(() => {
  const minutes = Math.floor(seconds.value / 60)
  const rest = seconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`
})

async function startSimulation() {
  if (!selectedSourceCall.value || isStarting.value) return

  isStarting.value = true
  seconds.value = 0
  window.clearInterval(timerId)
  await workspace.beginReplaySimulation(selectedSourceCall.value)
  if (workspace.callStage === 'live') {
    timerId = window.setInterval(() => {
      seconds.value += 1
    }, 1000)
  }
  isStarting.value = false
}

async function sendMessage() {
  if (isSending.value || !draftMessage.value.trim()) return

  const message = draftMessage.value
  draftMessage.value = ''
  isSending.value = true
  const sent = await workspace.sendReplayText(message)
  isSending.value = false
  if (!sent) draftMessage.value = message
  await nextTick()
  messagesEnd.value?.scrollIntoView({ behavior: 'smooth', block: 'end' })
}

async function finishSimulation() {
  window.clearInterval(timerId)
  await workspace.finishReplaySimulation(seconds.value)
}

onBeforeUnmount(() => {
  window.clearInterval(timerId)
})
</script>

<template>
  <section class="grid gap-6">
    <Transition name="page" mode="out-in">
      <section v-if="workspace.callStage === 'prep'" key="prep" class="grid gap-6">
        <LumaSurface class="p-6 sm:p-8">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div class="max-w-3xl">
              <ReplayBadge />
              <h2 class="mt-5 text-4xl font-semibold tracking-[-0.06em] text-stone-950 sm:text-5xl">
                Jouer avec une IA
              </h2>
              <p class="mt-4 max-w-2xl text-sm font-medium leading-6 text-stone-500">
                Choisis un call passé, relis le contexte, puis démarre une simulation où tu prends la parole en premier.
              </p>
            </div>
          </div>

          <div class="mt-10 grid gap-8 lg:grid-cols-[minmax(0,1fr)_20rem]">
            <div>
              <label class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400" for="replay-call">
                Call passé
              </label>
              <select
                id="replay-call"
                v-model.number="selectedSourceCallId"
                class="mt-3 w-full rounded-2xl border border-white/70 bg-white/65 px-4 py-3 text-sm font-semibold text-stone-700 outline-none backdrop-blur-xl"
              >
                <option v-for="call in sourceCalls" :key="call.id" :value="call.id">
                  {{ call.prospectName }} · {{ call.company }} · {{ call.date }}
                </option>
              </select>

              <div v-if="selectedSourceCall" class="mt-6 rounded-[1.5rem] border border-white/70 bg-white/44 p-5">
                <div class="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Résumé original</p>
                    <h3 class="mt-3 text-2xl font-semibold tracking-[-0.04em] text-stone-950">
                      {{ selectedSourceCall.prospectName }}
                    </h3>
                    <p class="mt-1 text-sm font-semibold text-stone-500">{{ selectedSourceCall.company }} · {{ selectedSourceCall.duration }}</p>
                  </div>
                  <div class="text-right">
                    <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Score</p>
                    <p class="mt-2 text-4xl font-semibold tracking-[-0.06em] text-stone-950">{{ selectedSourceCall.score }}</p>
                  </div>
                </div>
                <p class="mt-5 text-sm font-medium leading-6 text-stone-650">{{ selectedSourceCall.summary }}</p>
                <p class="mt-4 whitespace-pre-line text-sm font-medium leading-6 text-stone-500">{{ selectedSourceCall.transcriptPreview }}</p>
              </div>

              <button
                type="button"
                class="mt-8 w-full rounded-full bg-stone-950 px-7 py-3 text-sm font-semibold text-white shadow-[0_22px_60px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!selectedSourceCall || isStarting"
                @click="startSimulation"
              >
                {{ isStarting ? 'Starting...' : 'Lancer la simulation' }}
              </button>
            </div>

            <div v-if="selectedSourceCall" class="rounded-[1.5rem] bg-stone-950/[0.035] p-4">
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Scorecard original</p>
              <ScoreMetricList class="mt-4" :metrics="selectedSourceCall.metrics" compact />
            </div>
          </div>
        </LumaSurface>
      </section>

      <section v-else-if="workspace.callStage === 'live'" key="live" class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
        <LumaSurface class="overflow-hidden p-6 sm:p-8">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.24em] text-stone-400">AI simulation</p>
              <h2 class="mt-4 text-4xl font-semibold tracking-[-0.06em] text-stone-950 sm:text-5xl">
                {{ selectedSourceCall?.prospectName }}
              </h2>
              <p class="mt-4 max-w-2xl text-sm font-medium leading-6 text-stone-500">
                Aucun message n'est injecté au départ. À toi d'ouvrir la conversation.
              </p>
            </div>
            <button
              type="button"
              class="rounded-full bg-stone-950 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5"
              @click="finishSimulation"
            >
              Terminer
            </button>
          </div>

          <div class="my-8">
            <Waveform active />
          </div>

          <div class="mb-6 flex flex-wrap items-center gap-3">
            <span class="rounded-full bg-white/60 px-4 py-2 font-mono text-sm font-semibold text-stone-700 shadow-sm">{{ timerLabel }}</span>
            <span class="rounded-full bg-white/60 px-4 py-2 text-sm font-semibold text-stone-650 shadow-sm">{{ selectedMode }}</span>
          </div>

          <div class="grid min-h-[13rem] content-start gap-4">
            <p v-if="!workspace.replayMessages.length" class="rounded-[1.5rem] border border-dashed border-stone-300/70 bg-white/38 px-5 py-8 text-center text-sm font-semibold text-stone-500">
              La conversation est vide.
            </p>
            <article
              v-for="message in workspace.replayMessages"
              :key="message.id"
              class="max-w-[46rem] rounded-[1.5rem] px-5 py-4 text-sm font-medium leading-6"
              :class="message.speaker === 'ai' ? 'bg-white/64 text-stone-700 shadow-sm' : 'ml-auto bg-stone-950 text-white shadow-[0_18px_44px_rgba(28,25,23,0.16)]'"
            >
              {{ message.text }}
            </article>
            <div ref="messagesEnd" />
          </div>

          <form class="mt-8 flex flex-col gap-3 sm:flex-row" @submit.prevent="sendMessage">
            <input
              v-model="draftMessage"
              type="text"
              class="min-h-12 flex-1 rounded-full border border-white/70 bg-white/70 px-5 text-sm font-semibold text-stone-700 outline-none backdrop-blur-xl placeholder:text-stone-400"
              placeholder="Écris ta première réponse..."
              :disabled="isSending"
            >
            <button
              type="submit"
              class="rounded-full bg-stone-950 px-6 py-3 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="isSending || !draftMessage.trim()"
            >
              {{ isSending ? 'Thinking...' : 'Send' }}
            </button>
          </form>
        </LumaSurface>

        <aside v-if="selectedSourceCall" class="grid content-start gap-4">
          <LumaSurface class="p-5" subtle>
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Original call</p>
            <h3 class="mt-3 text-2xl font-semibold tracking-[-0.04em] text-stone-950">{{ selectedSourceCall.company }}</h3>
            <p class="mt-4 text-sm font-medium leading-6 text-stone-500">{{ selectedSourceCall.summary }}</p>
          </LumaSurface>

          <LumaSurface class="p-5" subtle>
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Original score</p>
            <p class="mt-3 text-5xl font-semibold tracking-[-0.06em] text-stone-950">{{ selectedSourceCall.score }}</p>
          </LumaSurface>
        </aside>
      </section>

      <section v-else key="review" class="grid gap-8">
        <div class="max-w-3xl">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.24em] text-stone-400">Replay review</p>
          <h2 class="mt-4 text-5xl font-semibold tracking-[-0.07em] text-stone-950">Simulation terminée.</h2>
          <p class="mt-5 text-sm font-medium leading-6 text-stone-500">
            Le scorecard reprend le même format que l'analyse post-call, avec la comparaison contre le call original.
          </p>
        </div>

        <AiReviewCard :review="workspace.aiReview" :comparison="replayComparison" @replay="workspace.replayCall(workspace.selectedCall)" />
      </section>
    </Transition>
  </section>
</template>
