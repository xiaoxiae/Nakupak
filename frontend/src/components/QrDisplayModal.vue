<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import QrcodeVue from 'qrcode.vue'
import BaseModal from './BaseModal.vue'

const { t } = useI18n()
const authStore = useAuthStore()

const qrUrl = computed(() => {
  const token = authStore.household?.token || ''
  return `${window.location.origin}/login?token=${encodeURIComponent(token)}`
})

defineProps({
  show: Boolean
})

defineEmits(['close'])
</script>

<template>
  <BaseModal :show="show" :title="t('settings.qrCode')" @close="$emit('close')">
    <div class="flex flex-col items-center gap-4">
      <div class="rounded-lg p-4" style="background: #ffffff">
        <QrcodeVue
          :value="qrUrl"
          :size="200"
          level="M"
          foreground="#000000"
          background="#ffffff"
        />
      </div>
      <span class="font-mono text-lg tracking-widest text-text-secondary">
        {{ authStore.household?.token }}
      </span>
    </div>
    <template #footer />
  </BaseModal>
</template>
