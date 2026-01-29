<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from './stores/auth'
import { useSyncStore } from './stores/sync'
import ToastContainer from './components/ToastContainer.vue'

const { t } = useI18n()
const authStore = useAuthStore()
const syncStore = useSyncStore()

onMounted(async () => {
  syncStore.setupOfflineDetection()
  if (authStore.isLoggedIn) {
    await authStore.fetchHousehold()
    syncStore.connect()
  }
})
</script>

<template>
  <div class="min-h-screen">
    <div v-if="syncStore.offline" class="bg-warning text-white text-center py-2 text-sm">
      {{ t('common.offline') }}
    </div>
    <router-view />
    <ToastContainer />
  </div>
</template>
