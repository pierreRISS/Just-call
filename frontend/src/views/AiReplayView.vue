<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import LumaSurface from '../components/LumaSurface.vue'
import ReplayBadge from '../components/ReplayBadge.vue'
import Waveform from '../components/Waveform.vue'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()
const difficulties = ['Calm', 'Balanced', 'Demanding']
const objectionTypes = ['Tool fatigue', 'Budget timing', 'Adoption risk', 'No urgency']
const behaviors = ['Skeptical but fair', 'Busy executive', 'Detail-oriented', 'Quiet founder']
const modes = ['Discovery', 'Objection practice', 'Closing clarity']
const selectedDifficulty = computed(() => workspace.selectedReplaySession?.difficulty ?? 'Balanced')
const selectedObjection = computed(() => workspace.selectedReplaySession?.objectionType ?? 'Tool fatigue')
const selectedBehavior = computed(() => workspace.selectedReplaySession?.prospectBehavior ?? 'Skeptical but fair')
const selectedMode = computed(() => workspace.selectedReplaySession?.simulationMode ?? 'Text replay')
const draftMessage = ref('')
const isSending = ref(false)
const messagesEnd = ref<HTMLElement | null>(null)

function updateSimulation() {
  workspace.pushToast('Simulation settings updated.', 'info')
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
</script>

<template>
  <section class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
    <LumaSurface class="overflow-hidden p-6 sm:p-8">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <ReplayBadge />
          <h2 class="mt-5 text-4xl font-semibold tracking-[-0.06em] text-stone-950 sm:text-5xl">
            Replay with {{ workspace.selectedCall.prospectName }}
          </h2>
          <p class="mt-4 max-w-2xl text-sm font-medium leading-6 text-stone-500">
            Practice the same objection in text with an AI prospect that mirrors the original call context.
          </p>
        </div>
        <button
          type="button"
          class="rounded-full bg-stone-950 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5"
          @click="updateSimulation"
        >
          Update simulation
        </button>
      </div>

      <div class="my-10">
        <Waveform active />
      </div>

      <div class="mb-10 grid gap-3 md:grid-cols-4">
        <select class="rounded-full border border-white/70 bg-white/60 px-4 py-2 text-sm font-semibold text-stone-650 outline-none backdrop-blur-xl" :value="selectedDifficulty">
          <option v-for="item in difficulties" :key="item">{{ item }}</option>
        </select>
        <select class="rounded-full border border-white/70 bg-white/60 px-4 py-2 text-sm font-semibold text-stone-650 outline-none backdrop-blur-xl" :value="selectedObjection">
          <option v-for="item in objectionTypes" :key="item">{{ item }}</option>
        </select>
        <select class="rounded-full border border-white/70 bg-white/60 px-4 py-2 text-sm font-semibold text-stone-650 outline-none backdrop-blur-xl" :value="selectedBehavior">
          <option v-for="item in behaviors" :key="item">{{ item }}</option>
        </select>
        <select class="rounded-full border border-white/70 bg-white/60 px-4 py-2 text-sm font-semibold text-stone-650 outline-none backdrop-blur-xl" :value="selectedMode">
          <option v-for="item in modes" :key="item">{{ item }}</option>
        </select>
      </div>

      <div class="grid gap-4">
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
          placeholder="Type your seller reply..."
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

      <div v-if="!workspace.selectedReplaySession" class="mt-6 rounded-2xl bg-white/55 p-4 text-sm font-semibold text-stone-500">
        Start a replay from any AI review to create a live practice session.
      </div>
    </LumaSurface>

    <aside class="grid content-start gap-4">
      <LumaSurface class="p-5" subtle>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Focus</p>
        <h3 class="mt-3 text-2xl font-semibold tracking-[-0.04em] text-stone-950">Handle tool fatigue.</h3>
        <p class="mt-4 text-sm font-medium leading-6 text-stone-500">
          Slow down after the objection. Reflect the concern before explaining workflow fit.
        </p>
      </LumaSurface>

      <LumaSurface class="p-5" subtle>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Original score</p>
        <p class="mt-3 text-5xl font-semibold tracking-[-0.06em] text-stone-950">{{ workspace.selectedCall.score }}</p>
      </LumaSurface>
    </aside>
  </section>
</template>
