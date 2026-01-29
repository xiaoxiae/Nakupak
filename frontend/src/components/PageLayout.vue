<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Sun, Moon } from 'lucide-vue-next'
import NavBar from './NavBar.vue'

defineProps({
  title: {
    type: String,
    required: true,
  },
  showNav: {
    type: Boolean,
    default: true,
  },
})

const { locale } = useI18n()

const isDark = ref(document.documentElement.classList.contains('dark'))

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  document.documentElement.classList.toggle('light', !isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

function toggleLanguage() {
  locale.value = locale.value === 'en' ? 'cs' : 'en'
  localStorage.setItem('language', locale.value)
}
</script>

<template>
  <div>
    <header class="flex items-center gap-4 px-4 h-16 border-b border-border sticky top-0 bg-surface z-50">
      <slot name="left" />
      <h1 class="flex-1 text-lg font-semibold text-text truncate">{{ title }}</h1>
      <slot name="actions" />
      <div class="flex items-center gap-1">
        <button class="p-2 text-text-muted hover:text-text-secondary text-lg w-8 text-center" @click="toggleLanguage">
          {{ locale === 'en' ? '🇬🇧' : '🇨🇿' }}
        </button>
        <button class="p-2 text-text-muted hover:text-text-secondary" @click="toggleTheme">
          <Sun v-if="isDark" class="w-5 h-5" />
          <Moon v-else class="w-5 h-5" />
        </button>
      </div>
    </header>

    <div class="p-4 pb-24">
      <slot />
    </div>

    <div class="fixed bottom-24 left-0 right-0 max-w-app mx-auto pr-6 flex justify-end pointer-events-none z-40">
      <div class="pointer-events-auto">
        <slot name="fab" />
      </div>
    </div>

    <NavBar v-if="showNav" />
  </div>
</template>
