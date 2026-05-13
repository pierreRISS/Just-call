<script setup lang="ts">
import { computed, ref } from 'vue'
import CallDetailDrawer from '../components/CallDetailDrawer.vue'
import CallHistoryItem from '../components/CallHistoryItem.vue'
import LumaSurface from '../components/LumaSurface.vue'
import { useWorkspaceStore } from '../stores/workspace'
import type { CallRecord } from '../types'

const workspace = useWorkspaceStore()
const isDrawerOpen = ref(false)

const drawerCall = computed(() => (isDrawerOpen.value ? workspace.selectedCall : null))

function openCall(call: CallRecord) {
  workspace.selectCall(call)
  isDrawerOpen.value = true
}

function startReplay(call: CallRecord) {
  isDrawerOpen.value = false
  workspace.replayCall(call)
}
</script>

<template>
  <section class="grid gap-8">
    <div class="max-w-3xl">
      <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Review</p>
      <h2 class="mt-3 text-4xl font-semibold tracking-[-0.06em] text-stone-950 sm:text-5xl">Every call, calmly organized.</h2>
      <p class="mt-5 text-sm font-medium leading-6 text-stone-500">
        Browse recent conversations, review the AI summary, and replay moments that matter.
      </p>
    </div>

    <LumaSurface class="px-5 sm:px-8">
      <CallHistoryItem
        v-for="call in workspace.callRecords"
        :key="call.id"
        :call="call"
        @select="openCall"
        @replay="startReplay"
      />
    </LumaSurface>

    <CallDetailDrawer
      :call="drawerCall"
      :calls="workspace.callRecords"
      :replay-sessions="workspace.replaySessions"
      @close="isDrawerOpen = false"
      @replay="startReplay"
    />
  </section>
</template>
