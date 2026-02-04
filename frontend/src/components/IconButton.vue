<script setup>
defineProps({
  small: {
    type: Boolean,
    default: false,
  },
  tiny: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <button
    class="bg-transparent text-text-muted rounded-full flex items-center justify-center hover:bg-surface hover:text-text-secondary"
    :class="tiny ? 'p-0 leading-none' : small ? 'p-1.5' : 'p-2 w-10 h-10'"
  >
    <slot />
  </button>
</template>
