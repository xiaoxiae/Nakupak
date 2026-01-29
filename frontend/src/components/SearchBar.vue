<script setup>
import { Search } from 'lucide-vue-next'

const model = defineModel({ type: String, default: '' })

defineProps({
  placeholder: {
    type: String,
    default: 'Search...',
  },
})

const emit = defineEmits(['enter'])
</script>

<template>
  <div class="relative mb-4">
    <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
    <input
      v-model="model"
      type="text"
      :placeholder="placeholder"
      class="w-full pl-10 pr-4 py-3 border border-border rounded-xl text-base bg-surface-secondary text-text placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
      @keydown.enter="emit('enter')"
    />
  </div>
</template>
