<script setup>
import { Motion, AnimatePresence } from 'motion-v'

defineProps({
  items: {
    type: Array,
    required: true,
  },
  keyField: {
    type: String,
    default: 'id',
  },
})
</script>

<template>
  <AnimatePresence :initial="false">
    <Motion
      v-for="item in items"
      :key="item[keyField]"
      :initial="{ opacity: 0 }"
      :animate="{ opacity: 1 }"
      :exit="{ opacity: 0 }"
      :transition="{ duration: 0.15, ease: 'easeOut' }"
    >
      <slot :item="item" />
    </Motion>
  </AnimatePresence>
</template>