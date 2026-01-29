<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { QrCode } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { useSyncStore } from '../stores/sync'
import QrScanModal from '../components/QrScanModal.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const syncStore = useSyncStore()

const shareToken = ref('')
const error = ref('')
const loading = ref(false)
const showScanModal = ref(false)

function extractToken(text) {
  try {
    const url = new URL(text)
    const token = url.searchParams.get('token')
    if (token) return token
  } catch {
    // not a URL, use as-is
  }
  return text
}

function onScanned(text) {
  showScanModal.value = false
  shareToken.value = extractToken(text)
  joinList()
}

onMounted(() => {
  const token = route.query.token
  if (token) {
    shareToken.value = token
    joinList()
  }
})

function isValidToken(code) {
  const hex = code.replace(/[^0-9A-F]/gi, '').toUpperCase()
  if (hex.length !== 8) return false
  const sum = [...hex].reduce((s, c) => s + parseInt(c, 16), 0)
  return sum % 4 === 0
}

function onTokenInput(e) {
  // Strip to hex chars, auto-insert dash
  let raw = e.target.value.replace(/[^0-9A-Fa-f]/g, '').toUpperCase().slice(0, 8)
  if (raw.length > 4) raw = raw.slice(0, 4) + '-' + raw.slice(4)
  shareToken.value = raw

  if (isValidToken(raw)) {
    joinList()
  }
}

async function createList() {
  error.value = ''
  loading.value = true

  try {
    await authStore.createHousehold()
    syncStore.connect()
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || t('login.error')
  } finally {
    loading.value = false
  }
}

async function joinList() {
  if (loading.value) return
  error.value = ''
  loading.value = true

  try {
    await authStore.joinHousehold(shareToken.value.trim())
    syncStore.connect()
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || t('login.error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[100svh] flex items-center justify-center p-4">
    <div class="w-full max-w-xs text-center">
      <h1 class="text-3xl font-bold text-primary mb-1">{{ t('login.title') }}</h1>
      <p class="text-text-muted mb-8">{{ t('login.tagline') }}</p>

      <div class="flex flex-col gap-4">
        <button
          class="w-full px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark disabled:bg-gray-300 disabled:cursor-not-allowed"
          :disabled="loading"
          @click="createList"
        >
          {{ loading ? t('login.loading') : t('login.create') }}
        </button>

        <div class="flex items-center gap-3 text-text-muted text-sm">
          <div class="flex-1 border-t border-border"></div>
          <span>{{ t('login.join') }}</span>
          <div class="flex-1 border-t border-border"></div>
        </div>

        <div class="flex items-center gap-2">
          <input
            :value="shareToken"
            @input="onTokenInput"
            type="text"
            :placeholder="t('login.placeholder')"
            :disabled="loading"
            class="flex-1 px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 text-center tracking-widest uppercase"
          />
          <button
            class="p-2.5 bg-surface border border-border rounded-lg text-text-muted hover:text-text-secondary"
            @click="showScanModal = true"
          >
            <QrCode class="w-5 h-5" />
          </button>
        </div>

        <p v-if="error" class="text-danger text-sm">{{ error }}</p>
      </div>

      <QrScanModal
        :show="showScanModal"
        @close="showScanModal = false"
        @scanned="onScanned"
      />
    </div>
  </div>
</template>
