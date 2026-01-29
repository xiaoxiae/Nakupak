<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ShoppingCart, CookingPot, History, Settings, Apple } from 'lucide-vue-next'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

function navigate(path) {
  if (route.path !== path) {
    router.push(path)
  }
}
</script>

<template>
  <nav class="flex border-t border-border min-[601px]:border-x fixed bottom-0 left-0 right-0 bg-surface max-w-app mx-auto">
    <div
      class="flex-1 flex flex-col items-center py-3 text-xs cursor-pointer"
      :class="route.path === '/' ? 'text-primary bg-primary/10' : 'text-text-muted'"
      @pointerup="navigate('/')"
    >
      <ShoppingCart class="w-6 h-6 mb-1" />
      <span>{{ t('nav.list') }}</span>
    </div>

    <div
      class="flex-1 flex flex-col items-center py-3 text-xs cursor-pointer"
      :class="route.path === '/recipes' ? 'text-primary bg-primary/10' : 'text-text-muted'"
      @pointerup="navigate('/recipes')"
    >
      <CookingPot class="w-6 h-6 mb-1" />
      <span>{{ t('nav.recipes') }}</span>
    </div>

    <div
      class="flex-1 flex flex-col items-center py-3 text-xs cursor-pointer"
      :class="route.path === '/history' ? 'text-primary bg-primary/10' : 'text-text-muted'"
      @pointerup="navigate('/history')"
    >
      <History class="w-6 h-6 mb-1" />
      <span>{{ t('nav.history') }}</span>
    </div>

    <div
      class="flex-1 flex flex-col items-center py-3 text-xs cursor-pointer"
      :class="route.path === '/items' ? 'text-primary bg-primary/10' : 'text-text-muted'"
      @pointerup="navigate('/items')"
    >
      <Apple class="w-6 h-6 mb-1" />
      <span>{{ t('nav.items') }}</span>
    </div>

    <div
      class="flex-1 flex flex-col items-center py-3 text-xs cursor-pointer"
      :class="route.path === '/settings' ? 'text-primary bg-primary/10' : 'text-text-muted'"
      @pointerup="navigate('/settings')"
    >
      <Settings class="w-6 h-6 mb-1" />
      <span>{{ t('nav.settings') }}</span>
    </div>
  </nav>
</template>
