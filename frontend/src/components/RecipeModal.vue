<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import { getUnit } from '../utils/units'
import BaseModal from './BaseModal.vue'
import ItemCardList from './ItemCardList.vue'
import ItemSearchPicker from './ItemSearchPicker.vue'

const { t } = useI18n()

const props = defineProps({
  show: Boolean,
  editRecipe: Object,
  preselectedItemIds: Array,
})

const emit = defineEmits(['close', 'save'])

const listStore = useListStore()

function randomColor() {
  return '#' + Math.floor(Math.random() * 0xffffff).toString(16).padStart(6, '0')
}

const recipeName = ref('')
const recipeColor = ref(randomColor())
const selectedItems = ref([])

const title = computed(() => props.editRecipe ? t('common.editRecipe') : t('common.newRecipe'))
const buttonText = computed(() => props.editRecipe ? t('common.save') : t('common.create'))

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.editRecipe) {
      recipeName.value = props.editRecipe.name
      recipeColor.value = props.editRecipe.color
      selectedItems.value = props.editRecipe.recipe_items.map(pi => ({
        item_id: pi.item_id,
        quantity: pi.quantity,
        unit: pi.unit || 'x',
      }))
    } else if (props.preselectedItemIds?.length) {
      recipeName.value = ''
      recipeColor.value = randomColor()
      selectedItems.value = props.preselectedItemIds.map(id => ({ item_id: id, quantity: 1, unit: 'x' }))
    } else {
      recipeName.value = ''
      recipeColor.value = randomColor()
      selectedItems.value = []
    }
  }
})

function addItem(item) {
  if (!selectedItems.value.some(i => i.item_id === item.id)) {
    selectedItems.value.push({ item_id: item.id, quantity: 1, unit: 'x' })
  }
}

function getItem(itemId) {
  return listStore.items.find(i => i.id === itemId)
}

function handleIncrement(si) {
  const step = getUnit(si.unit || 'x').step
  si.quantity += step
}

function handleDecrement(si) {
  const u = getUnit(si.unit || 'x')
  const newQty = si.quantity - u.step
  if (newQty < u.step) {
    const index = selectedItems.value.indexOf(si)
    if (index >= 0) selectedItems.value.splice(index, 1)
  } else {
    si.quantity = newQty
  }
}

function handleUpdateQuantity(si, newQty) {
  if (newQty <= 0) {
    const index = selectedItems.value.indexOf(si)
    if (index >= 0) selectedItems.value.splice(index, 1)
  } else {
    si.quantity = newQty
  }
}

function handleRemoveItem(si) {
  const index = selectedItems.value.indexOf(si)
  if (index >= 0) selectedItems.value.splice(index, 1)
}

function handleChangeUnit(si, newUnit) {
  si.unit = newUnit
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
      <div class="flex gap-2 items-center">
        <input
          v-model="recipeName"
          type="text"
          :placeholder="t('common.recipeNamePlaceholder')"
          class="flex-1 px-4 py-3 border border-border rounded-lg text-base bg-surface text-text focus:outline-none focus:border-primary"
        />
        <input
          v-model="recipeColor"
          type="color"
          class="w-9 h-9 rounded-full border border-border p-0 cursor-pointer bg-transparent [&::-webkit-color-swatch-wrapper]:p-0 [&::-webkit-color-swatch]:rounded-full [&::-webkit-color-swatch]:border-0 [&::-moz-color-swatch]:rounded-full [&::-moz-color-swatch]:border-0"
        />
      </div>
    </div>

    <div class="mb-4">
      <label class="block text-sm font-medium mb-2 text-text-secondary">{{ t('common.itemsLabel') }}</label>
      <div v-if="selectedItems.length > 0" class="mb-3">
        <ItemCardList
          :items="selectedItems.map(si => ({
            id: si.item_id,
            item: getItem(si.item_id),
            quantity: si.quantity,
            unit: si.unit || 'x',
            _raw: si,
          }))"
          @increment="(entry) => handleIncrement(entry._raw)"
          @decrement="(entry) => handleDecrement(entry._raw)"
          @change-unit="(entry, unit) => handleChangeUnit(entry._raw, unit)"
          @update-quantity="(entry, qty) => handleUpdateQuantity(entry._raw, qty)"
          @remove="(entry) => handleRemoveItem(entry._raw)"
        />
      </div>
      <ItemSearchPicker
        :placeholder="t('common.searchItems')"
        @select="addItem"
        @create="addItem"
      />
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
