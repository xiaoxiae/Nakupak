<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { recipes as recipesApi } from '../services/api'
import BaseModal from './BaseModal.vue'
import AppButton from './AppButton.vue'
import { Loader2 } from 'lucide-vue-next'

const { t } = useI18n()

defineProps({
  show: Boolean,
})

const emit = defineEmits(['close', 'imported'])

const mode = ref('url')
const url = ref('')
const text = ref('')
const loading = ref(false)
const error = ref('')

function reset() {
  url.value = ''
  text.value = ''
  error.value = ''
  loading.value = false
  mode.value = 'url'
}

function close() {
  reset()
  emit('close')
}

async function submit() {
  error.value = ''
  loading.value = true

  const payload = mode.value === 'url' ? { url: url.value } : { text: text.value }

  try {
    const { data } = await recipesApi.import(payload)
    emit('imported', data)
    reset()
  } catch (e) {
    const status = e.response?.status
    if (status === 503) {
      error.value = t('import.workerOffline')
    } else if (status === 504) {
      error.value = t('import.workerTimeout')
    } else {
      error.value = e.response?.data?.detail || t('import.error')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <BaseModal :show="show" :title="t('import.title')" @close="close">
    <div class="mb-4">
      <div class="flex gap-2 mb-3">
        <AppButton
          :variant="mode === 'url' ? 'primary' : 'secondary'"
          size="sm"
          @click="mode = 'url'"
        >
          {{ t('import.fromUrl') }}
        </AppButton>
        <AppButton
          :variant="mode === 'text' ? 'primary' : 'secondary'"
          size="sm"
          @click="mode = 'text'"
        >
          {{ t('import.fromText') }}
        </AppButton>
      </div>

      <input
        v-if="mode === 'url'"
        v-model="url"
        type="url"
        :placeholder="t('import.urlPlaceholder')"
        class="w-full px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary"
      />
      <textarea
        v-else
        v-model="text"
        :placeholder="t('import.textPlaceholder')"
        rows="8"
        class="w-full px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary resize-y"
      />
    </div>

    <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
      {{ error }}
    </div>

    <div v-if="loading" class="flex items-center justify-center gap-2 py-4 text-text-secondary">
      <Loader2 class="w-5 h-5 animate-spin" />
      <span>{{ t('import.processing') }}</span>
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="close">
        {{ t('common.cancel') }}
      </AppButton>
      <AppButton @click="submit" :disabled="loading || (mode === 'url' ? !url : !text)">
        {{ t('import.submit') }}
      </AppButton>
    </template>
  </BaseModal>
</template>
