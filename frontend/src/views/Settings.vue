<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { Eye, EyeOff, Copy, QrCode } from 'lucide-vue-next'
import { useToastStore } from '../stores/toast'
import PageLayout from '../components/PageLayout.vue'
import QrDisplayModal from '../components/QrDisplayModal.vue'
import AppButton from '../components/AppButton.vue'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const toastStore = useToastStore()
const showToken = ref(false)
const showQrModal = ref(false)

async function copyToken() {
  if (authStore.household?.token) {
    await navigator.clipboard.writeText(authStore.household.token)
    toastStore.show(t('settings.copiedToClipboard'))
  }
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <PageLayout :title="t('settings.title')">
    <section class="mb-8">
      <h2 class="text-base font-semibold text-text-secondary mb-4">{{ t('settings.householdCode') }}</h2>
      <div class="bg-surface-secondary border border-border rounded-xl p-4">
        <p class="text-sm text-text-muted mb-3">{{ t('settings.shareDescription') }}</p>
        <div class="flex items-center gap-2">
          <div class="flex-1 px-4 py-2.5 bg-surface border border-border rounded-lg font-mono text-center tracking-widest text-lg">
            <span v-if="showToken">{{ authStore.household?.token }}</span>
            <span v-else class="text-text-muted">{{ t('settings.maskedToken') }}</span>
          </div>
          <button
            class="p-2.5 bg-surface border border-border rounded-lg text-text-muted hover:text-text-secondary"
            @click="showToken = !showToken"
          >
            <EyeOff v-if="showToken" class="w-5 h-5" />
            <Eye v-else class="w-5 h-5" />
          </button>
          <button
            class="p-2.5 bg-surface border border-border rounded-lg text-text-muted hover:text-text-secondary"
            @click="copyToken"
          >
            <Copy class="w-5 h-5" />
          </button>
          <button
            class="p-2.5 bg-surface border border-border rounded-lg text-text-muted hover:text-text-secondary"
            @click="showQrModal = true"
          >
            <QrCode class="w-5 h-5" />
          </button>
        </div>
        <AppButton variant="danger" block class="mt-4" @click="logout">
          {{ t('settings.signOut') }}
        </AppButton>
      </div>
    </section>

    <QrDisplayModal
      :show="showQrModal"
      @close="showQrModal = false"
    />
  </PageLayout>
</template>
