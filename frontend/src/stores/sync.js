import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useListStore } from './list'
import { useAuthStore } from './auth'
import { shoppingList } from '../services/api'
import { getQueuedActions, removeFromQueue } from '../services/offline'

export const useSyncStore = defineStore('sync', () => {
  const ws = ref(null)
  const connected = ref(false)
  const offline = ref(!navigator.onLine)

  function connect() {
    const authStore = useAuthStore()
    if (!authStore.token) return

    const apiUrl = import.meta.env.VITE_API_URL || ''
    let wsUrl
    if (apiUrl) {
      wsUrl = apiUrl.replace('http', 'ws')
    } else {
      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      wsUrl = `${proto}//${window.location.host}`
    }
    wsUrl += '/api/ws?token=' + encodeURIComponent(authStore.token)

    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      connected.value = true
    }

    ws.value.onclose = () => {
      connected.value = false
      setTimeout(connect, 3000)
    }

    ws.value.onmessage = (event) => {
      const message = JSON.parse(event.data)
      handleMessage(message)
    }

    ws.value.onerror = () => {
      connected.value = false
    }
  }

  function handleMessage(message) {
    const listStore = useListStore()

    switch (message.type) {
      case 'list_updated':
        listStore.fetchList()
        break
    }
  }

  async function replayQueue() {
    const actions = await getQueuedActions()
    for (const action of actions) {
      try {
        if (action.type === 'toggle_check') {
          await shoppingList.toggleCheck(action.itemId)
        }
        await removeFromQueue(action.id)
      } catch {
        break
      }
    }
  }

  function setupOfflineDetection() {
    window.addEventListener('online', () => {
      offline.value = false
      if (!connected.value) {
        connect()
      }
      replayQueue()
    })

    window.addEventListener('offline', () => {
      offline.value = true
    })
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
    }
  }

  return { ws, connected, offline, connect, disconnect, setupOfflineDetection }
})
