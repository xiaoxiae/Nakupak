<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useListStore } from '../stores/list'
import { useToastStore } from '../stores/toast'
import { recipes as recipesApi } from '../services/api'
import { Pencil, Trash2, Plus } from 'lucide-vue-next'
import { Motion } from 'motion-v'
import PageLayout from '../components/PageLayout.vue'
import AnimatedList from '../components/AnimatedList.vue'
import RecipeModal from '../components/RecipeModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import EmptyState from '../components/EmptyState.vue'
import ItemBadge from '../components/ItemBadge.vue'
import IconButton from '../components/IconButton.vue'

const { t } = useI18n()
const listStore = useListStore()
const toastStore = useToastStore()

const showModal = ref(false)
const editingRecipe = ref(null)

const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)

onMounted(async () => {
  await Promise.all([
    listStore.fetchRecipes(),
    listStore.fetchItems(),
  ])
})

function startCreate() {
  editingRecipe.value = null
  showModal.value = true
}

function startEdit(recipe) {
  editingRecipe.value = recipe
  showModal.value = true
}

async function handleSave(data) {
  if (data.id) {
    await recipesApi.update(data.id, {
      name: data.name,
      color: data.color,
      items: data.items,
    })
  } else {
    await recipesApi.create({
      name: data.name,
      color: data.color,
      items: data.items,
    })
  }
  await listStore.fetchRecipes()
  showModal.value = false
}

function confirmDeleteRecipe(recipe) {
  deleteTarget.value = recipe
  showDeleteConfirm.value = true
}

async function handleDeleteConfirm() {
  await recipesApi.delete(deleteTarget.value.id)
  await listStore.fetchRecipes()
  showDeleteConfirm.value = false
  deleteTarget.value = null
}

async function addRecipeToList(recipe) {
  await listStore.addRecipe(recipe.id)
  const items = recipe.recipe_items?.map(pi => ({
    name: pi.item?.name,
    quantity: pi.quantity,
  })) || []
  toastStore.show(t('recipes.added', { name: recipe.name }), { items })
}
</script>

<template>
  <PageLayout :title="t('recipes.title')">
    <EmptyState v-if="listStore.recipes.length === 0" :title="t('recipes.emptyTitle')" :subtitle="t('recipes.emptySubtitle')" />

    <AnimatedList :items="listStore.recipes" v-slot="{ item: recipe }">
      <div class="bg-surface-secondary border border-border rounded-xl p-4 mb-4">
        <div class="flex items-center gap-3">
          <div class="w-4 h-4 rounded-full" :style="{ background: recipe.color }"></div>
          <h3 class="flex-1 text-base font-medium text-text truncate">{{ recipe.name }}</h3>
          <div class="flex gap-1">
            <IconButton @click="addRecipeToList(recipe)">
              <Plus class="w-4 h-4" />
            </IconButton>
            <IconButton @click="startEdit(recipe)">
              <Pencil class="w-4 h-4" />
            </IconButton>
            <IconButton @click="confirmDeleteRecipe(recipe)">
              <Trash2 class="w-4 h-4" />
            </IconButton>
          </div>
        </div>
        <div class="flex flex-wrap gap-2 mt-3">
          <ItemBadge
            v-for="pi in recipe.recipe_items"
            :key="pi.item_id"
            :name="pi.item?.name"
            :count="pi.quantity"
          />
        </div>
      </div>
    </AnimatedList>

    <RecipeModal
      :show="showModal"
      :edit-recipe="editingRecipe"
      @close="showModal = false"
      @save="handleSave"
    />

    <ConfirmModal
      :show="showDeleteConfirm"
      :title="t('recipes.deleteRecipe')"
      :message="t('recipes.deleteRecipeMessage', { name: deleteTarget?.name })"
      :confirm-text="t('common.delete')"
      :confirm-danger="true"
      @close="showDeleteConfirm = false"
      @confirm="handleDeleteConfirm"
    />

    <template #fab>
      <button
        class="px-4 py-3 bg-primary text-white rounded-xl font-medium shadow-lg hover:bg-primary-dark"
        @click="startCreate"
      >
        {{ t('recipes.newRecipe') }}
      </button>
    </template>
  </PageLayout>
</template>
