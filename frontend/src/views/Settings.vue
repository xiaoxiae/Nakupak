<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { useListStore } from '../stores/list'
import { categories as categoriesApi } from '../services/api'
import { Pencil, Trash2, Eye, EyeOff, Copy, QrCode } from 'lucide-vue-next'
import { useToastStore } from '../stores/toast'
import PageLayout from '../components/PageLayout.vue'
import AnimatedList from '../components/AnimatedList.vue'
import CategoryModal from '../components/CategoryModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import QrDisplayModal from '../components/QrDisplayModal.vue'
import EmptyState from '../components/EmptyState.vue'
import IconButton from '../components/IconButton.vue'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const listStore = useListStore()

const showCategoryModal = ref(false)
const editingCategory = ref(null)

const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)

const toastStore = useToastStore()
const showToken = ref(false)
const showQrModal = ref(false)

onMounted(async () => {
  await listStore.fetchCategories()
})

function startCreateCategory() {
  editingCategory.value = null
  showCategoryModal.value = true
}

function startEditCategory(category) {
  editingCategory.value = category
  showCategoryModal.value = true
}

async function handleCategorySave(data) {
  if (editingCategory.value) {
    await categoriesApi.update(editingCategory.value.id, data)
  } else {
    await categoriesApi.create(data)
  }
  await listStore.fetchCategories()
  showCategoryModal.value = false
}

function confirmDeleteCategory(category) {
  deleteTarget.value = category
  showDeleteConfirm.value = true
}

async function handleDeleteConfirm() {
  await categoriesApi.delete(deleteTarget.value.id)
  await listStore.fetchCategories()
  showDeleteConfirm.value = false
  deleteTarget.value = null
}

async function copyToken() {
  if (authStore.household?.token) {
    await navigator.clipboard.writeText(authStore.household.token)
    toastStore.show(t('settings.copiedToClipboard'))
  }
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <PageLayout :title="t('settings.title')">
    <section class="mb-8">
      <h2 class="text-base font-semibold text-text-secondary mb-4">{{ t('settings.householdCode') }}</h2>
      <div class="bg-surface-secondary border border-border rounded-xl p-4">
        <p class="text-sm text-text-muted mb-3">{{ t('settings.shareDescription') }}</p>
        <div class="flex items-center gap-2">
          <div class="flex-1 px-4 py-2.5 bg-surface border border-border rounded-lg font-mono text-center tracking-widest text-lg">
            <span v-if="showToken">{{ authStore.household?.token }}</span>
            <span v-else class="text-text-muted">{{ t('settings.maskedToken') }}</span>
          </div>
          <button
            class="p-2.5 bg-surface border border-border rounded-lg text-text-muted hover:text-text-secondary"
            @click="showToken = !showToken"
          >
            <EyeOff v-if="showToken" class="w-5 h-5" />
            <Eye v-else class="w-5 h-5" />
          </button>
          <button
            class="p-2.5 bg-surface border border-border rounded-lg text-text-muted hover:text-text-secondary"
            @click="copyToken"
          >
            <Copy class="w-5 h-5" />
          </button>
          <button
            class="p-2.5 bg-surface border border-border rounded-lg text-text-muted hover:text-text-secondary"
            @click="showQrModal = true"
          >
            <QrCode class="w-5 h-5" />
          </button>
        </div>
        <button
          class="w-full mt-4 py-3 bg-danger text-white rounded-lg font-medium hover:opacity-90"
          @click="logout"
        >
          {{ t('settings.signOut') }}
        </button>
      </div>
    </section>

    <section class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-base font-semibold text-text-secondary">{{ t('settings.categories') }}</h2>
        <button
          class="px-3 py-1.5 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-dark"
          @click="startCreateCategory"
        >
          {{ t('settings.addCategory') }}
        </button>
      </div>

      <AnimatedList :items="listStore.categories" v-slot="{ item: category }">
        <div class="flex items-center gap-3 px-4 py-3 bg-surface-secondary border border-border rounded-xl mb-3">
          <div class="w-4 h-4 rounded-full" :style="{ background: category.color }"></div>
          <span class="flex-1 font-medium text-text">{{ category.name }}</span>
          <IconButton @click="startEditCategory(category)">
            <Pencil class="w-4 h-4" />
          </IconButton>
          <IconButton @click="confirmDeleteCategory(category)">
            <Trash2 class="w-4 h-4" />
          </IconButton>
        </div>
      </AnimatedList>

      <EmptyState v-if="listStore.categories.length === 0" :title="t('settings.emptyCategoriesTitle')" :subtitle="t('settings.emptyCategoriesSubtitle')" />
    </section>

    <CategoryModal
      :show="showCategoryModal"
      :category="editingCategory"
      @close="showCategoryModal = false"
      @save="handleCategorySave"
    />

    <QrDisplayModal
      :show="showQrModal"
      @close="showQrModal = false"
    />

    <ConfirmModal
      :show="showDeleteConfirm"
      :title="t('settings.deleteCategory')"
      :message="t('settings.deleteCategoryMessage', { name: deleteTarget?.name })"
      :confirm-text="t('common.delete')"
      :confirm-danger="true"
      @close="showDeleteConfirm = false"
      @confirm="handleDeleteConfirm"
    />
  </PageLayout>
</template>
