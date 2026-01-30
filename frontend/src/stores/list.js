import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { shoppingList, items as itemsApi, categories as categoriesApi, recipes as recipesApi, pool as poolApi, sessions as sessionsApi } from '../services/api'
import { nameCompare } from '../utils/sort'

export const useListStore = defineStore('list', () => {
  const listItems = ref([])
  const items = ref([])
  const categories = ref([])
  const recipes = ref([])
  const poolItems = ref([])
  const sessions = ref([])

  const groupedByCategory = computed(() => {
    const grouped = {}
    const uncategorized = []

    for (const listItem of listItems.value) {
      const categoryId = listItem.item?.category_id
      if (categoryId) {
        if (!grouped[categoryId]) {
          const category = categories.value.find(c => c.id === categoryId)
          grouped[categoryId] = {
            category,
            items: []
          }
        }
        grouped[categoryId].items.push(listItem)
      } else {
        uncategorized.push(listItem)
      }
    }

    const sorted = Object.values(grouped).sort((a, b) =>
      nameCompare(a.category?.name || '', b.category?.name || '')
    )

    if (uncategorized.length > 0) {
      sorted.push({ category: null, items: uncategorized })
    }

    return sorted
  })

  const itemsGroupedByCategory = computed(() => {
    const grouped = {}
    const uncategorized = []

    for (const item of items.value) {
      const categoryId = item.category_id
      if (categoryId) {
        if (!grouped[categoryId]) {
          const category = categories.value.find(c => c.id === categoryId)
          grouped[categoryId] = {
            category,
            items: []
          }
        }
        grouped[categoryId].items.push(item)
      } else {
        uncategorized.push(item)
      }
    }

    const sorted = Object.values(grouped).sort((a, b) =>
      nameCompare(a.category?.name || '', b.category?.name || '')
    )

    if (uncategorized.length > 0) {
      sorted.push({ category: null, items: uncategorized })
    }

    return sorted
  })

  async function fetchList() {
    const response = await shoppingList.get()
    listItems.value = response.data
  }

  async function fetchItems() {
    const response = await itemsApi.list()
    items.value = response.data
  }

  async function fetchCategories() {
    const response = await categoriesApi.list()
    categories.value = response.data
  }

  async function fetchRecipes() {
    const response = await recipesApi.list()
    recipes.value = response.data
  }

  async function fetchPool() {
    const response = await poolApi.get()
    poolItems.value = response.data
  }

  async function fetchSessions() {
    const response = await sessionsApi.list()
    sessions.value = response.data
  }

  async function deleteSession(sessionId) {
    await sessionsApi.delete(sessionId)
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
  }

  async function addItem(itemId, quantity = 1) {
    const existing = listItems.value.find(i => i.item_id === itemId)
    if (existing) {
      existing.quantity += quantity
    }

    const response = await shoppingList.add([{ item_id: itemId, quantity }])

    if (existing) {
      const updated = response.data.find(i => i.item_id === itemId)
      if (updated) existing.quantity = updated.quantity
    } else {
      const added = response.data.find(i => i.item_id === itemId)
      if (added) listItems.value.push(added)
    }
  }

  async function updateQuantity(listItemId, quantity) {
    if (quantity <= 0) {
      await removeItem(listItemId)
    } else {
      // Optimistically update local state
      const item = listItems.value.find(i => i.id === listItemId)
      if (item) item.quantity = quantity

      await shoppingList.update(listItemId, quantity)
    }
  }

  async function removeItem(listItemId) {
    // Optimistically remove
    listItems.value = listItems.value.filter(i => i.id !== listItemId)

    await shoppingList.remove(listItemId)
  }

  async function addRecipe(recipeId) {
    await shoppingList.addRecipe(recipeId)
    await fetchList()
  }

  async function addItems(itemsToAdd) {
    await shoppingList.add(itemsToAdd)
    await fetchList()
  }

  async function createItem(name, categoryId = null) {
    const response = await itemsApi.create({ name, category_id: categoryId })
    items.value.push(response.data)
    return response.data
  }

  async function deleteItem(id) {
    await itemsApi.delete(id)
    items.value = items.value.filter(i => i.id !== id)
  }

  async function updateItem(id, data) {
    const response = await itemsApi.update(id, data)
    const index = items.value.findIndex(i => i.id === id)
    if (index >= 0) {
      items.value[index] = response.data
    }
    return response.data
  }

  async function bulkRemoveItems(ids) {
    listItems.value = listItems.value.filter(i => !ids.includes(i.id))
    await shoppingList.bulkRemove(ids)
  }

  async function clearList() {
    listItems.value = []
    await shoppingList.clear()
  }

  async function bulkDeleteItems(ids) {
    await itemsApi.bulkDelete(ids)
    items.value = items.value.filter(i => !ids.includes(i.id))
  }

  async function bulkSetCategory(ids, categoryId) {
    await itemsApi.bulkSetCategory(ids, categoryId)
    for (const item of items.value) {
      if (ids.includes(item.id)) {
        item.category_id = categoryId
        item.category = categoryId ? categories.value.find(c => c.id === categoryId) : null
      }
    }
  }

  async function mergeItems(targetId, sourceIds) {
    const response = await itemsApi.merge(targetId, sourceIds)
    items.value = items.value.filter(i => !sourceIds.includes(i.id) || i.id === targetId)
    const index = items.value.findIndex(i => i.id === targetId)
    if (index >= 0) {
      items.value[index] = response.data
    }
    return response.data
  }

  return {
    listItems,
    items,
    categories,
    recipes,
    poolItems,
    sessions,
    groupedByCategory,
    itemsGroupedByCategory,
    fetchList,
    fetchItems,
    fetchCategories,
    fetchRecipes,
    fetchPool,
    fetchSessions,
    deleteSession,
    addItem,
    updateQuantity,
    removeItem,
    addRecipe,
    addItems,
    createItem,
    deleteItem,
    updateItem,
    bulkRemoveItems,
    clearList,
    bulkDeleteItems,
    bulkSetCategory,
    mergeItems,
  }
})
