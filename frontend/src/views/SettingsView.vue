<script setup lang="ts">
import { computed, ref } from 'vue'
import LumaSurface from '../components/LumaSurface.vue'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()
const newStatus = ref('')

async function addStatus() {
  const didAdd = await workspace.addStatusOption(newStatus.value)
  if (didAdd) newStatus.value = ''
}

const sections = computed(() => [
  {
    title: 'Audio settings',
    items: [
      `Input: ${workspace.settings.audioInput}`,
      `Noise cleanup: ${workspace.settings.noiseCleanup}`,
      'Speaker test ready',
    ],
  },
  {
    title: 'Microphone',
    items: [
      `Permission: ${workspace.settings.microphonePermission}`,
      'Auto gain enabled',
      'Echo cancellation enabled',
    ],
  },
  {
    title: 'Notifications',
    items: Object.entries(workspace.settings.notifications).map(([key, value]) => `${key.replaceAll('_', ' ')}: ${value ? 'on' : 'off'}`),
  },
  {
    title: 'AI preferences',
    items: Object.entries(workspace.settings.aiPreferences).map(([key, value]) => `${key.replaceAll('_', ' ')}: ${value}`),
  },
  {
    title: 'Integrations',
    items: Object.entries(workspace.settings.integrations).map(([key, value]) => `${key}: ${value}`),
  },
  {
    title: 'Account settings',
    items: [
      `User: ${workspace.currentUser.displayName}`,
      `Email: ${workspace.currentUser.email}`,
      `Role: ${workspace.currentUser.role}`,
    ],
  },
])
</script>

<template>
  <section class="grid gap-8">
    <div class="max-w-3xl">
      <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Settings</p>
      <h2 class="mt-3 text-4xl font-semibold tracking-[-0.06em] text-stone-950 sm:text-5xl">Everything technical, quietly organized.</h2>
    </div>

    <LumaSurface class="p-6" subtle>
      <div class="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-stone-400">Prospect statuses</p>
          <h3 class="mt-3 text-2xl font-semibold tracking-[-0.04em] text-stone-950">Customize your pipeline language.</h3>
        </div>
        <form class="flex gap-2" @submit.prevent="addStatus">
          <input
            v-model="newStatus"
            maxlength="40"
            class="min-h-11 rounded-full border border-stone-200/80 bg-white/62 px-4 text-sm font-semibold text-stone-700 outline-none"
            placeholder="New status"
          />
          <button type="submit" class="rounded-full bg-stone-950 px-4 text-sm font-semibold text-white disabled:opacity-40" :disabled="!newStatus.trim()">
            Add
          </button>
        </form>
      </div>
      <div class="mt-6 flex flex-wrap gap-2">
        <span
          v-for="status in workspace.settings.statusOptions"
          :key="status"
          class="rounded-full border border-stone-200/80 bg-white/55 px-3 py-1.5 text-xs font-semibold text-stone-650"
        >
          {{ status }}
        </span>
      </div>
    </LumaSurface>

    <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      <LumaSurface v-for="section in sections" :key="section.title" class="p-6" subtle>
        <h3 class="text-xl font-semibold tracking-[-0.04em] text-stone-950">{{ section.title }}</h3>
        <div class="mt-6 grid gap-3">
          <p v-for="item in section.items" :key="item" class="text-sm font-medium capitalize text-stone-650">{{ item }}</p>
        </div>
      </LumaSurface>
    </div>
  </section>
</template>
