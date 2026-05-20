<script setup lang="ts">
import {
  BarChart3,
  Bot,
  Home,
  LogOut,
  PanelLeftClose,
  PanelLeftOpen,
  PhoneCall,
  Settings,
  Users,
  type LucideIcon,
} from 'lucide-vue-next'
import type { PageId } from '../types'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()

const navItems: Array<{ id: PageId; label: string; icon: LucideIcon }> = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'prospects', label: 'Prospects', icon: Users },
  { id: 'history', label: 'Calls', icon: PhoneCall },
  { id: 'replay', label: 'Jouer IA', icon: Bot },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'settings', label: 'Settings', icon: Settings },
]
</script>

<template>
  <aside
    class="relative z-50 hidden h-screen shrink-0 border-r border-white/60 bg-white/38 shadow-[18px_0_80px_rgba(85,68,42,0.08)] backdrop-blur-2xl transition-[width] duration-300 ease-[cubic-bezier(.22,1,.36,1)] md:block"
    :class="workspace.sidebarCollapsed ? 'w-[5.25rem]' : 'w-72'"
  >
    <div class="flex h-full flex-col px-4 py-5">
      <div class="flex items-center justify-between gap-3">
        <button
          type="button"
          class="group flex min-w-0 items-center gap-3 rounded-2xl px-2 py-2 text-left transition hover:bg-white/60"
          :class="workspace.activePage === 'profile' ? 'bg-white/70 shadow-[0_18px_48px_rgba(85,68,42,0.08)]' : ''"
          aria-label="Profile"
          @click="workspace.setPage('profile')"
        >
          <span class="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-stone-950 text-sm font-semibold text-white shadow-[0_14px_34px_rgba(28,25,23,0.18)]">
            {{ workspace.currentUser.initials }}
          </span>
          <span v-if="!workspace.sidebarCollapsed" class="min-w-0">
            <span class="block truncate text-sm font-semibold tracking-[-0.01em] text-stone-950">{{ workspace.currentUser.displayName }}</span>
            <span class="block truncate text-xs font-medium text-stone-400">Profile and settings</span>
          </span>
        </button>

        <button
          type="button"
          class="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-white/60 bg-white/45 text-stone-500 transition hover:bg-white hover:text-stone-950"
          :aria-label="workspace.sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
          @click="workspace.toggleSidebar"
        >
          <PanelLeftOpen v-if="workspace.sidebarCollapsed" class="h-4 w-4" stroke-width="2" />
          <PanelLeftClose v-else class="h-4 w-4" stroke-width="2" />
        </button>
      </div>

      <nav class="mt-8 grid gap-1">
        <button
          v-for="item in navItems"
          :key="item.id"
          type="button"
          class="group flex min-h-12 items-center gap-3 rounded-2xl px-3 text-left text-sm font-medium transition duration-300"
          :class="workspace.activePage === item.id ? 'bg-white/70 text-stone-950 shadow-[0_18px_48px_rgba(85,68,42,0.08)]' : 'text-stone-500 hover:bg-white/45 hover:text-stone-950'"
          :aria-label="item.label"
          @click="workspace.setPage(item.id)"
        >
          <span class="grid h-8 w-8 shrink-0 place-items-center rounded-full border border-stone-200/70 bg-white/50">
            <component :is="item.icon" class="h-[17px] w-[17px]" stroke-width="2" />
          </span>
          <span v-if="!workspace.sidebarCollapsed" class="truncate">{{ item.label }}</span>
        </button>
      </nav>
      <button
        type="button"
        class="mt-auto flex min-h-11 items-center gap-3 rounded-2xl border border-white/65 bg-white/42 px-3 text-left text-sm font-semibold text-stone-600 shadow-[0_18px_60px_rgba(85,68,42,0.08)] backdrop-blur-2xl transition hover:bg-white hover:text-stone-950"
        aria-label="Sign out"
        @click="workspace.signOut"
      >
        <LogOut class="h-[17px] w-[17px] shrink-0" stroke-width="2" />
        <span v-if="!workspace.sidebarCollapsed">Sign out</span>
      </button>
    </div>
  </aside>
</template>
