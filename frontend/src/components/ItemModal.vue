<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import { Pencil } from 'lucide-vue-next'
import BaseModal from './BaseModal.vue'
import AppButton from './AppButton.vue'
import IconButton from './IconButton.vue'
import CategoryManagerModal from './CategoryManagerModal.vue'

const { t } = useI18n()

const props = defineProps({
  show: Boolean,
  item: Object
})

const emit = defineEmits(['close', 'save'])

const listStore = useListStore()

const itemName = ref('')
const categoryId = ref(null)
const showCategoryManager = ref(false)

watch(() => props.show, (newVal) => {
  if (newVal && props.item) {
    itemName.value = props.item.name
    categoryId.value = props.item.category_id
  }
})

function closeCategoryManager() {
  showCategoryManager.value = false
  // Reset categoryId if selected category was deleted
  if (categoryId.value && !listStore.categories.find(c => c.id === categoryId.value)) {
    categoryId.value = null
  }
}

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
      <div class="flex items-center gap-2">
        <select
          v-model="categoryId"
          class="flex-1 px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary"
        >
          <option :value="null">{{ t('common.noCategory') }}</option>
          <option v-for="cat in listStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
        <IconButton @click="showCategoryManager = true">
          <Pencil class="w-4 h-4" />
        </IconButton>
      </div>
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="close">
        {{ t('common.cancel') }}
      </AppButton>
      <AppButton @click="save" :disabled="!itemName.trim()">
        {{ t('common.save') }}
      </AppButton>
    </template>

    <CategoryManagerModal
      :show="showCategoryManager"
      @close="closeCategoryManager"
    />
  </BaseModal>
</template>
