<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import BaseModal from './BaseModal.vue'
import ItemBadge from './ItemBadge.vue'

const { t } = useI18n()

const props = defineProps({
  show: Boolean,
  editRecipe: Object,
  preselectedItemIds: Array,
})

const emit = defineEmits(['close', 'save'])

const listStore = useListStore()

const recipeName = ref('')
const recipeColor = ref('#3b82f6')
const selectedItems = ref([])

const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4']

const title = computed(() => props.editRecipe ? t('common.editRecipe') : t('common.newRecipe'))
const buttonText = computed(() => props.editRecipe ? t('common.save') : t('common.create'))

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.editRecipe) {
      recipeName.value = props.editRecipe.name
      recipeColor.value = props.editRecipe.color
      selectedItems.value = props.editRecipe.recipe_items.map(pi => ({
        item_id: pi.item_id,
        quantity: pi.quantity
      }))
    } else if (props.preselectedItemIds?.length) {
      recipeName.value = ''
      recipeColor.value = '#3b82f6'
      selectedItems.value = props.preselectedItemIds.map(id => ({ item_id: id, quantity: 1 }))
    } else {
      recipeName.value = ''
      recipeColor.value = '#3b82f6'
      selectedItems.value = []
    }
  }
})

function toggleItem(itemId) {
  const index = selectedItems.value.findIndex(i => i.item_id === itemId)
  if (index >= 0) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push({ item_id: itemId, quantity: 1 })
  }
}

function isSelected(itemId) {
  return selectedItems.value.some(i => i.item_id === itemId)
}

function save() {
  emit('save', {
    id: props.editRecipe?.id,
    name: recipeName.value,
    color: recipeColor.value,
    items: selectedItems.value,
  })
}

function close() {
  emit('close')
}
</script>

<template>
  <BaseModal :show="show" :title="title" @close="close">
    <div class="mb-4">
      <label class="block text-sm font-medium mb-2 text-text-secondary">{{ t('common.name') }}</label>
      <input
        v-model="recipeName"
        type="text"
        :placeholder="t('common.recipeNamePlaceholder')"
        class="w-full px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary"
      />
    </div>

    <div class="mb-4">
      <label class="block text-sm font-medium mb-2 text-text-secondary">{{ t('common.color') }}</label>
      <div class="flex gap-2">
        <button
          v-for="color in colors"
          :key="color"
          class="w-8 h-8 rounded-full border-2 p-0"
          :class="recipeColor === color ? 'border-gray-900 dark:border-white' : 'border-transparent'"
          :style="{ background: color }"
          @click="recipeColor = color"
        />
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium mb-2 text-text-secondary">{{ t('common.itemsLabel') }}</label>
      <div class="flex flex-wrap gap-2">
        <ItemBadge
          v-for="item in listStore.items"
          :key="item.id"
          :name="item.name"
          :selected="isSelected(item.id)"
          clickable
          @click="toggleItem(item.id)"
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
        :disabled="!recipeName"
      >
        {{ buttonText }}
      </button>
    </template>
  </BaseModal>
</template>
