<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import PageLayout from '../components/PageLayout.vue'
import AppButton from '../components/AppButton.vue'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

const inputClass = 'w-full px-4 py-2.5 bg-surface border border-border rounded-lg text-base text-text focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10'

const name = ref(authStore.household?.name ?? '')
const nameError = ref('')
const savingName = ref(false)

// The household may still be loading when the page opens
watch(() => authStore.household?.name, (value) => {
  if (value !== undefined) name.value = value
})

async function saveName() {
  const trimmed = name.value.trim()
  nameError.value = ''
  if (!trimmed || trimmed === authStore.household?.name) return
  savingName.value = true
  try {
    await authStore.updateHousehold({ name: trimmed })
    toastStore.show(t('settings.saved'))
  } catch (e) {
    nameError.value = e.response?.status === 409 ? t('login.nameTaken') : t('login.error')
  } finally {
    savingName.value = false
  }
}

const currentPassword = ref('')
const newPassword = ref('')
const passwordError = ref('')
const savingPassword = ref(false)

async function savePassword() {
  passwordError.value = ''
  if (!newPassword.value) return
  savingPassword.value = true
  try {
    await authStore.updateHousehold({
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    currentPassword.value = ''
    newPassword.value = ''
    toastStore.show(t('settings.saved'))
  } catch (e) {
    passwordError.value = e.response?.status === 403 ? t('settings.wrongPassword') : t('login.error')
  } finally {
    savingPassword.value = false
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
      <h2 class="text-base font-semibold text-text-secondary mb-4">{{ t('settings.household') }}</h2>
      <div class="bg-surface-secondary border border-border rounded-xl p-4 flex flex-col gap-6">
        <form class="flex flex-col gap-2" @submit.prevent="saveName">
          <label class="text-sm text-text-muted" for="household-name">{{ t('settings.householdName') }}</label>
          <div class="flex items-center gap-2">
            <input id="household-name" v-model="name" type="text" autocomplete="username" :class="inputClass" />
            <AppButton
              type="submit"
              :disabled="savingName || !name.trim() || name.trim() === authStore.household?.name"
            >
              {{ t('common.save') }}
            </AppButton>
          </div>
          <p v-if="nameError" class="text-danger text-sm">{{ nameError }}</p>
        </form>

        <form class="flex flex-col gap-2" @submit.prevent="savePassword">
          <span class="text-sm text-text-muted">{{ t('settings.changePassword') }}</span>
          <input
            v-model="currentPassword"
            type="password"
            autocomplete="current-password"
            :placeholder="t('settings.currentPassword')"
            :class="inputClass"
          />
          <input
            v-model="newPassword"
            type="password"
            autocomplete="new-password"
            :placeholder="t('settings.newPassword')"
            :class="inputClass"
          />
          <AppButton type="submit" block :disabled="savingPassword || !newPassword">
            {{ t('settings.changePassword') }}
          </AppButton>
          <p v-if="passwordError" class="text-danger text-sm">{{ passwordError }}</p>
        </form>

        <AppButton variant="danger" block @click="logout">
          {{ t('settings.signOut') }}
        </AppButton>
      </div>
    </section>
  </PageLayout>
</template>
