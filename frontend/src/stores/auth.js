import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { auth } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const household = ref(null)
  const token = ref(localStorage.getItem('token'))

  const isLoggedIn = computed(() => !!token.value)

  async function createHousehold() {
    const response = await auth.create()
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    await fetchHousehold()
  }

  async function joinHousehold(shareToken) {
    const response = await auth.join(shareToken)
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    await fetchHousehold()
  }

  async function fetchHousehold() {
    if (!token.value) return
    try {
      const response = await auth.me()
      household.value = response.data
    } catch {
      logout()
    }
  }

  function logout() {
    household.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return { household, token, isLoggedIn, createHousehold, joinHousehold, fetchHousehold, logout }
})
