import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  let nextId = 0
  let dismissTimer = null

  function show(message, options = {}) {
    clearTimeout(dismissTimer)
    const duration = options.duration || 3000

    const id = nextId++
    toasts.value = [{
      id,
      message,
      category: options.category,
      items: options.items || [],
    }]

    dismissTimer = setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, duration)
  }

  return { toasts, show }
})
