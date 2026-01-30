<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import { useToastStore } from '../stores/toast'
import { getUnit } from '../utils/units'
import { Trash2 } from 'lucide-vue-next'
import { Motion, AnimatePresence } from 'motion-v'
import PageLayout from '../components/PageLayout.vue'
import AnimatedCategoryList from '../components/AnimatedCategoryList.vue'
import ItemCardList from '../components/ItemCardList.vue'
import EmptyState from '../components/EmptyState.vue'
import ItemSearchPicker from '../components/ItemSearchPicker.vue'
import ConfirmModal from '../components/ConfirmModal.vue'

const { t } = useI18n()
const listStore = useListStore()
const toastStore = useToastStore()

const loaded = ref(false)
const showClearConfirm = ref(false)
const hadItemsOnLoad = ref(listStore.listItems.length > 0)

onMounted(async () => {
  await Promise.all([
    listStore.fetchList(),
    listStore.fetchItems(),
    listStore.fetchCategories(),
    listStore.fetchRecipes(),
    listStore.fetchPool(),
  ])

  hadItemsOnLoad.value = hadItemsOnLoad.value || listStore.listItems.length > 0

  // Skip fab enter animation on initial load
  requestAnimationFrame(() => { loaded.value = true })
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
      <AnimatedCategoryList :groups="listStore.groupedByCategory" v-slot="{ group }">
            <ItemCardList
              :items="group.items.map(li => ({
                id: li.id,
                item: li.item,
                quantity: li.quantity,
                unit: li.unit || 'x',
                recipeColor: getRecipeColor(li),
                checked: !!li.checked,
                _raw: li,
              }))"
              @increment="(entry) => handleIncrement(entry._raw)"
              @decrement="(entry) => handleDecrement(entry._raw)"
              @change-unit="(entry, unit) => handleChangeUnit(entry._raw, unit)"
              @update-quantity="(entry, qty) => handleUpdateQuantity(entry._raw, qty)"
              @remove="(entry) => listStore.removeItem(entry._raw.id)"
              @toggle-check="(entry) => listStore.toggleCheck(entry._raw.id)"
            />
      </AnimatedCategoryList>
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
      <button
        v-if="!loaded && listStore.checkedCount > 0"
        class="px-4 py-3 bg-success text-white rounded-xl font-medium shadow-lg hover:opacity-90"
        @click="handlePurchase"
      >
        {{ t('mainList.purchased') }}
      </button>
      <AnimatePresence v-if="loaded">
        <Motion
          v-if="listStore.checkedCount > 0"
          key="purchased"
          :initial="{ opacity: 0, scale: 0.9 }"
          :animate="{ opacity: 1, scale: 1 }"
          :exit="{ opacity: 0, scale: 0.9 }"
          :transition="{ duration: 0.2 }"
        >
          <button
            class="px-4 py-3 bg-success text-white rounded-xl font-medium shadow-lg hover:opacity-90"
            @click="handlePurchase"
          >
            {{ t('mainList.purchased') }}
          </button>
        </Motion>
      </AnimatePresence>
    </template>
  </PageLayout>
</template>
