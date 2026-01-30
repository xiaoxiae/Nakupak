<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import { useSessionStore } from '../stores/session'
import { Trash2 } from 'lucide-vue-next'
import { Motion, AnimatePresence } from 'motion-v'
import PageLayout from '../components/PageLayout.vue'
import AnimatedCategoryList from '../components/AnimatedCategoryList.vue'
import ItemCard from '../components/ItemCard.vue'
import EmptyState from '../components/EmptyState.vue'
import ItemSearchPicker from '../components/ItemSearchPicker.vue'
import ConfirmModal from '../components/ConfirmModal.vue'

const { t } = useI18n()
const router = useRouter()
const listStore = useListStore()
const sessionStore = useSessionStore()

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
    sessionStore.fetchActive(),
  ])

  if (sessionStore.isActive) {
    router.push('/shopping')
  }

  hadItemsOnLoad.value = hadItemsOnLoad.value || listStore.listItems.length > 0

  // Skip fab enter animation on initial load
  requestAnimationFrame(() => { loaded.value = true })
})

async function handleIncrement(listItem) {
  await listStore.updateQuantity(listItem.id, listItem.quantity + 1)
}

async function handleDecrement(listItem) {
  await listStore.updateQuantity(listItem.id, listItem.quantity - 1)
}

async function startShopping() {
  await sessionStore.startSession()
  router.push('/shopping')
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
      <AnimatedCategoryList :groups="listStore.groupedByCategory" v-slot="{ item: listItem }">
            <ItemCard
              :item="listItem.item"
              :quantity="listItem.quantity"
              :recipe-color="getRecipeColor(listItem)"
              @increment="handleIncrement(listItem)"
              @decrement="handleDecrement(listItem)"
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
        v-if="!loaded && listStore.listItems.length > 0"
        class="px-4 py-3 bg-success text-white rounded-xl font-medium shadow-lg hover:opacity-90"
        @click="startShopping"
      >
        {{ t('mainList.startShopping') }}
      </button>
      <AnimatePresence v-if="loaded">
        <Motion
          v-if="listStore.listItems.length > 0"
          key="start-shopping"
          :initial="hadItemsOnLoad ? false : { opacity: 0, scale: 0.9 }"
          :animate="{ opacity: 1, scale: 1 }"
          :exit="{ opacity: 0, scale: 0.9 }"
          :transition="{ duration: 0.2 }"
        >
          <button
            class="px-4 py-3 bg-success text-white rounded-xl font-medium shadow-lg hover:opacity-90"
            @click="startShopping"
          >
            {{ t('mainList.startShopping') }}
          </button>
        </Motion>
      </AnimatePresence>
    </template>
  </PageLayout>
</template>
