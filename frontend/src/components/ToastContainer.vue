<script setup>
import { useToastStore } from '../stores/toast'
import { Motion, AnimatePresence } from 'motion-v'
import { Info } from 'lucide-vue-next'
import ItemBadge from './ItemBadge.vue'

const toastStore = useToastStore()
</script>

<template>
  <div class="fixed top-2 left-1/2 -translate-x-1/2 z-[60] grid justify-items-center pointer-events-none max-w-[90vw]">
    <AnimatePresence>
      <Motion
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        :initial="{ opacity: 0, y: -20, scale: 0.95 }"
        :animate="{ opacity: 1, y: 0, scale: 1 }"
        :exit="{ opacity: 0, y: 20, scale: 0.95 }"
        :transition="{ duration: 0.15 }"
        class="col-start-1 row-start-1 flex flex-col gap-2 px-4 py-3 bg-surface/95 backdrop-blur-sm border border-border rounded-xl shadow-lg pointer-events-auto"
      >
        <div class="flex items-center gap-2">
          <Info class="w-4 h-4 shrink-0 text-text-muted" />
          <span class="text-sm font-medium text-text">{{ toast.message }}</span>
          <span
            v-if="toast.category"
            class="px-2 py-0.5 rounded text-xs tracking-wide uppercase"
            :style="{ backgroundColor: toast.category.color + '20', color: toast.category.color }"
          >
            {{ toast.category.name }}
          </span>
        </div>
        <div v-if="toast.items.length > 0" class="flex flex-wrap gap-1.5">
          <ItemBadge
            v-for="item in toast.items"
            :key="item.name"
            :name="item.name"
            :count="item.quantity"
          />
        </div>
      </Motion>
    </AnimatePresence>
  </div>
</template>
