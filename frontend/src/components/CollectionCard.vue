<script setup>
import { Motion, AnimatePresence } from 'motion-v'

defineProps({
  expanded: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <div class="bg-surface-secondary border border-border rounded-xl p-4">
    <div class="flex items-center justify-between">
      <slot name="header" />
      <div class="flex items-center gap-2">
        <slot name="actions" />
      </div>
    </div>
    <AnimatePresence :initial="false">
      <Motion
        v-if="expanded"
        :initial="{ opacity: 0, height: 0 }"
        :animate="{ opacity: 1, height: 'auto' }"
        :exit="{ opacity: 0, height: 0 }"
        :transition="{ duration: 0.2, ease: 'easeInOut' }"
        style="overflow: hidden"
      >
        <div class="flex flex-wrap gap-2 pt-3">
          <slot />
        </div>
      </Motion>
    </AnimatePresence>
  </div>
</template>
