<script setup>
import { onMounted, ref } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const todos = ref([])
const title = ref('')
const isLoading = ref(false)
const error = ref('')

async function fetchTodos() {
  isLoading.value = true
  error.value = ''

  try {
    const response = await fetch(`${apiUrl}/todos`)
    if (!response.ok) {
      throw new Error('Impossible de charger les todos.')
    }

    todos.value = await response.json()
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    isLoading.value = false
  }
}

async function addTodo() {
  const trimmedTitle = title.value.trim()
  if (!trimmedTitle) return

  error.value = ''

  try {
    const response = await fetch(`${apiUrl}/todos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title: trimmedTitle }),
    })

    if (!response.ok) {
      throw new Error('Impossible d’ajouter la todo.')
    }

    const createdTodo = await response.json()
    todos.value = [createdTodo, ...todos.value]
    title.value = ''
  } catch (requestError) {
    error.value = requestError.message
  }
}

async function removeTodo(todoId) {
  error.value = ''

  try {
    const response = await fetch(`${apiUrl}/todos/${todoId}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error('Impossible de supprimer la todo.')
    }

    todos.value = todos.value.filter((todo) => todo.id !== todoId)
  } catch (requestError) {
    error.value = requestError.message
  }
}

onMounted(fetchTodos)
</script>

<template>
  <main class="grid min-h-screen place-items-start px-4 py-8 sm:px-5 sm:py-12">
    <section class="w-full max-w-3xl" aria-labelledby="todo-title">
      <div class="mb-7">
        <p class="mb-2 text-sm font-extrabold uppercase text-slate-500">
          Boilerplate FastAPI + Vue
        </p>
        <h1 id="todo-title" class="text-4xl font-bold leading-none text-slate-900 sm:text-6xl">
          Todo list
        </h1>
      </div>

      <form class="mb-5 grid gap-2.5" @submit.prevent="addTodo">
        <label for="todo-input" class="font-bold">Nouvelle todo</label>
        <div class="grid gap-2.5 sm:grid-cols-[1fr_auto]">
          <input
            id="todo-input"
            v-model="title"
            type="text"
            maxlength="255"
            placeholder="Ajouter un élément"
            class="min-h-11 min-w-0 rounded-md border border-slate-300 px-3.5 outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-200"
          />
          <button
            type="submit"
            class="min-h-11 rounded-md bg-blue-600 px-4.5 text-white hover:bg-blue-700 sm:px-5"
          >
            Ajouter
          </button>
        </div>
      </form>

      <p v-if="error" class="mt-5 font-bold text-red-700">{{ error }}</p>
      <p v-else-if="isLoading" class="mt-5 text-slate-600">Chargement...</p>

      <ul v-if="todos.length" class="mt-5.5 grid gap-2.5">
        <li
          v-for="todo in todos"
          :key="todo.id"
          class="grid min-h-14 items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-2.5 sm:grid-cols-[1fr_auto]"
        >
          <span class="break-words">{{ todo.title }}</span>
          <button
            type="button"
            aria-label="Supprimer"
            class="min-h-11 rounded-md bg-red-600 px-4.5 text-white hover:bg-red-700 sm:px-5"
            @click="removeTodo(todo.id)"
          >
            Supprimer
          </button>
        </li>
      </ul>

      <p v-else-if="!isLoading" class="mt-5 text-slate-600">Aucune todo pour le moment.</p>
    </section>
  </main>
</template>
