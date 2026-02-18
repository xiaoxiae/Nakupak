<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import { useToastStore } from '../stores/toast'
import { getUnit } from '../utils/units'
import { normalizeForSearch } from '../utils/sort'
import { Trash2 } from 'lucide-vue-next'
import { Motion, AnimatePresence } from 'motion-v'
import PageLayout from '../components/PageLayout.vue'
import ItemCard from '../components/ItemCard.vue'
import EmptyState from '../components/EmptyState.vue'
import ItemSearchPicker from '../components/ItemSearchPicker.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import AppButton from '../components/AppButton.vue'

const { t } = useI18n()
const listStore = useListStore()
const toastStore = useToastStore()

const showClearConfirm = ref(false)
const searchPicker = ref(null)

const searchTerm = computed(() => searchPicker.value?.search || '')

const matchingItemIds = computed(() => {
  const term = normalizeForSearch(searchTerm.value.trim())
  if (!term) return null
  return new Set(
    listStore.listItems
      .filter(li => normalizeForSearch(li.item?.name || '').includes(term))
      .map(li => li.id)
  )
})

function isListItemMatching(listItemId) {
  return !matchingItemIds.value || matchingItemIds.value.has(listItemId)
}

const sortedUncheckedGroups = computed(() => {
  const groups = listStore.uncheckedGroupedByCategory
  const term = normalizeForSearch(searchTerm.value.trim())
  if (!term) return groups
  return groups.map(g => ({
    ...g,
    items: [
      ...g.items.filter(i => normalizeForSearch(i.item?.name || '').includes(term)),
      ...g.items.filter(i => !normalizeForSearch(i.item?.name || '').includes(term)),
    ]
  }))
})

const flatList = computed(() => {
  const result = []
  for (const group of sortedUncheckedGroups.value) {
    result.push({
      type: 'category-header',
      key: `cat-${group.category?.id || 'uncategorized'}`,
      category: group.category,
      count: group.items.length,
    })
    for (const li of group.items) {
      result.push({
        type: 'item',
        key: li.id,
        listItem: li,
        dimmed: !isListItemMatching(li.id),
        checked: false,
      })
    }
  }
  if (listStore.checkedItems.length > 0) {
    result.push({
      type: 'purchased-header',
      key: 'purchased-header',
      count: listStore.checkedItems.length,
    })
    for (const li of listStore.checkedItems) {
      result.push({
        type: 'item',
        key: li.id,
        listItem: li,
        dimmed: false,
        checked: true,
      })
    }
  }
  return result
})

onMounted(async () => {
  await Promise.all([
    listStore.fetchList(),
    listStore.fetchItems(),
    listStore.fetchCategories(),
    listStore.fetchRecipes(),
    listStore.fetchPool(),
  ])
})

async function handleIncrement(listItem) {
  const step = getUnit(listItem.unit || 'x').step
  await listStore.updateQuantity(listItem.id, listItem.quantity + step)
}

async function handleDecrement(listItem) {
  const u = getUnit(listItem.unit || 'x')
  const newQty = listItem.quantity - u.step
  if (newQty < u.step) {
    await listStore.removeItem(listItem.id)
  } else {
    await listStore.updateQuantity(listItem.id, newQty)
  }
}

async function handleUpdateQuantity(listItem, newQty) {
  if (newQty <= 0) {
    await listStore.removeItem(listItem.id)
  } else {
    await listStore.updateQuantity(listItem.id, newQty)
  }
}

async function handleChangeUnit(listItem, newUnit) {
  await listStore.updateQuantity(listItem.id, listItem.quantity, newUnit)
}

async function handlePurchase() {
  const count = await listStore.purchaseChecked()
  if (count > 0) {
    toastStore.show(t('mainList.purchasedMessage', { count }))
  }
}

async function addToList(item) {
  await listStore.addItem(item.id)
}

async function handleClearList() {
  await listStore.clearList()
  showClearConfirm.value = false
}

function getRecipeColor(listItem) {
  if (!listItem.from_recipe_id) return null
  const recipe = listStore.recipes.find(p => p.id === listItem.from_recipe_id)
  return recipe?.color
}
</script>

