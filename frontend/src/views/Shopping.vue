<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSessionStore } from '../stores/session'
import { useListStore } from '../stores/list'
import { useToastStore } from '../stores/toast'
import { useSyncStore } from '../stores/sync'
import { X, Check } from 'lucide-vue-next'
import { Motion, AnimatePresence } from 'motion-v'
import PageLayout from '../components/PageLayout.vue'
import EmptyState from '../components/EmptyState.vue'
import IconButton from '../components/IconButton.vue'

const { t } = useI18n()
const router = useRouter()
const sessionStore = useSessionStore()
const listStore = useListStore()
const toastStore = useToastStore()
const syncStore = useSyncStore()

onMounted(async () => {
  try {
    await listStore.fetchCategories()
    await sessionStore.fetchActive()
  } catch {
    // Offline — fall through to use cached session data
  }

  if (!sessionStore.isActive) {
    router.push('/')
  }
})

async function toggleItem(item) {
  await sessionStore.toggleCheck(item.id)
}

async function completeShopping() {
  const checked = sessionStore.checkedCount
  const total = sessionStore.totalCount
  await sessionStore.completeSession()
  await listStore.fetchList()
  router.push('/')
  toastStore.show(t('shopping.completed', { checked, total }))
}

async function cancelShopping() {
  await sessionStore.abortSession()
  await listStore.fetchList()
  router.push('/')
  toastStore.show(t('shopping.cancelled'))
}

function getCategoryName(item) {
  if (!item.item?.category_id) return null
  const category = listStore.categories.find(c => c.id === item.item.category_id)
  return category?.name
}

function getCategoryColor(item) {
  if (!item.item?.category_id) return null
  const category = listStore.categories.find(c => c.id === item.item.category_id)
  return category?.color
}
</script>

<template>
  <PageLayout :title="t('shopping.title')" :show-nav="false">
    <template #left>
      <IconButton @click="cancelShopping" :disabled="syncStore.offline" :class="{ 'opacity-50': syncStore.offline }">
        <X class="w-6 h-6" />
      </IconButton>
    </template>

    <template #actions>
      <span class="font-semibold text-text-muted">{{ sessionStore.checkedCount }}/{{ sessionStore.totalCount }}</span>
    </template>

    <EmptyState v-if="sessionStore.loading" :title="t('shopping.loading')" />
    <EmptyState v-else-if="sessionStore.sortedItems.length === 0" :title="t('shopping.empty')" />

    <div v-else class="pb-20">
      <AnimatePresence :initial="false">
        <Motion
          v-for="item in sessionStore.sortedItems"
          :key="item.id"
          :initial="{ opacity: 0, y: -10 }"
          :animate="{ opacity: item.checked ? 0.6 : 1, y: 0 }"
          :exit="{ opacity: 0, x: -100 }"
          :transition="{ duration: 0.2, ease: 'easeOut' }"
          class="flex items-center gap-4 p-4 bg-surface border border-border rounded-lg mb-2 cursor-pointer active:scale-[0.98]"
          :class="{ 'bg-surface-secondary': item.checked }"
          @click="toggleItem(item)"
        >
          <div
            class="w-6 h-6 border-2 border-border rounded-full flex items-center justify-center shrink-0"
            :class="item.checked ? 'bg-success border-success text-white' : ''"
          >
            <Check v-if="item.checked" class="w-4 h-4" />
          </div>
          <div class="flex-1 min-w-0">
            <span
              class="block font-medium text-text"
              :class="{ 'line-through text-text-muted': item.checked }"
            >
              {{ item.item?.name }}
            </span>
            <span v-if="getCategoryName(item)" class="text-xs" :style="{ color: getCategoryColor(item) }">
              {{ getCategoryName(item) }}
            </span>
          </div>
          <span class="font-semibold text-text-muted">x{{ item.quantity }}</span>
        </Motion>
      </AnimatePresence>
    </div>

    <div class="fixed bottom-0 left-0 right-0 max-w-app mx-auto p-4 bg-surface border-t border-border">
      <button
        class="w-full py-3 bg-success text-white rounded-lg font-medium hover:opacity-90"
        :disabled="syncStore.offline"
        :class="{ 'opacity-50': syncStore.offline }"
        @click="completeShopping"
      >
        {{ t('shopping.complete') }}
      </button>
    </div>
  </PageLayout>
</template>
