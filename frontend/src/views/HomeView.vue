<script setup lang="ts">
import LumaSurface from '../components/LumaSurface.vue'
import ScoreMetricList from '../components/ScoreMetricList.vue'
import StartCallButton from '../components/StartCallButton.vue'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()
</script>

<template>
  <section class="grid min-h-[calc(100vh-9.5rem)] place-items-center pb-10">
    <div class="grid w-full max-w-5xl justify-items-center gap-14">
      <div class="grid justify-items-center gap-8 text-center">
        <p class="max-w-xl text-sm font-medium leading-6 text-stone-500">
          A quiet workspace for precise calls, clean notes, and AI replay practice after every conversation.
        </p>
        <StartCallButton @start="workspace.startCall" />
      </div>

      <LumaSurface class="w-full p-5 sm:p-7" subtle>
        <div class="grid gap-7 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Weekly AI insight</p>
            <h2 class="mt-3 text-2xl font-semibold tracking-[-0.04em] text-stone-950">
              Your objection handling improved this week.
            </h2>
          </div>
          <span class="rounded-full bg-white/65 px-4 py-2 text-sm font-semibold text-stone-600 shadow-sm">+6% from last week</span>
        </div>

        <div class="mt-10">
          <ScoreMetricList :metrics="workspace.metrics" />
        </div>
      </LumaSurface>
    </div>
  </section>
</template>
