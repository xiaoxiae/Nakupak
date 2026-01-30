<script setup>
import { Motion, AnimatePresence } from 'motion-v'
import CategorySection from './CategorySection.vue'

defineProps({
  groups: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <AnimatePresence :initial="false">
    <Motion
      v-for="group in groups"
      :key="group.category?.id || 'uncategorized'"
      :initial="{ opacity: 0 }"
      :animate="{ opacity: 1 }"
      :exit="{ opacity: 0 }"
      :transition="{ duration: 0.25, ease: 'easeOut' }"
    >
      <CategorySection
        :category="group.category"
        :count="group.items.length"
      >
        <slot :group="group" />
      </CategorySection>
    </Motion>
  </AnimatePresence>
</template>