<template>
  <PageLayout :title="t('mainList.title')">
    <ItemSearchPicker
      ref="searchPicker"
      :placeholder="t('mainList.searchPlaceholder')"
      @select="addToList"
      @create="addToList"
    />

    <!-- Current Shopping List -->
    <div class="relative">
      <AnimatePresence :initial="false">
      <Motion
        v-if="listStore.listItems.length > 0"
        key="list-header"
        :initial="{ opacity: 0 }"
        :animate="{ opacity: 1 }"
        :exit="{ opacity: 0 }"
        :transition="{ duration: 0.2 }"
        class="flex items-center justify-between mb-3"
      >
        <h3 class="text-sm font-semibold text-text-secondary">
          {{ t('mainList.yourList', { count: listStore.listItems.length }) }}
        </h3>
        <button
          class="p-1 text-text-muted hover:text-danger transition-colors"
          @click="showClearConfirm = true"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </Motion>
      </AnimatePresence>
      <TransitionGroup name="list-item" tag="div" class="relative">
        <div v-for="entry in flatList" :key="entry.key">
          <!-- Category header -->
          <div v-if="entry.type === 'category-header'" class="flex items-center gap-2 mb-3 mt-6 first:mt-0 pl-1">
            <h3 class="text-sm font-semibold uppercase tracking-wide"
                :style="entry.category ? { color: entry.category.color } : { color: 'var(--text-muted)' }">
              {{ entry.category?.name || t('common.uncategorized') }}
            </h3>
            <span class="text-xs text-text-muted">({{ entry.count }})</span>
          </div>
          <!-- Purchased header -->
          <div v-else-if="entry.type === 'purchased-header'" class="flex items-center gap-2 mb-3 mt-6 pl-1">
            <h3 class="text-sm font-semibold uppercase tracking-wide text-text-muted">
              {{ t('mainList.purchased') }}
            </h3>
            <span class="text-xs text-text-muted">({{ entry.count }})</span>
          </div>
          <!-- Item card -->
          <div v-else
            class="transition-opacity duration-200"
            :class="{ 'opacity-40': entry.dimmed, 'opacity-60': entry.checked }"
          >
            <ItemCard
              :item="entry.listItem.item"
              :quantity="entry.listItem.quantity"
              :unit="entry.listItem.unit || 'x'"
              :recipe-color="getRecipeColor(entry.listItem)"
              :checked="entry.checked"
              @increment="handleIncrement(entry.listItem)"
              @decrement="handleDecrement(entry.listItem)"
              @change-unit="(unit) => handleChangeUnit(entry.listItem, unit)"
              @update-quantity="(qty) => handleUpdateQuantity(entry.listItem, qty)"
              @remove="listStore.removeItem(entry.listItem.id)"
              @toggle-check="listStore.toggleCheck(entry.listItem.id)"
            />
          </div>
        </div>
      </TransitionGroup>
      <AnimatePresence :initial="false">
      <Motion
        v-if="listStore.listItems.length === 0"
        key="empty-state"
        :initial="{ opacity: 0 }"
        :animate="{ opacity: 1 }"
        :exit="{ opacity: 0 }"
        :transition="{ duration: 0.2 }"
        class="absolute inset-x-0 top-0"
      >
        <EmptyState :title="t('mainList.emptyTitle')" :subtitle="t('mainList.emptySubtitle')" />
      </Motion>
      </AnimatePresence>
    </div>

    <ConfirmModal
      :show="showClearConfirm"
      :title="t('mainList.clearList')"
      :message="t('mainList.clearListMessage')"
      :confirm-text="t('mainList.clearList')"
      :confirm-danger="true"
      @close="showClearConfirm = false"
      @confirm="handleClearList"
    />

    <template #fab>
      <AnimatePresence :initial="false">
        <Motion
          v-if="listStore.checkedCount > 0"
          key="purchased"
          :initial="{ opacity: 0, scale: 0.9 }"
          :animate="{ opacity: 1, scale: 1 }"
          :exit="{ opacity: 0, scale: 0.9 }"
          :transition="{ duration: 0.2 }"
        >
          <AppButton variant="success" fab @click="handlePurchase">
            {{ t('mainList.purchased') }}
          </AppButton>
        </Motion>
      </AnimatePresence>
    </template>
  </PageLayout>
</template>

<style scoped>
.list-item-move,
.list-item-enter-active,
.list-item-leave-active {
  transition: all 0.3s ease;
}
.list-item-enter-from,
.list-item-leave-to {
  opacity: 0;
}
.list-item-leave-active {
  position: absolute;
  width: 100%;
}
</style>
