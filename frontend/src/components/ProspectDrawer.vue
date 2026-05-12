<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { Prospect, WorkspaceSettings } from '../types'

const props = defineProps<{
  prospect: Prospect | null
  settings: WorkspaceSettings
  open: boolean
}>()

const emit = defineEmits<{
  archive: [prospect: Prospect]
  call: [prospect: Prospect]
  close: []
  save: [prospectId: number, updates: Partial<Prospect>]
}>()

const form = reactive({
  name: '',
  company: '',
  role: '',
  phone: '',
  email: '',
  status: '',
  priority: 'Medium' as Prospect['priority'],
  temperature: 'Neutral' as Prospect['temperature'],
  context: '',
  previousNotes: '',
  callObjective: '',
  possibleObjections: '',
  prioritySignals: '',
})

watch(
  () => props.prospect,
  (prospect) => {
    if (!prospect) return
    form.name = prospect.name
    form.company = prospect.company
    form.role = prospect.role
    form.phone = prospect.phone
    form.email = prospect.email
    form.status = prospect.status
    form.priority = prospect.priority
    form.temperature = prospect.temperature
    form.context = prospect.context
    form.previousNotes = prospect.previousNotes
    form.callObjective = prospect.callObjective
    form.possibleObjections = prospect.possibleObjections.join(', ')
    form.prioritySignals = prospect.prioritySignals.join(', ')
  },
  { immediate: true },
)

function listFromText(value: string) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function save(updates: Partial<Prospect>) {
  if (!props.prospect) return
  emit('save', props.prospect.id, updates)
}
</script>

<template>
  <Transition name="panel">
    <div v-if="open && prospect" class="fixed inset-0 z-40 bg-stone-950/10 backdrop-blur-sm" @click.self="$emit('close')">
      <aside class="absolute inset-y-0 right-0 grid w-full max-w-2xl grid-rows-[auto_1fr_auto] border-l border-white/70 bg-[#fbf8f1]/88 shadow-[0_30px_120px_rgba(60,45,25,0.2)] backdrop-blur-2xl">
        <div class="flex items-start justify-between gap-4 border-b border-stone-200/70 px-6 py-5">
          <div class="min-w-0">
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-stone-400">Prospect details</p>
            <input
              v-model="form.name"
              class="mt-2 w-full bg-transparent text-3xl font-semibold tracking-[-0.05em] text-stone-950 outline-none"
              @blur="save({ name: form.name })"
            />
          </div>
          <button
            type="button"
            class="rounded-full border border-white/70 bg-white/55 px-4 py-2 text-sm font-semibold text-stone-600 transition hover:bg-white hover:text-stone-950"
            @click="$emit('close')"
          >
            Close
          </button>
        </div>

        <div class="grid content-start gap-5 overflow-y-auto p-6">
          <div class="grid gap-4 sm:grid-cols-3">
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Status
              <select v-model="form.status" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 outline-none" @change="save({ status: form.status })">
                <option v-for="status in settings.statusOptions" :key="status" :value="status">{{ status }}</option>
              </select>
            </label>
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Priority
              <select v-model="form.priority" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 outline-none" @change="save({ priority: form.priority })">
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
              </select>
            </label>
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Temperature
              <select v-model="form.temperature" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 outline-none" @change="save({ temperature: form.temperature })">
                <option>Warm</option>
                <option>Neutral</option>
                <option>Cold</option>
              </select>
            </label>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Company
              <input v-model="form.company" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 outline-none" @blur="save({ company: form.company })" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Role
              <input v-model="form.role" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 outline-none" @blur="save({ role: form.role })" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Phone
              <input v-model="form.phone" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 font-mono outline-none" @blur="save({ phone: form.phone })" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Email
              <input v-model="form.email" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 outline-none" @blur="save({ email: form.email })" />
            </label>
          </div>

          <label class="grid gap-2 text-sm font-semibold text-stone-650">
            Context
            <textarea v-model="form.context" rows="5" class="resize-none rounded-2xl border border-stone-200/80 bg-white/62 px-3 py-3 outline-none" @blur="save({ context: form.context })" />
          </label>
          <label class="grid gap-2 text-sm font-semibold text-stone-650">
            Previous notes
            <textarea v-model="form.previousNotes" rows="4" class="resize-none rounded-2xl border border-stone-200/80 bg-white/62 px-3 py-3 outline-none" @blur="save({ previousNotes: form.previousNotes })" />
          </label>
          <label class="grid gap-2 text-sm font-semibold text-stone-650">
            Call objective
            <textarea v-model="form.callObjective" rows="3" class="resize-none rounded-2xl border border-stone-200/80 bg-white/62 px-3 py-3 outline-none" @blur="save({ callObjective: form.callObjective })" />
          </label>

          <div class="grid gap-4 sm:grid-cols-2">
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Objections
              <input v-model="form.possibleObjections" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 outline-none" @blur="save({ possibleObjections: listFromText(form.possibleObjections) })" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-stone-650">
              Signals
              <input v-model="form.prioritySignals" class="min-h-11 rounded-2xl border border-stone-200/80 bg-white/62 px-3 outline-none" @blur="save({ prioritySignals: listFromText(form.prioritySignals) })" />
            </label>
          </div>
        </div>

        <div class="flex flex-wrap items-center justify-between gap-3 border-t border-stone-200/70 px-6 py-4">
          <button type="button" class="rounded-full border border-stone-200 bg-white/55 px-4 py-2 text-sm font-semibold text-stone-600 hover:bg-white" @click="$emit('archive', prospect)">
            Archive
          </button>
          <button type="button" class="rounded-full bg-stone-950 px-5 py-2 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5" @click="$emit('call', prospect)">
            Prepare call
          </button>
        </div>
      </aside>
    </div>
  </Transition>
</template>
