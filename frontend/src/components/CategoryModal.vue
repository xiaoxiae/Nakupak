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

function randomColor() {
  return '#' + Math.floor(Math.random() * 0xffffff).toString(16).padStart(6, '0')
}

const categoryName = ref('')
const categoryColor = ref(randomColor())

const title = computed(() => props.category ? t('common.editCategory') : t('common.newCategory'))
const buttonText = computed(() => props.category ? t('common.save') : t('common.create'))

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.category) {
      categoryName.value = props.category.name
      categoryColor.value = props.category.color
    } else {
      categoryName.value = ''
      categoryColor.value = randomColor()
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
      <div class="flex gap-2 items-center">
        <input
          v-model="categoryName"
          type="text"
          :placeholder="t('common.categoryNamePlaceholder')"
          class="flex-1 px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary"
        />
        <input
          v-model="categoryColor"
          type="color"
          class="w-9 h-9 rounded-full border border-border p-0 cursor-pointer bg-transparent [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full [&::-webkit-color-swatch]:border-0 [&::-moz-color-swatch]:rounded-full [&::-moz-color-swatch]:border-0"
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
