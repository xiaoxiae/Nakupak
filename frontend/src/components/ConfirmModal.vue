<script setup>
import { useI18n } from 'vue-i18n'
import BaseModal from './BaseModal.vue'
import AppButton from './AppButton.vue'

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
      <AppButton variant="secondary" @click="close">
        {{ t('common.cancel') }}
      </AppButton>
      <AppButton :variant="confirmDanger ? 'danger' : 'primary'" @click="confirm">
        {{ confirmText }}
      </AppButton>
    </template>
  </BaseModal>
</template>
