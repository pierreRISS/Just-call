<script setup lang="ts">
import { computed, onMounted } from 'vue'
import AppSidebar from './components/AppSidebar.vue'
import ToastStack from './components/ToastStack.vue'
import AiReplayView from './views/AiReplayView.vue'
import CallView from './views/CallView.vue'
import CallsHistoryView from './views/CallsHistoryView.vue'
import HomeView from './views/HomeView.vue'
import AnalyticsView from './views/AnalyticsView.vue'
import ProfileView from './views/ProfileView.vue'
import ProspectsView from './views/ProspectsView.vue'
import LoginView from './views/LoginView.vue'
import { useWorkspaceStore } from './stores/workspace'
import type { PageId } from './types'

const workspace = useWorkspaceStore()

const navItems: Array<{ id: PageId; label: string }> = [
  { id: 'home', label: 'Home' },
  { id: 'prospects', label: 'Prospects' },
  { id: 'history', label: 'Calls' },
  { id: 'replay', label: 'Jouer IA' },
  { id: 'analytics', label: 'Analytics' },
]

const activeView = computed(() => {
  if (workspace.activePage === 'home') return HomeView
  if (workspace.activePage === 'prospects') return ProspectsView
  if (workspace.activePage === 'call') return CallView
  if (workspace.activePage === 'history') return CallsHistoryView
  if (workspace.activePage === 'replay') return AiReplayView
  if (workspace.activePage === 'analytics') return AnalyticsView
  return ProfileView
})

onMounted(() => {
  workspace.restoreSession()
})
</script>

<template>
  <LoginView v-if="workspace.isAuthReady && !workspace.isAuthenticated" />
  <main v-else-if="!workspace.isAuthReady" class="grid min-h-screen place-items-center bg-[#f5f1e9] text-sm font-semibold text-stone-500">
    Loading workspace...
  </main>
  <main v-else class="min-h-screen overflow-x-hidden bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.95),rgba(247,244,238,0.92)_42%,rgba(242,238,230,0.88))] text-stone-950">
    <ToastStack :toasts="workspace.toasts" @dismiss="workspace.dismissToast" />

    <div class="fixed inset-0 pointer-events-none">
      <div class="absolute left-1/2 top-[-18rem] h-[36rem] w-[36rem] -translate-x-1/2 rounded-full bg-white/55 blur-3xl" />
      <div class="absolute bottom-[-18rem] right-[-10rem] h-[34rem] w-[34rem] rounded-full bg-[#f5ead8]/70 blur-3xl" />
    </div>

    <div class="relative grid min-h-screen grid-cols-[auto_1fr]">
      <AppSidebar />

      <section class="relative min-w-0 px-5 py-5 sm:px-8 lg:px-12">
        <header class="mx-auto flex max-w-7xl items-center justify-between gap-4 py-2">
          <div class="min-w-0">
            <p class="text-[0.72rem] font-medium uppercase tracking-[0.24em] text-stone-400">AI calling workspace</p>
            <h1 class="mt-2 truncate text-xl font-semibold tracking-[-0.02em] text-stone-950 sm:text-2xl">
              {{ workspace.pageTitle }}
            </h1>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              class="grid h-9 w-9 place-items-center rounded-full bg-stone-950 text-sm font-semibold text-white"
              aria-label="Profile"
              @click="workspace.setPage('profile')"
            >
              {{ workspace.currentUser.initials }}
            </button>
          </div>
        </header>

        <nav class="mx-auto mt-5 flex max-w-7xl gap-2 overflow-x-auto pb-1 md:hidden">
          <button
            v-for="item in navItems"
            :key="item.id"
            type="button"
            class="shrink-0 rounded-full border border-white/70 bg-white/45 px-4 py-2 text-sm font-semibold text-stone-500 shadow-sm backdrop-blur-xl transition"
            :class="workspace.activePage === item.id ? 'bg-stone-950 text-white' : 'hover:bg-white hover:text-stone-950'"
            :aria-label="item.label"
            @click="workspace.setPage(item.id)"
          >
            {{ item.label }}
          </button>
        </nav>

        <div class="mx-auto max-w-7xl pt-8">
          <Transition name="page" mode="out-in">
            <component :is="activeView" :key="workspace.activePage" />
          </Transition>
        </div>
      </section>
    </div>
  </main>
</template>
