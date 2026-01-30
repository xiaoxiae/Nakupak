<script setup>
import { Check } from 'lucide-vue-next'

defineProps({
  checked: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['toggle'])
</script>

<template>
  <button
    class="flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors"
    :class="checked
      ? 'bg-success border-success text-white'
      : 'border-border text-transparent hover:border-text-muted'"
    @click.stop="emit('toggle')"
  >
    <Check class="w-4 h-4" />
  </button>
</template>
