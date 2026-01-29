<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseModal from './BaseModal.vue'

const { t } = useI18n()

const props = defineProps({
  show: Boolean,
  category: Object
})

const emit = defineEmits(['close', 'save'])

const categoryName = ref('')
const categoryColor = ref('#6b7280')

const colors = ['#6b7280', '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899']

const title = computed(() => props.category ? t('common.editCategory') : t('common.newCategory'))
const buttonText = computed(() => props.category ? t('common.save') : t('common.create'))

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.category) {
      categoryName.value = props.category.name
      categoryColor.value = props.category.color
    } else {
      categoryName.value = ''
      categoryColor.value = '#6b7280'
    }
  }
})

function close() {
  emit('close')
}

function save() {
  if (!categoryName.value.trim()) return
  emit('save', {
    name: categoryName.value.trim(),
    color: categoryColor.value
  })
}
</script>

<template>
  <BaseModal :show="show" :title="title" @close="close">
    <div class="mb-4">
      <label class="block text-sm font-medium mb-2 text-text-secondary">{{ t('common.name') }}</label>
      <input
        v-model="categoryName"
        type="text"
        :placeholder="t('common.categoryNamePlaceholder')"
        class="w-full px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary"
      />
    </div>

    <div>
      <label class="block text-sm font-medium mb-2 text-text-secondary">{{ t('common.color') }}</label>
      <div class="flex gap-2">
        <button
          v-for="color in colors"
          :key="color"
          class="w-8 h-8 rounded-full border-2 p-0"
          :class="categoryColor === color ? 'border-gray-900 dark:border-white' : 'border-transparent'"
          :style="{ background: color }"
          @click="categoryColor = color"
        />
      </div>
    </div>

    <template #footer>
      <button
        class="px-6 py-3 bg-surface-secondary text-text-secondary rounded-lg font-medium hover:opacity-80"
        @click="close"
      >
        {{ t('common.cancel') }}
      </button>
      <button
        class="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed"
        @click="save"
        :disabled="!categoryName.trim()"
      >
        {{ buttonText }}
      </button>
    </template>
  </BaseModal>
</template>
