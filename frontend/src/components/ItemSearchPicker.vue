<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import { Plus } from 'lucide-vue-next'
import { Motion, AnimatePresence } from 'motion-v'
import SearchBar from './SearchBar.vue'
import ItemBadge from './ItemBadge.vue'

const { t } = useI18n()
const listStore = useListStore()

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Search...',
  },
})

const emit = defineEmits(['select', 'create'])

const search = ref('')

const filteredItems = computed(() => {
  const term = search.value.toLowerCase().trim()
  if (!term) return listStore.poolItems

  return listStore.items
    .filter(item => item.name.toLowerCase().includes(term))
    .map(item => ({ item, score: 0, frequency: 0 }))
})

const exactMatch = computed(() => {
  const term = search.value.toLowerCase().trim()
  if (!term) return true
  return listStore.items.some(item => item.name.toLowerCase() === term)
})

async function handleEnter() {
  if (filteredItems.value.length > 0) {
    handleSelect(filteredItems.value[0].item)
  } else if (search.value.trim()) {
    await createAndEmit()
  }
}

function handleSelect(item) {
  emit('select', item)
  search.value = ''
}

async function createAndEmit() {
  if (!search.value.trim()) return
  const item = await listStore.createItem(search.value.trim(), null)
  await listStore.fetchItems()
  emit('create', item)
  search.value = ''
}
</script>

<template>
  <SearchBar v-model="search" :placeholder="placeholder" @enter="handleEnter" />

  <AnimatePresence :initial="false">
    <Motion
      v-if="filteredItems.length > 0 || search"
      key="search-section"
      :initial="{ opacity: 0, height: 0 }"
      :animate="{ opacity: 1, height: 'auto' }"
      :exit="{ opacity: 0, height: 0 }"
      :transition="{ duration: 0.2, ease: 'easeOut' }"
      class="mb-6 overflow-hidden"
    >
      <div class="flex items-center justify-between mb-3">
        <h3 v-if="!search" class="text-sm font-semibold text-text-secondary">{{ t('mainList.frequentlyBought') }}</h3>
        <h3 v-else class="text-sm font-semibold text-text-secondary">{{ t('mainList.searchResults') }}</h3>
      </div>

      <div class="flex gap-2 overflow-x-auto no-scrollbar">
        <ItemBadge
          v-for="poolItem in filteredItems"
          :key="poolItem.item.id"
          :name="poolItem.item.name"
          :count="poolItem.frequency"
          count-style="parentheses"
          clickable
          @click="handleSelect(poolItem.item)"
        />

        <ItemBadge
          v-if="search && !exactMatch"
          :name="search"
          clickable
          selected
          @click="createAndEmit"
        >
          <template #prefix>
            <Plus class="w-4 h-4" />
          </template>
        </ItemBadge>
      </div>
    </Motion>
  </AnimatePresence>
</template>
