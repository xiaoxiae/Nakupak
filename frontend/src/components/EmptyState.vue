<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: null,
  },
})
</script>

<template>
  <div class="text-center py-12 text-text-muted">
    <p>{{ title }}</p>
    <p v-if="subtitle" class="text-sm mt-1">{{ subtitle }}</p>
  </div>
</template>
