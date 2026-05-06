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
  <main class="app-shell">
    <section class="todo-panel" aria-labelledby="todo-title">
      <div class="panel-header">
        <p class="eyebrow">Boilerplate FastAPI + Vue</p>
        <h1 id="todo-title">Todo list</h1>
      </div>

      <form class="todo-form" @submit.prevent="addTodo">
        <label for="todo-input">Nouvelle todo</label>
        <div class="input-row">
          <input
            id="todo-input"
            v-model="title"
            type="text"
            maxlength="255"
            placeholder="Ajouter un élément"
          />
          <button type="submit">Ajouter</button>
        </div>
      </form>

      <p v-if="error" class="status error">{{ error }}</p>
      <p v-else-if="isLoading" class="status">Chargement...</p>

      <ul v-if="todos.length" class="todo-list">
        <li v-for="todo in todos" :key="todo.id">
          <span>{{ todo.title }}</span>
          <button type="button" aria-label="Supprimer" @click="removeTodo(todo.id)">
            Supprimer
          </button>
        </li>
      </ul>

      <p v-else-if="!isLoading" class="empty-state">Aucune todo pour le moment.</p>
    </section>
  </main>
</template>

