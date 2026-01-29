<script setup>
import { Motion, AnimatePresence } from 'motion-v'
import CategorySection from './CategorySection.vue'
import AnimatedList from './AnimatedList.vue'

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
      :initial="{ opacity: 0, height: 0 }"
      :animate="{ opacity: 1, height: 'auto' }"
      :exit="{ opacity: 0, height: 0 }"
      :transition="{ duration: 0.25, ease: 'easeOut' }"
    >
      <CategorySection
        :category="group.category"
        :count="group.items.length"
      >
        <AnimatedList :items="group.items" v-slot="{ item }">
          <slot :item="item" :group="group" />
        </AnimatedList>
      </CategorySection>
    </Motion>
  </AnimatePresence>
</template>
