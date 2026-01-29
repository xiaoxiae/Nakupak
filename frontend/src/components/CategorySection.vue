<script setup>
defineProps({
  category: Object,
  count: Number,
})
</script>

<template>
  <div class="mb-6">
    <div class="flex items-center gap-2 mb-3 pl-1">
      <h3
        class="text-sm font-semibold uppercase tracking-wide"
        :style="category ? { color: category.color } : { color: 'var(--text-muted)' }"
      >
        {{ category?.name || 'Uncategorized' }}
      </h3>
      <span v-if="count != null" class="text-xs text-text-muted">({{ count }})</span>
    </div>
    <slot></slot>
  </div>
</template>
