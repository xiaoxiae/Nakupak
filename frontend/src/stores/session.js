import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sessions } from '../services/api'
import { nameCompare } from '../utils/sort'
import { queueAction } from '../services/offline'

export const useSessionStore = defineStore('session', () => {
  const activeSession = ref(null)
  const loading = ref(false)

  const isActive = computed(() => !!activeSession.value)

  const sortedItems = computed(() => {
    if (!activeSession.value?.session_items) return []

    return [...activeSession.value.session_items].sort((a, b) => {
      const catA = a.item?.category?.name || ''
      const catB = b.item?.category?.name || ''
      return nameCompare(catA, catB)
    })
  })

  const checkedCount = computed(() =>
    activeSession.value?.session_items?.filter(i => i.checked).length || 0
  )

  const totalCount = computed(() =>
    activeSession.value?.session_items?.length || 0
  )

  async function fetchActive() {
    loading.value = true
    try {
      const response = await sessions.getActive()
      activeSession.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function startSession() {
    loading.value = true
    try {
      const response = await sessions.start()
      activeSession.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function toggleCheck(itemId) {
    const item = activeSession.value?.session_items?.find(i => i.id === itemId)
    if (!item) return

    // Optimistic update
    item.checked = !item.checked
    item.checked_at = item.checked ? new Date().toISOString() : null

    try {
      const response = await sessions.toggleCheck(itemId)
      item.checked = response.data.checked
      item.checked_at = response.data.checked_at
    } catch (error) {
      // Queue for later replay if offline / network error
      await queueAction({ type: 'toggle_check', itemId })
    }
  }

  async function completeSession() {
    loading.value = true
    try {
      await sessions.complete()
      activeSession.value = null
    } finally {
      loading.value = false
    }
  }

  async function abortSession() {
    loading.value = true
    try {
      await sessions.abort()
      activeSession.value = null
    } finally {
      loading.value = false
    }
  }

  return {
    activeSession,
    loading,
    isActive,
    sortedItems,
    checkedCount,
    totalCount,
    fetchActive,
    startSession,
    toggleCheck,
    completeSession,
    abortSession,
  }
}, {
  persist: {
    key: 'nakupak-session',
    pick: ['activeSession'],
  },
})
