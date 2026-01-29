<script setup>
import { useI18n } from 'vue-i18n'
import BaseModal from './BaseModal.vue'

const { t } = useI18n()

const props = defineProps({
  show: Boolean,
  title: {
    type: String,
    default: 'Confirm'
  },
  message: {
    type: String,
    default: 'Are you sure?'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  confirmDanger: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'confirm'])

function close() {
  emit('close')
}

function confirm() {
  emit('confirm')
}
</script>

<template>
  <BaseModal :show="show" :title="title" @close="close">
    <p class="text-text-secondary">{{ message }}</p>

    <template #footer>
      <button
        class="px-6 py-3 bg-surface-secondary text-text-secondary rounded-lg font-medium hover:opacity-80"
        @click="close"
      >
        {{ t('common.cancel') }}
      </button>
      <button
        class="px-6 py-3 rounded-lg font-medium"
        :class="confirmDanger
          ? 'bg-danger text-white hover:opacity-90'
          : 'bg-primary text-white hover:bg-primary-dark'"
        @click="confirm"
      >
        {{ confirmText }}
      </button>
    </template>
  </BaseModal>
</template>
