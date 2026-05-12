<script setup lang="ts">
import { reactive, ref } from 'vue'
import ToastStack from '../components/ToastStack.vue'
import { useWorkspaceStore } from '../stores/workspace'

const workspace = useWorkspaceStore()
const isSubmitting = ref(false)
const form = reactive({
  email: 'pierre@just-call.local',
  password: 'justcall',
})

async function submit() {
  if (!form.email.trim() || !form.password || isSubmitting.value) return
  isSubmitting.value = true
  await workspace.signIn(form.email, form.password)
  isSubmitting.value = false
}
</script>

<template>
  <main class="grid min-h-screen place-items-center bg-[#f5f1e9] px-5 text-stone-950">
    <ToastStack :toasts="workspace.toasts" @dismiss="workspace.dismissToast" />

    <section class="w-full max-w-md rounded-[2rem] border border-white/70 bg-white/55 p-7 shadow-[0_34px_120px_rgba(85,68,42,0.14)] backdrop-blur-2xl">
      <div class="flex items-center gap-3">
        <div class="grid h-11 w-11 place-items-center rounded-2xl bg-stone-950 text-sm font-semibold text-white">JC</div>
        <div>
          <p class="text-sm font-semibold text-stone-950">Just Call</p>
          <p class="text-xs font-medium text-stone-400">Sign in to your call workspace</p>
        </div>
      </div>

      <form class="mt-8 grid gap-4" @submit.prevent="submit">
        <label class="grid gap-2 text-sm font-semibold text-stone-650">
          Email
          <input
            v-model="form.email"
            autocomplete="email"
            class="min-h-12 rounded-2xl border border-stone-200/80 bg-white/72 px-4 text-stone-950 outline-none transition focus:border-stone-300 focus:bg-white"
            type="email"
          />
        </label>
        <label class="grid gap-2 text-sm font-semibold text-stone-650">
          Password
          <input
            v-model="form.password"
            autocomplete="current-password"
            class="min-h-12 rounded-2xl border border-stone-200/80 bg-white/72 px-4 text-stone-950 outline-none transition focus:border-stone-300 focus:bg-white"
            type="password"
          />
        </label>

        <button
          type="submit"
          class="mt-2 min-h-12 rounded-full bg-stone-950 px-5 text-sm font-semibold text-white shadow-[0_18px_44px_rgba(28,25,23,0.18)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="isSubmitting || !form.email.trim() || !form.password"
        >
          {{ isSubmitting ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>
    </section>
  </main>
</template>
