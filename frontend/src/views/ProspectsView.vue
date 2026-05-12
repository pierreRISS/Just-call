<script setup lang="ts">
import { reactive, ref } from 'vue'
import ProspectDrawer from '../components/ProspectDrawer.vue'
import ProspectTable from '../components/ProspectTable.vue'
import type { Prospect } from '../types'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()
const isAddOpen = ref(false)
const isDetailsOpen = ref(false)
const isSubmitting = ref(false)

const form = reactive({
  name: '',
  company: '',
  role: '',
  phone: '',
  email: '',
  context: '',
})

function resetForm() {
  form.name = ''
  form.company = ''
  form.role = ''
  form.phone = ''
  form.email = ''
  form.context = ''
}

async function submitProspect() {
  if (!form.name.trim() || !form.phone.trim() || isSubmitting.value) return

  isSubmitting.value = true
  const didCreate = await workspace.addProspect({
    name: form.name,
    company: form.company,
    role: form.role,
    phone: form.phone,
    email: form.email,
    context: form.context,
  })
  isSubmitting.value = false

  if (didCreate) {
    resetForm()
    isAddOpen.value = false
    isDetailsOpen.value = true
  }
}

function openProspect(prospect: Prospect) {
  workspace.selectProspect(prospect)
  isDetailsOpen.value = true
}

async function archiveProspect(prospect: Prospect) {
  const didArchive = await workspace.archiveProspect(prospect)
  if (didArchive) isDetailsOpen.value = false
}
</script>

<template>
  <section class="grid gap-8">
    <div class="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
      <div class="max-w-3xl">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Prospects</p>
        <h2 class="mt-3 text-4xl font-semibold tracking-[-0.06em] text-stone-950 sm:text-5xl">A calm CRM for focused calls.</h2>
        <p class="mt-5 text-sm font-medium leading-6 text-stone-500">
          Clean context, thoughtful prioritization, and one soft path into the next conversation.
        </p>
        <p class="mt-4 text-sm font-semibold text-stone-500">
          {{ workspace.prospects.length }} prospects loaded{{ workspace.isLoading ? ' · Syncing...' : '' }}
        </p>
      </div>

      <button
        type="button"
        class="w-fit rounded-full bg-stone-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5"
        @click="isAddOpen = true"
      >
        Add prospect
      </button>
    </div>

    <div class="min-w-0">
      <ProspectTable
        :prospects="workspace.prospects"
        :selected-prospect-id="workspace.selectedProspect?.id"
        @select="openProspect"
        @call="workspace.prepareProspectCall"
      />
    </div>

    <ProspectDrawer
      :open="isDetailsOpen"
      :prospect="workspace.selectedProspect"
      :settings="workspace.settings"
      @archive="archiveProspect"
      @call="workspace.prepareProspectCall"
      @close="isDetailsOpen = false"
      @save="workspace.saveProspect"
    />

    <Transition name="panel">
      <div v-if="isAddOpen" class="fixed inset-0 z-40 bg-stone-950/10 backdrop-blur-sm" @click.self="isAddOpen = false">
        <aside class="absolute inset-y-0 right-0 grid w-full max-w-xl grid-rows-[auto_1fr] border-l border-white/70 bg-[#fbf8f1]/82 shadow-[0_30px_120px_rgba(60,45,25,0.2)] backdrop-blur-2xl">
          <div class="flex items-start justify-between gap-4 border-b border-stone-200/70 px-6 py-5">
            <div>
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">New prospect</p>
              <h3 class="mt-2 text-2xl font-semibold tracking-[-0.04em] text-stone-950">Add clean context</h3>
            </div>
            <button
              type="button"
              class="rounded-full border border-white/70 bg-white/55 px-4 py-2 text-sm font-semibold text-stone-600 transition hover:bg-white hover:text-stone-950"
              @click="isAddOpen = false"
            >
              Close
            </button>
          </div>

          <form class="grid content-start gap-4 overflow-y-auto p-6" @submit.prevent="submitProspect">
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Name
              <input v-model="form.name" required maxlength="120" class="min-h-12 rounded-2xl border border-stone-200/80 bg-white/62 px-4 text-stone-950 outline-none transition focus:border-stone-300 focus:bg-white" placeholder="Camille Laurent" />
            </label>

            <div class="grid gap-4 sm:grid-cols-2">
              <label class="grid gap-2 text-sm font-semibold text-stone-650">
                Company
                <input v-model="form.company" maxlength="120" class="min-h-12 rounded-2xl border border-stone-200/80 bg-white/62 px-4 text-stone-950 outline-none transition focus:border-stone-300 focus:bg-white" placeholder="Nestra" />
              </label>
              <label class="grid gap-2 text-sm font-semibold text-stone-650">
                Role
                <input v-model="form.role" maxlength="120" class="min-h-12 rounded-2xl border border-stone-200/80 bg-white/62 px-4 text-stone-950 outline-none transition focus:border-stone-300 focus:bg-white" placeholder="VP Revenue" />
              </label>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <label class="grid gap-2 text-sm font-semibold text-stone-650">
                Phone
                <input v-model="form.phone" required maxlength="40" type="tel" class="min-h-12 rounded-2xl border border-stone-200/80 bg-white/62 px-4 font-mono text-stone-950 outline-none transition focus:border-stone-300 focus:bg-white" placeholder="+33 6 12 34 56 78" />
              </label>
              <label class="grid gap-2 text-sm font-semibold text-stone-650">
                Email
                <input v-model="form.email" maxlength="255" type="email" class="min-h-12 rounded-2xl border border-stone-200/80 bg-white/62 px-4 text-stone-950 outline-none transition focus:border-stone-300 focus:bg-white" placeholder="camille@company.com" />
              </label>
            </div>

            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Quick context
              <textarea v-model="form.context" maxlength="4000" rows="8" class="resize-none rounded-2xl border border-stone-200/80 bg-white/62 px-4 py-3 text-stone-950 outline-none transition focus:border-stone-300 focus:bg-white" placeholder="Company context, sales signal, likely objection, reason to call..." />
            </label>

            <button
              type="submit"
              class="mt-2 min-h-12 rounded-full bg-stone-950 px-5 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="!form.name.trim() || !form.phone.trim() || isSubmitting"
            >
              {{ isSubmitting ? 'Adding...' : 'Add prospect' }}
            </button>
          </form>
        </aside>
      </div>
    </Transition>
  </section>
</template>
