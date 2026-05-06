const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${apiUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  if (!response.ok) {
    let message = 'Une erreur est survenue.'
    try {
      const payload = await response.json()
      message = payload.detail || message
    } catch {
      message = response.statusText || message
    }
    throw new Error(message)
  }

  if (response.status === 204) return null
  return response.json()
}

export function createContact(payload) {
  return apiRequest('/contacts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateContact(contactId, payload) {
  return apiRequest(`/contacts/${contactId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function deleteContact(contactId) {
  return apiRequest(`/contacts/${contactId}`, {
    method: 'DELETE',
  })
}

export function createCallLog(payload) {
  return apiRequest('/call-logs', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function clearCallLogs() {
  return apiRequest('/call-logs', {
    method: 'DELETE',
  })
}
