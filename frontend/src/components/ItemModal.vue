<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import BaseModal from './BaseModal.vue'

const { t } = useI18n()

const props = defineProps({
  show: Boolean,
  item: Object
})

const emit = defineEmits(['close', 'save'])

const listStore = useListStore()

const itemName = ref('')
const categoryId = ref(null)

watch(() => props.show, (newVal) => {
  if (newVal && props.item) {
    itemName.value = props.item.name
    categoryId.value = props.item.category_id
  }
})

function close() {
  emit('close')
}

function save() {
  if (!itemName.value.trim()) return
  emit('save', {
    name: itemName.value.trim(),
    category_id: categoryId.value
  })
}
</script>

<template>
  <BaseModal :show="show" :title="t('common.editItem')" @close="close">
    <div class="mb-4">
      <label class="block text-sm font-medium mb-2 text-text-secondary">{{ t('common.name') }}</label>
      <input
        v-model="itemName"
        type="text"
        :placeholder="t('common.itemNamePlaceholder')"
        class="w-full px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary"
      />
    </div>

    <div>
      <label class="block text-sm font-medium mb-2 text-text-secondary">{{ t('common.categoryLabel') }}</label>
      <select
        v-model="categoryId"
        class="w-full px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary"
      >
        <option :value="null">{{ t('common.noCategory') }}</option>
        <option v-for="cat in listStore.categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
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
        :disabled="!itemName.trim()"
      >
        {{ t('common.save') }}
      </button>
    </template>
  </BaseModal>
</template>
