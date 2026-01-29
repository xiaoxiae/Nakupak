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
      :initial="{ opacity: 0, height: 0, scale: 0.95, marginBottom: '0px' }"
      :animate="{ opacity: 1, height: 'auto', scale: 1, marginBottom: '0px' }"
      :exit="{ opacity: 0, height: 0, marginBottom: '0px' }"
      :transition="{ duration: 0.15, ease: 'easeOut' }"
      style="overflow: hidden"
    >
      <slot :item="item" />
    </Motion>
  </AnimatePresence>
</template>
